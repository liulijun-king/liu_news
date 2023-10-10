# -*- coding: utf-8 -*-
# @Time    : 2023/5/18 0018 15:17
# @Author  : Liu
# @Site    : 
# @File    : incident_map.py
# @Software: PyCharm

import json
import re
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import urljoin

from loguru import logger
from lxml import etree

from base_spider import Base_spider
from tools.base_tools import req_get, time_parse, get_md5, wen_hai_parser_server


class IncidentMap(Base_spider):
    def __init__(self, is_proxies=None):
        super(IncidentMap, self).__init__(is_proxies=is_proxies)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.log = logger.add(f'./log/{self.__class__.__name__}.log')
        self.module_dict = json.load(open('./setting/config.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.config = None
        self.export = []

    def id_split(self):
        data_dict = self.module_dict
        for key, value in data_dict.items():
            self.config = value
            self.history_spider(key)

    def id_split_thread(self):
        data_dict = self.config.get("keywords")
        with ThreadPoolExecutor(max_workers=15) as pool:
            for _ in data_dict:
                pool.submit(self.history_spider, _)

    def history_spider(self, url):
        max_page = self.config.get("max_page")
        start_page = self.config.get("start_page")
        page_size = self.config.get("page_size")
        for _ in range(start_page, max_page):
            self.list_spider(_ * page_size, url)

    def list_spider(self, page, url):
        try:
            logger.info(f"当前采集链接：{url}，页码：{page}")
            response = req_get(url.format(page), headers=self.headers, proxies=self.is_proxies)
            html = re.search(r"(?<=var events = \[).*?(?=}}];)", response.content.decode())
            html_json = json.loads(f"[{html.group()}" + '}}]')
            for index, li in enumerate(html_json):
                entity_url = urljoin(url, f"event_detail?id={li.get('attributes').get('OBJECTID')}")
                self.entity_spider(entity_url)
                if index > 2:
                    break
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def entity_spider(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            responses = req_get(entity_url, headers=self.headers, proxies=self.is_proxies)
            data_xpath = "//div[@id='page_content']/div[@class='grid grid-cols-4 gap-1 py-3 px-1']"
            tree = etree.HTML(responses.content.decode())
            table = tree.xpath(data_xpath)
            headers = []
            td = []
            item = {}
            if table:
                for index, tr in enumerate(table[0].xpath('./div')):
                    if index % 2 == 0:
                        headers.append(tr.xpath('string(.)'))
                    else:
                        td.append(tr.xpath('string(.)'))
                for index, tr in enumerate(headers):
                    item[tr] = td[index]
            if item.get('Url'):
                result = self.get_event(item.get('Url'))
                item['content'] = result.get('content', '')
                item['pubtime'] = result.get('datepublished', '')
                item['author'] = result.get('author', '')
                item['types'] = self.config.get("module_name")
            self.export.append(item)
            # print(json.dumps(item, ensure_ascii=False, indent=4))
        except Exception as e:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")

    def get_event(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            responses = req_get(entity_url, headers=self.headers, proxies=self.is_proxies)
            item = wen_hai_parser_server(entity_url, responses.text)
            return item
        except Exception as e:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")
            return {}


if __name__ == '__main__':
    mp = IncidentMap()
    mp.id_split()

