# -*- coding: utf-8 -*-
import re

import requests
from lxml import etree
from functools import lru_cache

def get_category_info():
	index_url = 'https://www.chem17.com/exhibition/t0/list_ch0_pid0.html'
	index = get_index(index_url)

	page_tree = etree.HTML(index)
	category_eles = page_tree.xpath('//ul[@class="public-category showone"]')[0].xpath('./li[position()>1]/a')  # 分类ul标签
	province_eles = page_tree.xpath('//ul[@class="public-category showone"]')[1].xpath('./li[position()>1]/a')  # 省市ul标签


# @lru_cache
def get_index(index_url):
	resp = requests.get(index_url)
	if resp.status_code == 200:
		return resp.text
	else:
		raise requests.exceptions.RequestException

def parse_detail(detail_url):
	detail_index = get_index(detail_url)
	detail_tree = etree.HTML(detail_index)
	content_ele = detail_tree.xpath('//div[@class="exhi-content"]')[0]
	content = etree.tostring(content_ele, encoding='utf-8').decode('utf-8')
	return content

def parse_category(page_tree: etree.ElementTree):
	items = page_tree.xpath('//div[@class="main"]//div[@class="left"]/ul/li')
	for item in items:
		field = '展览'
		cover = item.xpath('./div[@class="image"]//img/@src')[0]

		name = item.xpath('./div[@class="text"]//a/text()')[0]

		time = item.xpath('./div[@class="text"]/div[@class="bottom"]/b[1]/text()')[0]
		year = re.match(r'^\d{4}', time).group()
		time = re.sub(r'-', '/', time)
		time = re.sub(r'~', '--', time)

		place = item.xpath('./div[@class="text"]/div[@class="bottom"]/b[2]/text()')[0]
		type = '线下'
		try:
			item.xpath('./div[@class="text"]/div[@class="bottom"]/b[2]//a')
			type = '线上'
		except:
			pass

		detail_url = item.xpath('./div[@class="text"]//a/@href')[0]
		content = parse_detail(detail_url)
		print(name, time, place, content)
		break

def main():
	index_url = 'https://www.chem17.com/exhibition/t0/list_ch0_pid0.html'
	index = get_index(index_url)

	page_tree = etree.HTML(index)
	category_eles = page_tree.xpath('//ul[@class="public-category showone"]')[0].xpath('./li[position()>1]/a')  # 分类ul标签
	province_eles = page_tree.xpath('//ul[@class="public-category showone"]')[1].xpath('./li[position()>1]/a')  # 省市ul标签

	for category_ele in category_eles:
		category_name = category_ele.xpath('./text()')[0]
		category_url = category_ele.xpath('./@href')[0]

		category_index = get_index(category_url)  # 分类首页
		category_index_tree = etree.HTML(category_index)

		try:
			page_info = category_index_tree.xpath('//div[@class="pages"]/span[@class="jump"]/text()')[0]
		except:
			continue
		else:
			totle_pages = int(re.search(r'共(\d)页', page_info).group(1))
			if totle_pages == 1:
				parse_category(category_index_tree)
			else:
				pass
			break



if __name__ == '__main__':
	main()