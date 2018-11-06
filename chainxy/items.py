# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ChainItem(Item):

	Last_Answered_Date = Field()

	Count_Of_Answers = Field()

	Full_Name = Field()

	First_Name = Field()

	Middle_Name = Field()

	Last_Name = Field()

	Mobile_Number = Field()

	Free_or_Advertiser = Field()

	Practice_Areas = Field()

	Address_Street_Line_1 = Field()

	Address_Street_Line_2 = Field()

	City = Field()

	State = Field()

	Zip_Code = Field()

	Office_Phone = Field()

	Office_Fax	 = Field()

	Website_Address = Field()

	Email = Field()

	About_Summary = Field()

	About_Description = Field()

	License = Field()

	Education = Field()

	Awards = Field()

	Work_Experience = Field()

	Associations = Field()

	Publications = Field()

	Speaking_Engagements = Field()

	Legal_Cases = Field()

	Avatar = Field()

	Rating = Field()

	Review = Field()

	Link = Field()

	Link_Via = Field()
