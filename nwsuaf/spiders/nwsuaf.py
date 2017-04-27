#!/bin/python3
#-*-coding:utf-8-*-
""" nwsuaf spider first test to practise """

import os 
from pymongo import MongoClient
# os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'NWSUAF.settings')
from scrapy import crawler
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
from nwsuaf.items import NwsuafItem

class NwsuafSpider(CrawlSpider):
    """ This is spider """
    name = 'nwsuaf'
    
    # 暂时无法从settings中取到设置
    # mongo_uri = crawler.settings['MONGO_URI']
    # mongo_db = crawler.settings['MONGO_DATABASE']

    client = MongoClient('localhost:27017')
    db = client.search
    co = db.url
    firsturl = co.find_one()
    allowed_domains = [firsturl['url']]
    start_first_url = 'http://' + firsturl['url']
    start_urls = [start_first_url]
    print(firsturl['url'])

    # allowed_domains = ['www.nwsuaf.edu.cn']
    # start_urls = ['http://www.nwsuaf.edu.cn']
    # 此处要注意二者区别
    # allowed_domains = ['tao-blog.herokuapp.com']
    # start_urls = ['https://tao-blog.herokuapp.com/']

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
        soup = BeautifulSoup(response.body, 'lxml')
        item['content'] = soup.get_text(strip=True)
        print(item['title'])
        yield item


# def auto_crawl():
#     process = CrawlerProcess(get_project_settings())
#     process.crawl('nwsuaf')
#     process.start()
#     return True