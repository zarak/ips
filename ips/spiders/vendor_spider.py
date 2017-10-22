import scrapy
import pandas as pd

class VendorViewStateSpider(scrapy.Spider):
    name = "ips_data"
    start_urls = ['https://www.ips.state.nc.us/vendor/SearchVendor.aspx']
    download_delay = 1.5
    def __init__(self):
        self.page_num = 1

    def parse(self, response):
        yield scrapy.FormRequest.from_response(
                response=response,
                formdata={
                    'ctl00$ContentPlaceHolder1$ddlState': u'CO',
                    # '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first()
                },
                callback=self.next_page
        )

    def next_page(self, response):
        self.page_num += 1
        self.parse_page(response)
        yield scrapy.FormRequest.from_response(
                response=response,
                formdata={
                    # 'ctl00$ContentPlaceHolder1$ddlState': u'CO',
                    '__EVENTARGUMENT': 'Page${}'.format(self.page_num),
                    '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$gvVendorList',
                    '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first()
                },
                callback=self.next_page
        )


    def parse_page(self, response):
        # x = response.xpath('//*[@id="content"]')
        # tbody = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvVendorList"]/tbody').extract()
        y = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_gvVendorList_ctl03_hlCompanyName"]/text()').extract()
        yield y






# __EVENTTARGET:ctl00$ContentPlaceHolder1$gvVendorList
# __EVENTARGUMENT:Page$1
# __VIEWSTATE:5Mb3qSupd4EUyU
# __VIEWSTATEGENERATOR:670BE266
# __VIEWSTATEENCRYPTED:
# __EVENTVALIDATION:VtK92hlTRAdAom+Ts4+iHQ1JZf01Z+77b4QX1qC8BFmDNN3ipLFXl4LwcnMHEGCNqmC3TwRSA3OYjLa/aOFOMB5oDY07tBQO17L2kcfp+1THgPvF7hh0YB1629OL/xKvL0vYtcVRfJ1oBOTsssjf+x5bVy56s8+cPewCGIzSatQ3miyO6hb5RWARTfj0+FnrtUF0yPUr8uqTw6o+B++gZy6zUOucikhp3DuS4BYT240LlzGxDU50pGf8xeT1CIu8hTIP4/LzNJCIz2rQC2uTN0qdq1w=


# __EVENTTARGET:ctl00$ContentPlaceHolder1$gvVendorList
# __EVENTARGUMENT:Page$2
# __VIEWSTATE:e3psJtFzpVgq
# __VIEWSTATEGENERATOR:670BE266
# __VIEWSTATEENCRYPTED:
# __EVENTVALIDATION:JpkYynsreYN4urdwTlALKLMf5zuWPJhgXW0NEHq2wLpR/VhPe+3tObX+zs+0rbjppN6VT3tlWNMihMOB9fEVvetZfUPhj/KQ/hsmgOKiosPk5yUST12GI5CACJ2MPsvJWFinYmzruhpFkluGqb4tzMDHqAE7aqxvF8Aov3RhBS0V2zeGpllS/HM3UPJfenS6TnTOYuw5zaWyEmfTZYr7Em7N5WlHoPr7VdMukYplgDuTROsGm/OiRh2TcJHJzYuD10TE+ADPjcVjIk1H6V36C+dPKRg=
