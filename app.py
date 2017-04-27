#!/bin/python3
#-*-coding:utf-8-*-

import os, json, re, scrapy
from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from whoosh.highlight import highlight, ContextFragmenter, Highlighter
from whoosh.searching import Hit
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy import log, signals
from scrapy.spiders import CrawlSpider
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from jieba.analyse import ChineseAnalyzer
from nwsuaf.spiders.nwsuaf import NwsuafSpider





app = Flask(__name__)
CORS(app)
# app.config['JSON_AS_ASCII'] = False

client = MongoClient('localhost:27017')
db = client.search
co = db.search
url_co = db.url
analyzer = ChineseAnalyzer()
# PAGE_SIZE = 5

class WhooshSarch(object):
    """
    Object utilising Whoosh to create a search index of all
    crawled rss feeds, parse queries and search the index for related mentions.
    """

    def __init__(self, collection):
        self.collection = collection
        self.indexdir = "indexdir"
        self.indexname = "indexname"
        self.schema = self.get_schema()
        if not os.path.exists(self.indexdir):
            os.mkdir(self.indexdir)
            create_in(self.indexdir, self.schema, indexname=self.indexname)
        self.ix = open_dir(self.indexdir, indexname=self.indexname)

    def get_schema(self):
        return Schema(title=TEXT(stored=True, analyzer=analyzer),
                      url=ID(unique=True, stored=True),
                      content=TEXT(stored=True, analyzer=analyzer))

    def rebuild_index(self):
        ix = create_in(self.indexdir, self.schema, indexname=self.indexname)
        writer = ix.writer()
        for coll in self.collection.find():
            writer.update_document(title=coll["title"], url=coll["url"],
                            content=coll["content"])
        writer.commit() 

    def commit(self, writer):
        """ commit data to index """
        writer.commit()
        return True

    def parse_query(self, query):
        parser = MultifieldParser(["url", "title", "content"], self.ix.schema)
        return parser.parse(query)
                    
    # def search(self, query, page):
    #     """ 考虑使用后端分页还是前段分页 """
    #     results = []
    #     with self.ix.searcher() as searcher:
    #         result_page = searcher.search_page(
    #             self.parse_query(query), page, pagelen=PAGE_SIZE)
    #         for result in result_page:
    #         # for result in searcher.search(self.parse_query(query)):
    #             results.append(dict(result))
    #     return {'results': results, 'total': result_page.total}

    def search(self, query):
        results = []
        fragments = []
        with self.ix.searcher() as searcher:
            result_origin = searcher.search(self.parse_query(query))
            # result_origin现在就是一个hit对象，可以直接对它使用highlights方法
            #TODO 将查询结果中'content'字段内容改为html格式的摘要

            my_cf = ContextFragmenter(maxchars=100, surround=30)
            hi = Highlighter(fragmenter=my_cf)
            for hit in result_origin:
                # hit['fragment'] = highlight(hit['content'], query, analyzer,
                #                             )
                # print(hit['fragment'])
                print(hit.highlights("content"))
                fragment={}
                fragment['fragment'] = hit.highlights("content")
                fragments.append(fragment)



            for result in result_origin:
                # my_cf = highlight.ContextFragmenter(maxchars=100, surround=30)
                #Fragment size 的maxchars默认200，surround默认20
                # dict(result)
                # re.sub("[\t\r\n ]+", " ", result['content'])
                # results.append(result)
                # result['fragment'] = hit.highlights("content")
                # 无法修改search result
                results.append(dict(result))
            for i in range(len(results)):
                results[i].update(fragments[i])
            # results = zip(*[(result.update(fragment)) for result, fragment 
            #                 in zip(results, fragments)])
            # for fragment in fragments for result in results:
            #     result.update(fragment)
        return results
            # result_len = len(result_origin)
            # for i in range(result_len):
            #     results.append(result_origin[i].fields)
            # keywords = [keyword for keyword, score in
            #     result_origin.key_terms("content", docs=10, numterms=5)]
            # print(keywords)

    def close(self):
        """
        Closes the searcher obj. Must be done manually.
        """
        self.ix.close()

url_co.insert({"url": "www.nwsuaf.edu.cn"})
# TODO 第一次的自动执行爬虫，执行完了再执行下面的代码
# TODO 执行上面的语句时要先清空数据库
# crawl_finished = False

# query_one = "关于举办新西兰林肯大学土壤学专家系列学术报告的通知"
# pageshow = nwsuaf.search(query_one)
# print(pageshow)
# nwsuaf.close()

def auto_crawl():
    # TODO运行爬虫前需要将数据库中的search集合清空，url集合不可以清空
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(NwsuafSpider)
    # reactor如果在此处stop后，后面的爬虫将不能运行
    # d.addBoth(lambda _: reactor.stop())
    reactor.run() # the script will block here until the crawling is finished
    nwsuaf.rebuild_index()

nwsuaf = WhooshSarch(co)
auto_crawl()


@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/url-get', methods=['GET'])
def url_get():
    #find_one用来获取匹配的文档，当只有一个或只要第一个时很有用
    urlstr = url_co.find_one()
    #返回的字典不能直接jsonify，也不能直接用字典。
    return jsonify({'posturl': urlstr['url']}), 200

@app.route('/url-post', methods=['GET', 'POST'])
def url_post():
    if not request.json or not 'posturl' in request.json:
        abort(400)
    # update语句需要用$进行操作，加上$set即可,最后一个参数为true表示找不到就创建一个
    # url_co.find_one_and_update({},{'posturl': request.json['posturl']})
    url_co.find_one_and_update({},{'$set': {'url': request.json['posturl']}}, upsert=False)
    urlstr = url_co.find_one()
    auto_crawl()
    return urlstr['url']
    
# @app.route('/messages', methods=['POST'])
# def test():
#     if request.headers['Content-Type'] == 'text/plain':
#         return "Text Message: " + request.data

#     elif request.headers['Content-Type'] == 'application/json':
#         return "JSON Message: " + json.dumps(request.json)

#     else:
#         return "415 Unsupported Media Type ;)"

@app.route('/results', methods=['GET', 'POST'])
def get_results():
    if not request.json or not 'keywords' in request.json:
        abort(400)
    query_keywords = request.json['keywords']
    pageshow = nwsuaf.search(query_keywords)
    # 此处猜想，search的应该是已经建立好的index而非数据库
    print(query_keywords)
    print(pageshow)
    # TODO 此处添加完成搜索后的返回消息
    return jsonify({'results': pageshow}), 201

# @app.route('/keywords', method=['POST'])
# def post_keywords():
#     query_keywords = resquest.json['keywords']
#     pageshow = nwsuaf.search(query_keywords)
#     print(pageshow)
#     # TODO 此处添加完成搜索后的返回消息
#     return 200




if __name__ == "__main__":
    app.run(debug=True)
  