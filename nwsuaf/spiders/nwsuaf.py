#!/bin/python3
#-*-coding:utf-8-*-
""" nwsuaf spider first test to practise """

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
from nwsuaf.items import NwsuafItem

class NusuafSpider(CrawlSpider):
    """ This is spider """
    name = 'nwsuaf'
    allowed_domains = ['www.nwsuaf.edu.cn']
    start_urls = ['http://www.nwsuaf.edu.cn']
    rules = [
        Rule(LinkExtractor(), callback='parse_response', follow=True),
    ]

    def parse_response(self, response):
        """ 由于crawlspider是由自身parse函数实现，所以此处命名重复则会覆盖出错 """
        # filename = response.url.split('http://')[-1].replace('.', '_') + '.html'
        # with open(filename, 'wb') as tempfile:
        #     tempfile.write(response.body)

        nafu = Selector(response)
        item = NwsuafItem()
        item['url'] = response.url
        item['title'] = nafu.xpath('/html/head/title/text()').extract()[0]
        soup = BeautifulSoup(response.body)
        item['content'] = soup.get_text(strip=True)
        print(item['item'])
        yield item
