# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobProfessionItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    update_time = scrapy.Field()
    status = scrapy.Field()
    city_en = scrapy.Field()
    city = scrapy.Field()
    job_industry_en = scrapy.Field()
    job_industry = scrapy.Field()
    job_profession_en = scrapy.Field()
    job_profession = scrapy.Field()
    job_salary = scrapy.Field()
    job_education = scrapy.Field()
    job_experience = scrapy.Field()
    job_age = scrapy.Field()
    job_vacancy = scrapy.Field()
    job_url = scrapy.Field()
    
    job_company = scrapy.Field()
    job_company_en = scrapy.Field()
    pass
