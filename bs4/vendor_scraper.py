#!/usr/bin/env python
# modified from https://github.com/thayton/architectfinder/blob/master/scraper_selenium.py

"""
Python script for scraping the results from https://www.ips.state.nc.us/vendor/SearchVendor.aspx
"""

import re
import string
from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

class VendorFinderScraper(object):
    def __init__(self):
        self.url = "https://www.ips.state.nc.us/vendor/SearchVendor.aspx"
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

    def next_state(self):
        """Click on new search"""
        self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnResetSearch').click()
        wait = WebDriverWait(self.driver, 10)
        # https://stackoverflow.com/questions/41530940/python-selenium-not-work-with-webdriverwait
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_pnlSearch")))
        select = Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlState'))
        return select


    def scrape(self):
        self.driver.get(self.url)
    
        # Select state selection dropdown
        select = Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_ddlState'))
        # option_indexes = range(1, len(select.options))
        option_indexes = range(1, 8)


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
                name = s.find('a', attrs={'id': 'ctl00_ContentPlaceHolder1_gvVendorList_ctl03_hlCompanyName'}).text
                print("firm name: ", name)
                print()
            
                # Pagination
                try:
                    # prop = self.driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvVendorList"]/tbody/tr[1]/td/table/tbody/tr/td[{}]'.format(pageno))
                    prop = self.driver.find_element_by_xpath("//a[text()='{}']".format(pageno))
                    
                    # next_page_elem = prop.find_element_by_xpath('.//a')
                    next_page_elem = prop
                    
                    # next_page_elem = self.driver.find_element_by_xpath("//a[text()='%d']" % pageno)
                except NoSuchElementException:
                    print("No more pages")
                    break

                next_page_elem.click()

                def next_page(driver):
                    '''
                    Wait until the next page background color changes indicating
                    that it is now the currently selected page
                    '''
                    # prop = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_gvVendorList"]/tbody/tr[1]/td/table/tbody/tr/td[{}]'.format(pageno))
                    try:
                        # prop.find_element_by_xpath('.//span')
                        self.driver.find_element_by_xpath("//a[text()='{}']".format(pageno))
                    except NoSuchElementException:
                        return False
                    return True


                
                wait = WebDriverWait(self.driver, 10)
                wait.until(next_page)

                pageno += 1

            # Reset search for next state
            select = self.next_state()

        self.driver.quit()


if __name__ == '__main__':
    scraper = VendorFinderScraper()
    scraper.scrape()
