# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JianshuScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uid = scrapy.Field()
    nickname = scrapy.Field()
    head_pic = scrapy.Field()
    gender = scrapy.Field()
    following_num = scrapy.Field()
    follower_num = scrapy.Field()
    articles_num = scrapy.Field()
    words_num = scrapy.Field()
    beliked_num = scrapy.Field()


class relationItem(scrapy.Item):
    uid = scrapy.Field()
    follower = scrapy.Field()
