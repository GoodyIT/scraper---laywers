# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv

import time

import datetime

from scrapy import signals

from scrapy.contrib.exporter import CsvItemExporter


class ChainxyPipeline(object):

    def __init__(self):

        self.files = {}


    @classmethod
    def from_crawler(cls, crawler):

        pipeline = cls()

        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)

        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)

        return pipeline


    def spider_opened(self, spider):

        file = open('%s_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')), 'w+b')
        
        self.files[spider] = file
        
        self.exporter = CsvItemExporter(file)

        self.exporter.fields_to_export = ['First_Name','Middle_Name', 'Last_Name', 'Last_Answered_Date',
            'Count_Of_Answers', 'Free_or_Advertiser', 'Avatar','Rating',
            'Review', 'Address_Street_Line_1',
            'Address_Street_Line_2', 'City', 'State', 'Zip_Code',
            'Mobile_Number', 'Office_Phone', 'Office_Fax','Website_Address', 
            'Practice_Areas', 'About_Summary', 'About_Description',
            'License', 'Education', 'Awards', 'Work_Experience', 'Associations',
            'Publications', 'Speaking_Engagements', 'Legal_Cases','Link', 'Link_Via'
        ]
       
        self.exporter.start_exporting()        


    def spider_closed(self, spider):
        
        self.exporter.finish_exporting()
        
        file = self.files.pop(spider)
        
        file.close()


    def process_item(self, item, spider):

        self.exporter.export_item(item)
        
        return item