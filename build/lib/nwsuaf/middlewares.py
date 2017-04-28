# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
from scrapy import signals


class NwsuafSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class proxMiddleware(object):
    #proxy_list=[{'http': 'http://123.157.146.116:8123'}, {'http': 'http://116.55.16.233:8998'}, {'http': 'http://115.85.233.94:80'}, {'http': 'http://180.76.154.5:8888'}, {'http': 'http://139.213.135.81:80'}, {'http': 'http://124.88.67.14:80'}, {'http': 'http://106.46.136.90:808'}, {'http': 'http://106.46.136.226:808'}, {'http': 'http://124.88.67.21:843'}, {'http': 'http://113.245.84.253:8118'}, {'http': 'http://124.88.67.10:80'}, {'http': 'http://171.38.141.12:8123'}, {'http': 'http://124.88.67.52:843'}, {'http': 'http://106.46.136.237:808'}, {'http': 'http://106.46.136.105:808'}, {'http': 'http://106.46.136.190:808'}, {'http': 'http://106.46.136.186:808'}, {'http': 'http://101.81.120.58:8118'}, {'http': 'http://106.46.136.250:808'}, {'http': 'http://106.46.136.8:808'}, {'http': 'http://111.78.188.157:8998'}, {'http': 'http://106.46.136.139:808'}, {'http': 'http://101.53.101.172:9999'}, {'http': 'http://27.159.125.68:8118'}, {'http': 'http://183.32.88.133:808'}, {'http': 'http://171.38.37.193:8123'}]
    proxy_list=[
    "http://180.76.154.5:8888",
    "http://14.109.107.1:8998",
    "http://106.46.136.159:808",
    "http://175.155.24.107:808",
    "http://124.88.67.10:80",
    "http://124.88.67.14:80",
    "http://58.23.122.79:8118",
    "http://123.157.146.116:8123",
    "http://124.88.67.21:843",
    "http://106.46.136.226:808",
    "http://101.81.120.58:8118",
    "http://180.175.145.148:808"]
    def process_request(self,request,spider):
        # if not request.meta['proxies']:
        ip = random.choice(self.proxy_list)
        print(ip)
        #print 'ip=' %ip
        request.meta['proxy'] = ip