# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

        
class JsystspiderAreaItem(scrapy.Item):
    #地名
    name = scrapy.Field()
    #地名编号
    code = scrapy.Field()

class JsystspiderKmItem(scrapy.Item):
    #科目
    km = scrapy.Field()
    #题号
    question_num = scrapy.Field()
    #地区号
    area_code = scrapy.Field()
    #问题类型
    question_type = scrapy.Field()

class JsystspiderKmQuestionItem(scrapy.Item):
    #科目
    km = scrapy.Field()
    #题号
    question_num = scrapy.Field()
    #问题
    question = scrapy.Field()
    #图像链接
    img_url = scrapy.Field()
    #问题
    answer = scrapy.Field()
    #选项
    options = scrapy.Field()
    #解释
    explanation = scrapy.Field()
