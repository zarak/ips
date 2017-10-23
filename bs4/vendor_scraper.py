#!/usr/bin/env python

"""
Python script for scraping the results from https://www.ips.state.nc.us/vendor/SearchVendor.aspx
"""

import re
import string
from urllib.parse import urlparse, urljoin

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

class VendorFinderScraper(object):
    def __init__(self):
        self.url = "https://www.ips.state.nc.us/vendor/SearchVendor.aspx"
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

    def scrape(self):
        self.driver.get(self.url)
    
        try:
            self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnAccept').click()
        except NoSuchElementException:
            pass

        # Select state selection dropdown
        select = Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_drpState'))
        option_indexes = range(1, len(select.options))

        # Iterate through each state
        for index in option_indexes:
            select.select_by_index(index)
            self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnSearch').click()

            # Wait for the results to finish loading
            wait = WebDriverWait(self.driver, 10)
            wait.until(lambda driver: driver.find_element_by_id('ctl00_ContentPlaceHolder1_uprogressSearchResults').is_displayed() == False)

            pageno = 2

            while True:
                s = BeautifulSoup(self.driver.page_source)
                r1 = re.compile(r'^frmFirmDetails\.aspx\?FirmID=([A-Z0-9-]+)$')
                r2 = re.compile(r'hpFirmName$')
                x = {'href': r1, 'id': r2}

                for a in s.findAll('a', attrs=x):
                    print("firm name: ", a.text)
                    print("firm url: ", urljoin(self.driver.current_url, a['href']))
                    print()
            
                # Pagination
                try:
                    next_page_elem = self.driver.find_element_by_xpath("//a[text()='%d']" % pageno)
                except NoSuchElementException:
                    break # No more pages

                next_page_elem.click()

                def next_page(driver):
                    '''
                    Wait until the next page background color changes indicating
                    that it is now the currently selected page
                    '''
                    style = driver.find_element_by_xpath("//a[text()='%d']" % pageno).get_attribute('style')
                    return 'background-color' in style
                
                wait = WebDriverWait(self.driver, 10)
                wait.until(next_page)

                pageno += 1

        self.driver.quit()


if __name__ == '__main__':
    scraper = ArchitectFinderScraper()
    scraper.scrape()
