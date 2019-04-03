import re
from jsystSpider.items import *
import json


class IntegrateSpider(scrapy.Spider):
    name = 'integrate'
    allowed_domains = ['jsyst.cn']
    start_urls = ['http://www.jsyst.cn/']

    def parse(self, response):
        '''
        解析地区
        :param response:
        :return:
        '''
        # areas = response.xpath('//dl[@class="kmlink0 cl"]/li/a') #谷歌浏览没问题 scrapy的xpath匹配不到
        areas = response.xpath('(//li/a)[position()<32]')
        for area in areas:
            url = area.xpath('./@href').extract_first()
            code = re.match('http://www.jsyst.cn/(\w+)/', url).group(1)
            name = area.xpath('./text()').extract_first()
            area = JsystspiderAreaItem(name=name, code=code)
            # 地区Item扔给调度器分配给piplelines处理保存
            yield area
            # 科目一
            yield scrapy.Request(url + 'km1/kt/', callback=self.parse_question, meta={
                'area': code,
                'km': 'km1'
            })  # C1\C2小车
            # # 科目四
            yield scrapy.Request(url + 'km4/kt/', callback=self.parse_question, meta={
                'area': code,
                'km': 'km4'
            })  # C1\C2小车
        # 大车不分地区
        # 科目一
        yield scrapy.Request('http://km1.jsyst.cn/a/kt/', callback=self.parse_question_ab)  # A1\B1\A3客车
        yield scrapy.Request('http://km1.jsyst.cn/b/kt/', callback=self.parse_question_ab)  # A2\B2货车
        # 科目四 不分AB
        yield scrapy.Request('http://km4.jsyst.cn/ab/kt/', callback=self.parse_question_ab)  # A1\B1\A3\A2\B2大车

    def parse_question(self, response):
        '''
        解析小车
        :param response:
        :return:
        '''
        area = response.meta['area']  # 区域
        km = response.meta['km']  # 科目
        questions_detail = re.findall('(http://km[14].jsyst.cn/fx/q(\d+)/)', response.text)
        for link, num in questions_detail:
            kmItem = JsystspiderKmItem(km=km, question_num=num, area_code=area, question_type='c')
            yield kmItem
            yield scrapy.Request(link, callback=self.parse_item)

    def parse_question_ab(self, response):
        '''
        解析大车
        :param response:
        :return:
        '''
        result = re.match(r'http://(\w+).jsyst.cn/(\w+)/kt/', response.url)
        km = result.group(1)  # 科目
        question_type = result.group(2)  # 类型

        if question_type == 'ab':
            questions_detail = re.findall(r"Array\('(\d+)\'", response.text)
            for num in questions_detail:
                kmItem = JsystspiderKmItem(km=km, question_num=num, area_code='', question_type=question_type)
                yield kmItem
                yield scrapy.Request('http://km4.jsyst.cn/fx/q' + num + '/', callback=self.parse_item)
        else:
            questions_detail = re.findall('(http://km[14].jsyst.cn/fx/q(\d+)/)', response.text)
            for link, num in questions_detail:
                kmItem = JsystspiderKmItem(km=km, question_num=num, area_code='', question_type=question_type)
                yield kmItem
                yield scrapy.Request(link, callback=self.parse_item)

    def parse_item(self, response):
        '''
        解析题目
        :param response:
        :return:
        '''

        result = re.match('http://(\w+).jsyst.cn/fx/q(\d+)/', response.url, re.S)
        km = result.group(1)  # 科目
        question_num = result.group(2)  # 题号

        ele = response.xpath('//div[@class="vehiclesIn3"]')[0]
        question = ele.xpath('./h1/text()').extract_first().split('、', 1)[1]
        img_url = ele.xpath('./div/img/@src').extract_first()
        p = ele.xpath('//div[@class="vehiclesIn3"]/p')
        options = p[1: -3].xpath('./text()').extract()
        answer = p[-4].xpath('./font/b/text()').extract_first()
        explanation = p[-3].xpath('./text()').extract_first().\
            replace("更多试题详细分析，请扫描下面的二维码，进入驾驶员试题网手机版查看，已更新至2018年最新题库：", "")
        questionItem = JsystspiderKmQuestionItem(km=km,
                                                 question_num=question_num,
                                                 question=question,
                                                 img_url=img_url,
                                                 answer=answer,
                                                 options=json.dumps(options, ensure_ascii=False),
                                                 explanation=explanation)

        yield questionItem

