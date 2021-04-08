import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import BorderbankItem
from itemloaders.processors import TakeFirst
base ='https://www.border.bank/DesktopModules/EasyDNNNews/getnewsdata.ashx?language=en-US&portalid=0&tabid=64&moduleid=729&pageTitle=Information%20and%20Helpful%20Articles%20Out%20On%20Our%20Blog%20%7C%20Border%20Bank&numberOfPostsperPage=9&startingArticle={}'


class BorderbankSpider(scrapy.Spider):
	name = 'borderbank'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		if not response.text:
			return
		data = json.loads(response.text)
		raw_data = scrapy.Selector(text=data['content'])
		post_links = raw_data.xpath('//div[@class="blueboxnews"]')
		for post in post_links:
			url = post.xpath('.//a[@class="LightBlueButton"]/@href').get()
			date = post.xpath('.//span[@class="date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if post_links:
			self.page += 9
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="GreyFullSection"]/h1/text()').get()
		description = response.xpath('//div[@class="content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BorderbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
