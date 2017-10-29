#!/usr/bin/env python
# modified from https://github.com/thayton/architectfinder/blob/master/scraper_selenium.py

"""
Python script for scraping the results from https://www.ips.state.nc.us/vendor/SearchVendor.aspx
"""

import re
import string
import pandas as pd
from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

class VendorFinderScraper(object):
    def __init__(self, category='State'):
        self.url = "https://www.ips.state.nc.us/vendor/SearchVendor.aspx"
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.category = category
        self.search_id = self.get_search_id(category)

    def next_state(self):
        """Click on new search"""
        self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnResetSearch').click()
        wait = WebDriverWait(self.driver, 10)
        # https://stackoverflow.com/questions/41530940/python-selenium-not-work-with-webdriverwait
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_pnlSearch")))
        select = Select(self.driver.find_element_by_id(self.search_id))
        return select

    def get_search_id(self, category):
        id_dict = {
                'State': 'ctl00_ContentPlaceHolder1_ddlState',
                'Construction Codes': 'ctl00_ContentPlaceHolder1_lboxSicCodes',
                'Construction License': 'ctl00_ContentPlaceHolder1_ddlConstructionLicense'
                }
        return id_dict[category]

    def parse_page(self, soup):
        """Returns a dataframe which contains the information from the html
        table of a page."""
        table = soup.findAll('table', {'id': 'ctl00_ContentPlaceHolder1_gvVendorList'})[0]
        df = pd.read_html(table.prettify())[0]
        col_length = len(df.columns)
        if col_length > 7:
            df = df.drop(range(8, col_length), axis=1)
        # df = df.drop([8, 9], axis=1)
        df = df.drop(df.index[:3])
        df = df.drop(df.index[-2:])
        print(df.head())
        return df

    def contact_info_columns(self, df):
        fax = df['Contact Info'].str.extract(r'Fax:  (\(?\d{3}\D*\d{3}\D*\d{4})')
        fax.name = 'Fax'
        toll_free = df['Contact Info'].str.extract(r'TollFree:  (\(?\d{3,4}\D*\d{3}\D*\d{4})')
        toll_free.name = 'TollFree'
        contact_info = df['Contact Info'].str.extract(r'^Contact:  (?P<Name>.*)  Phone:  (?P<Phone>.*) x.*  Email:  (?P<Email>.*)$')
        combined = pd.concat([df, contact_info, fax, toll_free], axis=1) 
        return combined
        
    def final_dataframe(self, dataframes, columns):
        df = pd.concat(dataframes)
        df.columns = columns
        return df

    def scrape(self):
        dataframes = []
        self.driver.get(self.url)
    
        # Select state selection dropdown
        select = Select(self.driver.find_element_by_id(self.search_id))
        option_indexes = range(1, len(select.options))
        # option_indexes = range(1, 4)

        # Iterate through each state
        for index in option_indexes:
            select.select_by_index(index)
            self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnSearch').click()

            # Wait for the results to finish loading
            wait = WebDriverWait(self.driver, 10)
            # https://stackoverflow.com/questions/41530940/python-selenium-not-work-with-webdriverwait
            wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_pnlResults")))

            pageno = 2

            while True:
                s = BeautifulSoup(self.driver.page_source, "lxml")

                df = self.parse_page(s)
                if not df.empty:
                    dataframes.append(df)
            
                # Pagination
                try:
                    next_page_elem = self.driver.find_element_by_xpath(
                            '//a[@href="javascript:__doPostBack(\'ctl00$ContentPlaceHolder1$gvVendorList\',\'Page${}\')"]'.format(pageno))
                except NoSuchElementException:
                    print("No more pages")
                    break

                next_page_elem.click()

                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.element_to_be_clickable((By.XPATH,
                    '//a[@href="javascript:__doPostBack(\'ctl00$ContentPlaceHolder1$gvVendorList\',\'Page${}\')"]'.format(pageno-1))))

                pageno += 1

            # Reset search for next state
            select = self.next_state()
        columns = [item.text for item in s.findAll('th')]
        final_df = self.final_dataframe(dataframes, columns)
        final_df = self.contact_info_columns(final_df)
        final_df.to_csv('ins_scraped.csv', index=False)

        self.driver.quit()


if __name__ == '__main__':
    scraper = VendorFinderScraper('Construction Codes')
    scraper.scrape()
