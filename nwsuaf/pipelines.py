# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import pymongo
from scrapy.exceptions import DropItem

class NwsuafPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    collection_name = 'search'

    def __init__(self, mongo_uri, mongo_db):
        # connection = pymongo.Connection(
        #     settings['MONGODB_SERVER'],
        #     settings['MONGODB_PORT']
        # )
        # db = connection[settings['MONGODB_DB']]
        # self.collection = db[settings['MONGODB_COLLECTIO']]
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing{0}!".format(data))
        if valid:
            self.db[self.collection_name].insert(dict(item))
            # self.collection.insert(dict(item))
            logging.debug("data has add to MongoDB database")
        return item