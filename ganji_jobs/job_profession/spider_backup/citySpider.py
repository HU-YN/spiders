# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from job_profession.items import JobProfessionItem

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')


def zhprint(obj):
    import re
    print re.sub(r"\\u([a-f0-9]{4})", lambda mg: unichr(int(mg.group(1), 16)), obj.__repr__())


class CityspiderSpider(scrapy.Spider):
    name = "citySpider"
    allowed_domains = ["ganji.com"]

    #city list
    #http://www.ganji.com/index.htm
    
    #zhaopin page
    #http://anshan.ganji.com/zhaopin/
    
    #job_profession_en page
    #http://anshan.ganji.com/zpdianhuaxiaoshou/
    
    
    def __init__(self, city_en='cd', city=u'成都', *args, **kwargs):
        super(CityspiderSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://%s.ganji.com/zhaopin/' % city_en]
        self.city = u'深圳'
        self.city_en = city_en
        zhprint(city)
        zhprint(city_en)
        

    def parse(self, response):
        filename = self.city_en + ".html"
        #filename = response.url.split("/")[-2]
        #with open(filename, 'wb') as f:
        #    f.write(response.body)

        xp = '//*[@id="wrapper"]/div[5]/div[2]/dl'
        for s in response.xpath(xp):
            city = self.city
            city_en = self.city_en
            job_industry = s.xpath('.//dt/a/text()').extract()[0]
            job_industry_en = s.xpath('.//dt/a/@href').extract()[0]
            for i in s.xpath('.//dd/i'):
                #l = ItemLoader(item=JobProfessionItem(), response=response)
                #l.add_xpath('city', city)
                #l.add_xpath('city_en', city_en)
                #l.add_xpath('job_industry', job_industry)
                #l.add_xpath('job_industry_en', job_industry_en)
                #l.add_xpath('job_profession', './/a/text()')
                #l.add_xpath('job_profession_en', './/a/@href')
                #return l.load_item()

                item = JobProfessionItem()
                item['city'] = city
                item['city_en'] = city_en
                item['job_industry'] = job_industry
                item['job_industry_en'] = job_industry_en
                item['job_profession'] = i.xpath('.//a/text()').extract()[0]
                item['job_profession_en'] = i.xpath('.//a/@href').extract()[0]
                yield item
        pass
