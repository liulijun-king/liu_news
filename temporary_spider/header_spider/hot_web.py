# -*- coding: utf-8 -*-
# @Time    : 2023/9/19 0019 9:41
# @Author  : Liu
# @Site    : 
# @File    : hot_web.py
# @Software: PyCharm
import json
import os
import re
import time
import traceback

import jsonpath
from googletrans import Translator
from kafka import KafkaProducer
from loguru import logger
from lxml import etree

from base_spider import Base_spider
from tools.base_tools import req_get, url_join, req_post


class HotWeb(Base_spider):
    def __init__(self, is_proxies=None, kafka_pro=None):
        super(HotWeb, self).__init__(is_proxies=is_proxies)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        self.base_root = "/".join(os.path.abspath(__file__).replace("\\", "/").split("/")[:-2])
        self.module = json.load(open(f'{self.base_root}/setting/hot_spider.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.config = None
        self.kafka_pro = kafka_pro
        self.translator = Translator()

    def id_split(self):
        data_dict = self.module
        for key, value in data_dict.items():
            self.config = value
            if value.get("spider_module") == "json":
                self.json_spider(key)
            elif value.get("spider_module") == "html_json":
                self.json_html_spider(key)
            else:
                self.list_spider(key)

    def list_spider(self, url):
        try:
            logger.info(f"当前采集链接：{url}")
            if self.config.get("other_req"):
                other_req = self.config.get("other_req")
            else:
                other_req = False
            response = req_get(url, headers=self.headers, proxies=self.is_proxies, other_req=other_req,
                               verify=True)
            logger.info(f"响应状态：{response.status_code}")
            if self.config.get("char"):
                res_html = response.content.decode(self.config.get("char"), "ignore")
            else:
                res_html = response.content.decode("utf-8", "ignore")
            print(f"正文:{res_html}")
            html = etree.HTML(res_html)
            lis = html.xpath(self.config.get("lis_xpath"))
            event_list = []
            for index, li in enumerate(lis):
                try:
                    if self.config.get("url_xpath"):
                        entity_url = url_join(url, li.xpath(self.config.get("url_xpath"))[0]).strip()
                    else:
                        entity_url = url_join(url, li.xpath("./@href")[0]).strip()
                    if self.config.get("title_xpath"):
                        title = self.get_string(self.config.get("title_xpath"), li).strip()
                    else:
                        title = li.xpath("string(.)").strip()
                    if self.config.get("hot_xpath"):
                        hot = li.xpath(self.config.get("hot_xpath"))[0]
                    else:
                        hot = 0
                    entity_url = re.sub("[\n\s\t]", "", entity_url)
                    logger.info(f"当前循环标题：{title}")
                    event = {
                        "en": title,
                        "enzh": self.translator.translate(title, src='auto', dest='zh-cn').text,
                        "ehot": hot,
                        "erank": index + 1,
                        "eurl": entity_url,
                    }
                    event_list.append(event)
                except Exception as e:
                    logger.error(f"循环内错误,部分数据异常：{e}")
            item = {
                "pt": int(time.time()),
                "lang": self.config.get("language"),
                "url": url,
                "ss": response.content.decode(),
                "event": event_list,
                "host": self.config.get("host"),
                "name": self.config.get("name")
            }
            self.send_data('topic_c1_original_headline', item)
        except Exception as e:
            logger.error(f"列表页请求失败！{traceback.format_exc()}")

    def json_spider(self, url):
        try:
            logger.info(f"当前采集链接：{url}")
            self.headers['content-type'] = 'application/json'
            if self.config.get("other_req"):
                other_req = self.config.get("other_req")
            else:
                other_req = False

            data = self.config.get("data").replace("'", '"') if self.config.get("data") else None
            if self.config.get("request_module") == "post":
                response = req_post(url, headers=self.headers, proxies=self.is_proxies, data=data, other_req=other_req,
                                    verify=True)
            else:
                response = req_get(url, headers=self.headers, proxies=self.is_proxies, other_req=other_req,
                                   verify=True)
            logger.info(f"响应状态：{response.status_code}")
            html_json = response.json()
            lis = jsonpath.jsonpath(html_json, self.config.get("lis_xpath"))
            event_list = []
            for index, li in enumerate(lis):
                entity_url = url_join(url, jsonpath.jsonpath(li, self.config.get("url_xpath"))[0]).strip()
                title = jsonpath.jsonpath(li, self.config.get("title_xpath"))[0].strip()
                if self.config.get("hot_xpath"):
                    hot = jsonpath.jsonpath(li, self.config.get("hot_xpath"))[0]
                else:
                    hot = 0
                event = {
                    "en": title,
                    "enzh": self.translator.translate(title, src='auto', dest='zh-cn').text,
                    "ehot": hot,
                    "erank": index + 1,
                    "eurl": entity_url,
                }
                event_list.append(event)
            item = {
                "pt": int(time.time()),
                "lang": self.config.get("language"),
                "url": url,
                "ss": response.content.decode(),
                "event": event_list,
                "host": self.config.get("host"),
                "name": self.config.get("name")
            }
            self.send_data('topic_c1_original_headline', item)
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def json_html_spider(self, url):
        try:
            logger.info(f"当前采集链接：{url}")
            self.headers['content-type'] = 'application/json'
            if self.config.get("other_req"):
                other_req = self.config.get("other_req")
            else:
                other_req = False
            data = self.config.get("data").replace("'", '"') if self.config.get("data") else None
            if self.config.get("request_module") == "post":
                response = req_post(url, headers=self.headers, proxies=self.is_proxies, data=data, other_req=other_req,
                                    verify=True)
            else:
                response = req_get(url, headers=self.headers, proxies=self.is_proxies, other_req=other_req,
                                   verify=True)
            logger.info(f"响应状态：{response.status_code}")
            html_json = response.json()
            html_content = jsonpath.jsonpath(html_json, self.config.get("html_xpath"))[0]
            html = etree.HTML(html_content)
            lis = html.xpath(self.config.get("lis_xpath"))
            event_list = []
            for index, li in enumerate(lis):
                entity_url = url_join(url, li.xpath(self.config.get("url_xpath"))[0]).strip()
                title = li.xpath(self.config.get("title_xpath")).strip()
                if self.config.get("hot_xpath"):
                    hot = jsonpath.jsonpath(li, self.config.get("hot_xpath"))[0]
                else:
                    hot = 0
                event = {
                    "en": title,
                    "enzh": self.translator.translate(title, src='auto', dest='zh-cn').text,
                    "ehot": hot,
                    "erank": index + 1,
                    "eurl": entity_url,
                }
                event_list.append(event)
            item = {
                "pt": int(time.time()),
                "lang": self.config.get("language"),
                "url": url,
                "ss": response.content.decode(),
                "event": event_list,
                "host": self.config.get("host"),
                "name": self.config.get("name")
            }
            self.send_data('topic_c1_original_headline', item)
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def send_data(self, topic, item):
        d_count = 0
        while d_count < 3:
            try:
                send_data = json.dumps(item)
                future = self.kafka_pro.send(topic, send_data.encode())
                record_metadata = future.get(timeout=20)
                if record_metadata:
                    logger.info(f'插入kafka成功')
                    break
            except Exception as e:
                d_count = d_count + 1
                logger.error(str(e))


if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['140.210.203.161:9092', '140.210.219.168:9092', '140.210.207.185:9092'])
    # "192.168.6.1:1984"
    # "192.168.0.74:7890"
    # "127.0.0.1:7890"
    proxies = {
        "http": "127.0.0.1:7890",
        "https": "127.0.0.1:7890"
    }
    mp = HotWeb(is_proxies=proxies, kafka_pro=producer)
    mp.id_split()
