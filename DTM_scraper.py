import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import re
import json

covered_URLS=set()

class mySpider(scrapy.Spider):
    name = "mySpider"
    start_urls = ['https://www.mercedes-benz.com/en/']
    covered_URLS.add('https://www.mercedes-benz.com/en/')
    allowed_domains=['www.mercedes-benz.com']
    rules = [
        Rule(LinkExtractor(allow=['mercedes-benz.com/en/.+']), callback='parse', follow=True),
    ] 

    def parse(self, response):

        URL_SELECTOR = '::attr(href)'
        DTM_SELETOR = 'script[src^="//assets.adobedtm.com/"]'


        if response.css(DTM_SELETOR).extract_first():
            yield{
                'URL': response.url,
                'DTMheader': response.css(DTM_SELETOR).extract_first()
            }
        else:
            yield{
                'URL': response.request.url,
                'DTMheader': "none found"
            }

        for next_page in response.css('a ::attr(href)').extract():
            next_page=next_page.split("?")[0]
            if next_page and next_page.find("www.mercedes-benz.com/en/")>-1 and not(next_page in covered_URLS):
                covered_URLS.add(next_page)
                next_page = response.urljoin(next_page)
                yield scrapy.Request(url=next_page, callback=self.parse)