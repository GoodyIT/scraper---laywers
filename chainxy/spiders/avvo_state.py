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

import math

import dropbox


class avvo_state(scrapy.Spider):

	name = 'avvo_state'

	domain = 'https://www.avvo.com'

	history = []

	output = []


	headers = {
		"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		"accept-encoding": "gzip, deflate, br",
		"upgrade-insecure-requests": "1",
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
	}

	def __init__(self):

		script_dir = os.path.dirname(__file__)

		file_path = script_dir + '/proxies.txt'

		with open(file_path, 'rb') as text:

			self.proxy_list =  [ "http://" + x.strip() for x in text.readlines()]

		access_token = 'Yatg9zZ6OLAAAAAAAAAAKEuTu64N8iip_bBD5JgvWL5_TNb9mNPIUn00bt19Qh-2'

		self.dbx = dropbox.Dropbox(access_token)

	
	def start_requests(self):

		url = "https://www.avvo.com/find-a-lawyer/"

		yield scrapy.Request(url, 
					callback=self.parse_state, 
					headers=self.headers,
					meta={
						'proxy' : random.choice(self.proxy_list),
					}
				)


	def parse_state(self, response):

		state_list = response.xpath('//div[@id="js-top-state-link-farm"]//a/@href').extract()

		for state in state_list[40:45]:

			url = self.domain + state

			yield scrapy.Request(url, callback=self.parse_category, 
					headers = self.headers,
					meta={
						'proxy' : random.choice(self.proxy_list),
					})


	def parse_category(self, response):

		category_list = response.xpath('//div[@class="bubble-farm"]//div[contains(@class, "pa-list")]//a/@href').extract()

		for category in category_list:

			url = self.domain + category

			yield scrapy.Request(url, callback=self.parse_list, 
					headers = self.headers,
					meta={
						'proxy' : random.choice(self.proxy_list),
					})


	def parse_list(self, response):

		total_count = response.xpath('//span[@id="title-total-count"]//text()').extract_first()

		if total_count:
			total_count = int(total_count.lower().strip()[1:-1].replace('results', '').strip())

		page_count = int(math.ceil(total_count / 10.0))

		for idx in range(1, page_count+1):

			next_link = response.url + '?utf8=%E2%9C%93&page='+str(idx)+'&sort=relevancy'

			yield scrapy.Request(next_link, callback=self.parse_page,
					headers=self.headers,
					meta={
						'proxy' : random.choice(self.proxy_list),
					})


	def parse_page(self, response):

		link_list = response.xpath('//a[@class="v-serp-block-link"]')

		for link in link_list:

			item = ChainItem()

			item['Full_Name'] = self.validate(''.join(link.xpath('.//text()').extract()))

			link = self.domain + link.xpath('./@href').extract_first()

			yield scrapy.Request(link, headers=self.headers, callback=self.parse_profile, meta={ 'item' : item, 'proxy' : random.choice(self.proxy_list) })
	

	def parse_profile(self, response):

		item =response.meta['item']

		check = self.validate(''.join(response.xpath('//div[contains(@class, "downgraded-card-title")]//text()').extract()))

		if check == '':

			item['Avatar'] = 'https:' + response.xpath('//div[contains(@class, "v-lawyer-card-wrapper")]//img/@src').extract_first()

			item['Review'] = response.xpath('//span[@itemprop="reviewCount"]/@content').extract_first()

			item['Rating'] = response.xpath('//span[@itemprop="ratingValue"]/@content').extract_first()

			item['Free_or_Advertiser'] = 'Advertiser'

			practice_list = self.eliminate_space(response.xpath('//ol[contains(@class, "v-chart-legend-list")]//li//a//text()').extract())

			item['Practice_Areas'] = ', '.join([ practice.split(':')[0] for practice in practice_list ])

			item['About_Summary'] = self.validate(''.join(response.xpath('//section[@id="about"]//p[contains(@class, "js-specialty-display-container")]//text()').extract()))

			item['About_Description'] = self.validate(''.join(response.xpath('//section[@id="about"]//div[@id="js-truncated-aboutme"]//text()').extract()))

			raw_address = self.validate(' '.join(response.xpath('//address[contains(@class, "js-context js-address js-v-address")]')[0].xpath('.//p//text()').extract()))

			contact_list = response.xpath('//address[contains(@class, "js-context js-address js-v-address")]')[0].xpath('.//div')

			for contact in contact_list:

				detail = contact.xpath('.//span[@class="text-muted"]//text()').extract_first()

				if 'office' in detail.lower():

					item['Office_Phone'] = self.validate(''.join(contact.xpath('.//span[@class="js-v-phone-replace-text"]//text()').extract()))

					item['Mobile_Number'] = self.validate(''.join(contact.xpath('.//span[@class="js-v-phone-replace-text"]//text()').extract()))

				if 'fax' in detail.lower():

					item['Office_Fax'] = self.validate(''.join(contact.xpath('.//span[@class="js-v-phone-replace-text"]//text()').extract()))
					
			item['Website_Address'] =  response.xpath('//div[@class="text-truncate"]//a//text()').extract_first()

			item['Email'] = ''

		else:

			item['Avatar'] = 'https:' + response.xpath('//div[contains(@class, "downgraded-card-body")]//img/@src').extract_first()

			try:
				item['Review'] = self.validate(response.xpath('//section[@id="client_reviews"]//span[@class="text-muted"]//text()').extract_first().replace('(', '').replace(')',''))
			except:
				pass

			item['Rating'] = response.xpath('//div[contains(@class, "downgraded-card-body")]//span[@class="avvo-rating-modal-info"]/@data-rating').extract_first()

			item['Free_or_Advertiser'] = 'Free'	

			item['Practice_Areas'] = self.validate(''.join(response.xpath('//div[@id="practice-areas"]//p//text()').extract()))

			item['About_Description'] = self.validate(''.join(response.xpath('//section[@id="about"]//div[@id="js-truncated-aboutme"]//text()').extract()))

			raw_address = self.validate(' '.join(response.xpath('//address[contains(@class, "js-context js-address js-v-address")]')[0].xpath('.//text()').extract()))

		addr_list = usaddress.parse(raw_address)

		address_1 = ''

		address_2 = '' 

		city = ''

		for addr in addr_list:

			if addr[1] == 'PlaceName':
				city += addr[0]	+ ' '

			elif addr[1] == 'StateName':
				item['State'] = addr[0]

			elif addr[1] == 'ZipCode':
				item['Zip_Code'] = addr[0]

			elif 'Occupancy' in addr[1]:
				address_2 += addr[0] + ' '

			else:
				address_1 += addr[0] + ' '

		item['City'] = self.validate(city)

		item['Address_Street_Line_1'] = self.validate(address_1)

		item['Address_Street_Line_2'] = self.validate(address_2)

		license_list = response.xpath('//table[contains(@class, "table-responsive-flip")]//tr')	

		license_dump = ''

		for idx, license in enumerate(license_list[1:]):

			license_dump += ' , '.join(license.xpath('.//text()').extract()) + ' | '

		item['License'] = self.validate(license_dump[:-2])

		data_list = response.xpath('//div[contains(@class, "v-resume-table-wrapper")]')

		for data in data_list:

			category = data.xpath('.//strong/text()').extract_first()

			sub_data_dump = ''

			sub_data_list = data.xpath('.//table//tr')	

			for idx, sub_data in enumerate(sub_data_list[1:]):

				sub_data_dump += ' : '.join(sub_data.xpath('.//text()').extract()) + ' | '

			sub_data_dump = self.validate(sub_data_dump[:-2])	

			try:		

				item[category.replace(' ', '_').title()] = sub_data_dump

			except:

				pass

		item['Link'] = response.url

		yield item

		yield scrapy.Request(item['Avatar'], callback=self.download_image)


	def download_image(self, response):

		file_name = response.url.split('/')[-1]

		file_to = '/Profile Avatars Avvo/' + file_name

		if 'ghost' not in file_name:

			self.dbx.files_upload(response.body, file_to)

		# with open(file_name, 'wb') as f:
		# 	f.write(response.body)


	def validate(self, item):

		try:

			return item.encode('ascii','ignore').replace('\n', '').replace('\t','').replace('\r', '').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp