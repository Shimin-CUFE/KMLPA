# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from twisted.enterprise import adbapi
import pymysql.cursors

from scrapy.crawler import Settings as settings
from .items import JianshuScrapyItem
from .items import relationItem


class JianshuScrapyPipeline(object):
    def __init__(self):
        dbargs = dict(
            host='localhost',
            db='jianshu_scrapy',
            user='root',
            passwd='root',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbargs)

    def process_item(self, item, spider):
#       if isinstance(item, JianshuScrapyItem):
#           res = self.dbpool.runInteraction(self.item_a_insert, item)
#            return item
        if isinstance(item, relationItem):
            res = self.dbpool.runInteraction(self.item_b_insert, item)
            return item

#    def item_a_insert(self, conn, item):
#        try:
#            sql = "insert into jianshu_user(uid,nickname,head_pic,gender,following_num,follower_num,articles_num,words_num,beliked_num) values('%s','%s','%s','%s',%d,%d,%d,%d,%d) ;" % (
#                item['uid'], item['nickname'], item['head_pic'], item['gender'], int(item['following_num']),
#                int(item['follower_num']), int(item['articles_num']), int(item['words_num']), int(item['beliked_num']))
#           conn.execute(sql)
#        except Exception as e:
#            print(e)

    def item_b_insert(self, conn, item):
        try:
            conn.execute('insert into jianshu_user_relation(uid,follower_uid) values (%s,%s)',
                         (item['uid'], item['follower']))
        except Exception as e:
            print(e)
