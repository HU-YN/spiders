# -*- coding: utf-8 -*-

import re
import scrapy
from scrapy.loader import ItemLoader
from job_profession.items import JobProfessionItem
import MySQLdb

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')


def zhprint(obj):
    import re
    print re.sub(r"\\u([a-f0-9]{4})", lambda mg: unichr(int(mg.group(1), 16)), obj.__repr__())


class JobProfessionSpider(scrapy.Spider):
    name = "JobProfessionSpider"
    allowed_domains = ["ganji.com"]
    start_urls = ['http://www.ganji.com/index.htm']
    base = "ganji.com"
    
    #city list
    #http://www.ganji.com/index.htm
    
    #zhaopin page
    #http://anshan.ganji.com/zhaopin/
    
    #job_profession_en page
    #http://anshan.ganji.com/zpdianhuaxiaoshou/

    def __init__(self, *args, **kwargs):
        self.db = MySQLdb.connect(host="localhost",
                                  user="root",
                                 #passwd="",
                                  db="ganji",
                                  charset='utf8' )
        self.cursor = self.db.cursor()
        self.cursor.execute('use ganji')
        
        self.sql_check_jp_item = '''
                                SELECT id FROM ganji.job_profession
                                WHERE id = %s
                                 '''

        self.sql_check_jp_page = '''
                                    SELECT id FROM ganji.job_profession_pages
                                    WHERE id = %s
                                '''
        self.sql_add_jp_page = '''
                                INSERT INTO ganji.job_profession_pages
                                (id) 
                                VALUES (%s)
                                '''

    #http://anshan.ganji.com/zhaopin/
    def parse_city(self, response):
        #get city name at the very top of the page
        city = response.xpath('/html/body/div[1]/div/div[1]/a[1]/text()').extract()[0]
        city_en = re.split('\.', response.url[7:])[0]
        filename = city_en + ".html"
        with open(filename, 'wb') as f:
            f.write(response.body)

        xp = '//*[@id="wrapper"]/div[5]/div[2]/dl'
        for s in response.xpath(xp):
            #job_industry is ignored for now
            job_industry = s.xpath('.//dt/a/text()').extract()[0]
            job_industry_en = s.xpath('.//dt/a/@href').extract()[0][1:-1]
            for i in s.xpath('.//dd/i'):
                job_profession = i.xpath('.//@href').extract()[0][1:-1]
                jp_list_url = "http://" + city_en + "." + self.base + "/" + job_profession + "/"
                yield scrapy.Request(jp_list_url, callback=self.parse_job_profession_page)
        pass
        
        
    #http://anshan.ganji.com/zpdianhuaxiaoshou/
    #http://anshan.ganji.com/zpdianhuaxiaoshou/o2/
    def parse_job_profession_page(self, response):
        #add this page, and won't process any more
        self.cursor.execute(self.sql_add_jp_page, str(response.url))
        self.db.commit()

        #parse each job profession item and yield it to parse_job_item
        xp = '//*[@id="list-job-id"]/div[9]/dl'
        for s in response.xpath(xp):
            #http://biz.click.ganji.com/bizClick?url=pZwY0jCfsvQlshI6UhGGshPfUiql0ZPCpyPCmyOMXy-8uL6GmytfnHbQnH9znH0YnM98pZwVgjTknNDkPNcknjuKnbNOnbnvPH6AwNNLwHmQPjF7Pb7jnW-7gjTknHcvPjNkP1cQrHckP1mzn1TOnHDznW70njTQsRkknjDvPHDOrHcznjw0njTQn-kknjDQrHDQrjcQP1EzgjTknH93gjTknH9YgjTknHnkgjTknHNLgjTknHDYPHbknHndnHE1rHK0njTQnRkknjDQn170njTQmh-buA-8udkknjDQgjTknHDOnj0vnj9Yg16x0AI0njTQn7kknjDzPWEdnj0znHbznj0vnWnkrHDQnWcQgjTknHK0njTQnHD3sWDQnB3dPz3Qrju0njTQHyqlpyQ_mitdsWT927IGUhwfILn9H-E9PB3QrzKgHd0vPab9EgKkUARguyFspgEfPHnLsWnvca6si7wPHak9UA-ouiKZuyPoUzb9Ev6zUvd-s1EOsWT8nWmznz33PzKHmyu60hbfPHnLsWnvgjTknHNYnRkknjDVnRkknjDVnRkknj7jpZFfUyR0njTQmhD3mWFWPWNVuWK6mBYYnhmzsyFhPHTVmvNznHRBuWckrHbQ&v=2
            job_url = s.xpath('.//dt/a/@href').extract()[0]
            if 'biz' == re.split('\.', job_url[7:])[0]:
                yield scrapy.Request(job_url, callback=self.parse_job_item)

            #http://anshan.ganji.com/zpshichangyingxiao/1863580425x.htm
            city_en = re.split('\.', job_url[7:])[0]
            job_profession_en = re.split('/', job_url)[3]
            post_url = re.split('/', job_url)[4]
            id = city_en+"_"+job_profession_en+"_"+post_url
            if not self.cursor.execute(self.sql_check_jp_item, id):
                yield scrapy.Request(job_url, callback=self.parse_job_item)

        #parse the left pages and pass it to this function again
        xp = '//*[@id="list-job-id"]/div[16]/ul'
        for s in response.xpath(xp):
           if s.xpath('.//@href'):
                jp_list_url = "http://" + city_en + "." + self.base + s.xpath('.//@href').extract()[0]
                if not self.cursor.execute(self.sql_check_jp_page, jp_list_url):
                    yield scrapy.Request(jp_list_url, callback=self.parse_job_profession_page)

    def parse_job_item(self, response):
        city_en = re.split('\.', response.url[7:])[0]
        job_profession_en = re.split('/', response.url)[3]
        job_url = re.split('/', response.url)[4]
        id = city_en+"_"+job_profession_en+"_"+job_url
       
        #only yield when the id does not exist, or else, skip
        if not self.cursor.execute(self.sql_check_jp_item, id):
            #get city name at the very top of the page
            city = response.xpath('//*[@id="header"]/div/div[1]/a[1]/text()').extract()[0]
        
            job_profession = response.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[5]/ul/li[1]/em/a/text()').extract()[0]
            job_salary = response.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[5]/ul/li[2]/em/text()').extract()[0]
            job_education = response.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[5]/ul/li[3]/em/text()').extract()[0]
            job_experience = response.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[5]/ul/li[4]/em/text()').extract()[0]
            job_age = response.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[5]/ul/li[5]/em/text()').extract()[0]
            job_vacancy = response.xpath('//*[@id="wrapper"]/div[5]/div[1]/div[5]/ul/li[6]/em/text()').extract()[0]
            
            job_company_en =  re.split('/', response.xpath('//*[@id="companyName"]/span/a/@href').extract()[0])[-2]
            job_company = response.xpath('//*[@id="companyName"]/span/a/text()').extract()[0]
            
            item = JobProfessionItem()
            item['id'] = id
            item['city_en'] = city_en
            item['city'] = city
            item['job_profession'] = job_profession
            item['job_profession_en'] = job_profession_en
            item['job_salary'] = job_salary
            item['job_education'] = job_education
            item['job_experience'] = job_experience
            item['job_age'] = job_age
            item['job_vacancy'] = job_vacancy
            item['job_company_en'] = job_company_en
            item['job_company'] = job_company
            item['job_url'] = job_url
            yield item
    
    
    #http://www.ganji.com/index.htm
    def parse(self, response):
        filename = "cities.html"
        with open(filename, 'wb') as f:
            f.write(response.body)

        #This will parse the whole city pages and ectract all the cities from ganji
        xp = '/html/body/div[1]/div[3]/dl/dd'
        #dd is the city list for each character.
        for s in response.xpath(xp):
            for i in s.xpath('.//a'):
            
                ####u'http://anshan.ganji.com/'
                url = i.xpath('.//@href').extract()[0]
            
                ####city_en is the first word, without the first 7 letters-> http://
                city_en = re.split('\.', url[7:])[0]
                
                ####city is not used for now...
                city = i.xpath('.//text()').extract()[0]
                city_url = url + "zhaopin/"
                yield scrapy.Request(city_url, callback=self.parse_city)
