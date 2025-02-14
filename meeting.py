# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import json
import os
import re
import loguru
import requests
from lxml import etree
from functools import lru_cache

from utils import get_resp_siliconflow, Saver


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
	try:
		res = get_resp_siliconflow()(content)['choices'][0]['message']['content']
		parse_json = json.loads(re.sub(r'^.*?(\{.*}).*?$', r'\1', res, flags=re.S))
	except:
		parse_json = {"主办单位": '', "联系方式": []}
	return content, parse_json

def parse_index(page_tree: etree.ElementTree):
	items = page_tree.xpath('//div[@class="main meeting-list"]//div[@class="left"]/ul/li')
	for item in items:
		type = '会议'

		try:
			item.xpath('./div[@class="text"]/div[@class="bottom"]/b[2]//a')[0]
			form = '线上'
		except:
			form = '线下'

		cover = item.xpath('./div[@class="image"]//img/@src')[0]

		name = item.xpath('./div[@class="text"]//a/text()')[0]
		try:
			summary = item.xpath('./div[@class="text"]/span/text()')[0]
		except:
			summary = None

		time = item.xpath('./div[@class="text"]/div[@class="bottom"]/b[1]/text()')[0]
		year = re.match(r'^\s*\d{4}', time).group()

		province = None
		field = None

		time = re.sub(r'-', '/', time)
		time = re.sub(r' ~ ', '--', time)

		place = item.xpath('./div[@class="text"]/div[@class="bottom"]/b[2]/text()')[0]

		detail_url = item.xpath('./div[@class="text"]//a/@href')[0]
		content, parse_json = parse_detail(detail_url)
		organizer = parse_json.get('主办单位') if parse_json.get('主办单位') else '详情见下文'
		contact_detail = str(parse_json.get('联系方式')) if parse_json.get('联系方式') else None
		annex = None
		# print(field, '\n', type, '\n', form, '\n', year, '\n', province, '\n', cover, '\n', name, '\n', time, '\n', place, '\n', organizer, '\n', summary, '\n', content, '\n', contact_detail, '\n', annex)
		yield {
			'field': field,
			'type': type,
			'form': form,
			'year': year,
			'province': province,
			'cover': cover,
			'name': name,
			'time': time,
			'place': place,
			'organizer': organizer,
			'summary': summary,
			'content': content,
			'contact_detail': contact_detail,
			'annex': annex
		}

def main():
	index_urls = ['https://www.chem17.com/meeting/t0/list.html',
				 'https://www.chem17.com/meeting/t0/list_p2.html',
				 'https://www.chem17.com/meeting/t0/list_p3.html',
				 'https://www.chem17.com/meeting/t0/list_p4.html',
				 'https://www.chem17.com/meeting/t0/list_p5.html']
	for index_url in index_urls:
		index = get_index(index_url)

		page_tree = etree.HTML(index)
		res_gen = parse_index(page_tree)

		# with open('result.json', 'a', encoding='utf-8') as f:
		for res in res_gen:
			# json.dump(res, f, ensure_ascii=False)
				saver.save(res)
	saver.close()

if __name__ == '__main__':
	saver = Saver()
	main()
