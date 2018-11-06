# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from scrapy import signals

from scrapy.xlib.pydispatch import dispatcher

from selenium import webdriver

from lxml import etree

from lxml import html

import random

import pdb

import usaddress

import dropbox

from nameparser import HumanName

class temp_all(scrapy.Spider):

	handle_httpstatus_list = [403] 

	name = 'temp'

	domain = 'https://www.avvo.com'

	history = []

	output = []

	headers = {
		"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"accept-encoding": "gzip, deflate, br",
		"upgrade-insecure-requests": "1",
		"referer": "None"
	}


	def __init__(self):

		script_dir = os.path.dirname(__file__)

		file_path = script_dir + '/proxies.txt'

		with open(file_path, 'rb') as text:

			self.proxy_list =  [ "http://" + x.strip() for x in text.readlines()]

		access_token = 'Yatg9zZ6OLAAAAAAAAAAKEuTu64N8iip_bBD5JgvWL5_TNb9mNPIUn00bt19Qh-2'
	
	def start_requests(self):

		url = "https://www.avvo.com/find-a-lawyer/all-practice-areas"
		urls = [
			"https://www.avvo.com/find-a-lawyer/all-practice-areas"
		]

		for url in urls:
			yield  scrapy.Request(url, 
					callback=self.parse_category, 
					headers=self.headers,
					meta={
						'proxy' : random.choice(self.proxy_list),
					},
					dont_filter=True
				)


	def parse_category(self, response):

		if response.status == 403:

			yield scrapy.Request(response.url, 
					callback=self.parse_category, 
					headers=self.headers,
					meta={
						'proxy' : random.choice(self.proxy_list),
					},
					dont_filter=True
				)

		else:
			category_list = response.xpath('//div[@id="areas-of-law"]//div[@class="v-content-wrapper"]//a/@href').extract()

			for category in category_list[70:75]:

				url = self.domain + category

				yield scrapy.Request(url, callback=self.parse_state, 
						headers = self.headers,
						meta={
							'proxy' : random.choice(self.proxy_list),
						}, dont_filter=True)


	def parse_state(self, response):
		pass