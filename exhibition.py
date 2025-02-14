# -*- coding: utf-8 -*-
import json
import os
import re
import loguru
import requests
from lxml import etree
from functools import lru_cache

from utils import get_resp_siliconflow, Saver


def get_dict(page_tree, category_spec_name):
	info_dict = {}
	items = page_tree.xpath('//div[@class="main"]//div[@class="left"]/ul/li')
	for item in items:
		name = item.xpath('./div[@class="text"]//a/text()')[0]
		# info_dict.setdefault(name, []).append(category_spec_name)
		info_dict[name] = category_spec_name
	return info_dict


def get_info(category_name):
	if os.path.exists(category_name + '.json'):
		print(f'读取{category_name}类别缓存...')
		with open(category_name + '.json', 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data
	loguru.logger.info(f'正在获取{category_name}的类别信息...')
	info_dict = {}
	index_url = 'https://www.chem17.com/exhibition/t0/list.html'
	index = get_index(index_url)

	page_tree = etree.HTML(index)
	if category_name == 'field':
		eles = page_tree.xpath('//ul[@class="public-category showone"]')[0].xpath('./li[position()>1]/a')  # 分类ul标签
	elif category_name == 'province':
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
	with open(category_name + '.json', 'w', encoding='utf-8') as f:
		json.dump(info_dict, f, ensure_ascii=False)

	loguru.logger.info(f'{category_name}类别信息获取完毕...')
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
	try:
		res = get_resp_siliconflow()(content)['choices'][0]['message']['content']
		parse_json = json.loads(re.sub(r'^.*?(\{.*}).*?$', r'\1', res, flags=re.S))
	except:
		parse_json = [{"主办单位": '', "联系方式": []}]
	print(parse_json)
	return content, parse_json

def parse_index(page_tree: etree.ElementTree):
	items = page_tree.xpath('//div[@class="main"]//div[@class="left"]/ul/li')
	for item in items:
		type = '展览'

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

		province = province_dict.get(name, None)
		field = field_dict.get(name, '其他')

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
	index_urls = ['https://www.chem17.com/exhibition/t0/list_ch0_pid0.html',
				 'https://www.chem17.com/exhibition/t0/list_p2.html',
				 'https://www.chem17.com/exhibition/t0/list_p3.html']
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
	field_dict = get_info('field')
	province_dict = get_info('province')
	saver = Saver()
	main()
