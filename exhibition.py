# -*- coding: utf-8 -*-
import re

import requests
from lxml import etree
from functools import lru_cache


def get_dict(page_tree, category_spec_name):
	info_dict = {}
	items = page_tree.xpath('//div[@class="main"]//div[@class="left"]/ul/li')
	for item in items:
		name = item.xpath('./div[@class="text"]//a/text()')[0]
		info_dict.setdefault(name, []).append(category_spec_name)
	return info_dict


def get_info(category_name):
	info_dict = {}
	index_url = 'https://www.chem17.com/exhibition/t0/list.html'
	index = get_index(index_url)

	page_tree = etree.HTML(index)
	if category_name == 'field':
		eles = page_tree.xpath('//ul[@class="public-category showone"]')[0].xpath('./li[position()>1]/a')  # 分类ul标签
	else:
		eles = page_tree.xpath('//ul[@class="public-category showone"]')[1].xpath('./li[position()>1]/a')  # 省市ul标签

	for ele in eles:
		name = ele.xpath('./text()')[0]
		url = ele.xpath('./@href')[0]

		index = get_index(url)  # 分类首页
		index_tree = etree.HTML(index)

		try:
			page_info = index_tree.xpath('//div[@class="pages"]/span[@class="jump"]/text()')[0]
		except:
			continue
		else:
			info_dict.update(get_dict(index_tree, name))

			totle_pages = int(re.search(r'共(\d)页', page_info).group(1))
			for page in range(2, totle_pages + 1):
				url_head = url.rsplit('/', 1)[0]
				next_url = url_head + f'_p{page}'
				next_page = requests.get(next_url)
				next_page_tree = etree.HTML(next_page.text)
				next_info_dict = get_dict(next_page_tree, name)
				info_dict.update(next_info_dict)
		# break
	return info_dict


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

def parse_index(page_tree: etree.ElementTree):
	items = page_tree.xpath('//div[@class="main"]//div[@class="left"]/ul/li')
	for item in items:
		field = '展览'
		cover = item.xpath('./div[@class="image"]//img/@src')[0]

		name = item.xpath('./div[@class="text"]//a/text()')[0]

		time = item.xpath('./div[@class="text"]/div[@class="bottom"]/b[1]/text()')[0]
		year = re.match(r'^\d{4}', time).group()
		time = re.sub(r'-', '/', time)
		time = re.sub(r' ~ ', '--', time)

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
	index_urls = ['https://www.chem17.com/exhibition/t0/list_ch0_pid0.html',
				 'https://www.chem17.com/exhibition/t0/list_p2.html',
				 'https://www.chem17.com/exhibition/t0/list_p3.html']
	for index_url in index_urls:
		index = get_index(index_url)

		page_tree = etree.HTML(index)
		parse_index(page_tree)



if __name__ == '__main__':
	# main()
	res = get_info('field')
	print(res)