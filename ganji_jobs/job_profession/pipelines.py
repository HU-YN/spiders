# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy

import MySQLdb


class JobProfessionPipeline(object):

    def __init__(self):
        # prepare the json file to store the content
        #self.file = open('items.jl', 'wb')

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
        self.sql = '''INSERT 
        INTO progress(city_en, city, 
                      job_industry_en, job_industry,
                      job_profession_en, job_profession) VALUES (%s, %s, %s, %s, %s, %s)'''
                      
                      
        self.insert_jp_item = '''
            INSERT INTO job_profession
            (id, 
            city_en, city, 
            job_profession_en, job_profession,
            job_url,
            job_salary, job_education, job_experience, job_age, job_vacancy, 
            job_company_en, job_company 
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                      
        pass
        
    def process_item(self, item, spider):
        if not self.cursor.execute(self.sql_check_jp_item, str(item['id'])):
            args = (str(item['id']), 
                    str(item['city_en']), str(item['city']),
                    str(item['job_profession_en']), str(item['job_profession']),
                    str(item['job_url']),
                    str(item['job_salary']),str(item['job_education']),str(item['job_experience']),str(item['job_age']),
                    str(item['job_vacancy']),
                    str(item['job_company_en']), str(item['job_company']))

            self.cursor.execute(self.insert_jp_item, args)
            self.db.commit()
            return item
        else:
            raise DropItem("existing item %s" % item)
        #try add to db
        #catch
            # exist
            # raise DropItem("existing item %s" % item)
        #line = json.dumps(dict(item)) + "\n"
        #self.file.write(line)
        
