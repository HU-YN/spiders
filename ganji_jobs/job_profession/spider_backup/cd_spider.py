# -*- coding: utf-8 -*-


import scrapy
from job_profession.items import JobProfessionItem

def zhprint(obj):
    import re
    print re.sub(r"\\u([a-f0-9]{4})", lambda mg: unichr(int(mg.group(1), 16)), obj.__repr__())

class cdSpider(scrapy.Spider):
    name = "cd"
    #allowed_domains = ["ganji.com"]
    allowed_domains = ["127.0.0.1"]
    start_urls = [
        "http://127.0.0.1/cd.html",
    ]

    def parse(self, response):
        #filename = self.name + ".html"
        #filename = response.url.split("/")[-2]
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        
        xp = '//*[@id="wrapper"]/div[5]/div[2]/dl'
        for s in response.xpath(xp):
            city = u'成都'
            city_en = 'cd'
            job_industry = s.xpath('.//dt/a/text()').extract()[0]
            job_industry_en = s.xpath('.//dt/a/@href').extract()[0]
            for i in s.xpath('.//dd/i'):
                item = JobProfessionItem()
                item['city'] = city
                item['city_en'] = city_en
                item['job_industry'] = job_industry
                item['job_industry_en'] = job_industry_en
                item['job_profession'] = i.xpath('.//a/text()').extract()[0]
                item['job_profession_en'] = i.xpath('.//a/@href').extract()[0]
                yield item
            
            
#/html/body/div[3]/div[5]/div[2]/dl[1]/dt/a
#response.xpath('/html/body/div[3]/div[5]/div[2]/dl[1]/dt/a/text()').extract()
#[u'销售']

#/html/body/div[3]/div[5]/div[2]/dl 是所有的dl列表