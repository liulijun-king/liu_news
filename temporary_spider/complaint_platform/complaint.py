# -*- coding: utf-8 -*-
# @Time    : 2023/8/2 0002 9:23
# @Author  : Liu
# @Site    : 
# @File    : complaint.py
# @Software: PyCharm

import json
import os
import re
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta

from loguru import logger
from lxml import etree

from base_spider import Base_spider
from tools.base_tools import req_get, time_parse, get_md5, req_post, get_proxies
from tools.push_service import all_push_server


class Complaint(Base_spider):
    def __init__(self, is_proxies=None):
        super(Complaint, self).__init__(is_proxies=is_proxies)
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.base_root = "/".join(os.path.abspath(__file__).replace("\\", "/").split("/")[:-2])
        self.log = logger.add(f'{self.base_root}/log/{self.__class__.__name__}.log')
        self.module = json.load(open(f'{self.base_root}/setting/one_spider.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.config = None
        self.export = []

    def id_split(self):
        data_dict = self.module
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
        self.get_cookie()
        for _ in range(start_page, max_page):
            self.list_spider(_ * page_size, url)

    def list_spider(self, page, url1):
        local_time = time.strftime("%Y-%m-%d", time.localtime())
        yesterday_time = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400 * 0))
        dates = self.get_dates_list(yesterday_time, local_time)
        for index, date in enumerate(dates):
            try:
                url = url1.format(date, date, str(page))
                logger.info(f"当前采集链接：{url}，页码：{page}")
                response = req_get(url, headers=self.headers, proxies=get_proxies())
                res_data = response.json()
                if response.status_code == 200 and res_data.get("rows"):
                    if len(res_data.get("rows")) == 0:
                        break
                    rows = res_data.get("rows")
                    for item in rows:
                        self.entity_spider(item, url)
                    if len(self.export) > 0:
                        all_push_server(self.export, "major_info")
                        self.export.clear()
                else:
                    self.get_cookie()
            except Exception as e:
                logger.error(f"列表页请求失败！{e}")

    def get_cookie(self):
        response = req_post('https://gd.tsgs.12315.cn/public-web/slider/getToken', headers=self.headers)
        token = response.text
        self.headers['token'] = token.replace('"', '')

    def entity_spider(self, entity_item, entity_url):
        try:
            logger.info(f"实体页链接：{entity_item.get('id')}")
            host = self.config['host']
            title = entity_item.get("entName", "")
            author = entity_item.get("department", "")
            source = "广东消费投诉信息公示平台"
            pubtime = entity_item.get("endtime", "")
            abstract = ""
            content_html = f"<div><h1>{entity_item.get('entName')}\n</h1>" \
                           f"<p>{entity_item.get('entName')},统一社会信用代码:{entity_item.get('creditNo')},地址:{entity_item.get('entAddr')}\n投诉问题：\n</p>" \
                           f"<p>{entity_item.get('content')}\n处理结果：\n{entity_item.get('res')}\n公示部门：{entity_item.get('department')}</p></div>"
            html = etree.HTML(content_html)
            content = html.xpath('//div')[0].xpath('string(.)')
            images = []
            video = []
            item = {
                'title': title.strip() + "投诉信息公示",  # 标题
                'author': re.sub(r"[\n\r\t]", '', author).strip(),  # 作者
                'source': source,
                'pubtime': time_parse(pubtime.strip()),  # 发布时间
                'abstract': abstract.strip(),
                'content': content,  # 内容
                'content_html': content_html,  # 内容
                'pictures': "#".join(list(set(images))),  # 图片链接
                'videos': "#".join(list(set(video))),  # 视频链接
                'module_name': self.config['module_name'],
                'module_url': self.config['module_url'],
                # 'module_url_md5': get_md5(self.config['module_url']),
                'ref_url': entity_url,
                'source_url': entity_url,
                'url_md5': get_md5(entity_url + entity_item.get('id')),
                'uuid': get_md5(entity_url + entity_item.get('id')),
                'host': host,
                'sub_host': host.replace("www.", ''),
                'website_name': self.config['website_name'],  # 站点名称
                'article_type': self.config['article_type'],
                'language': self.config['language'],  # 语种
                'language_str': self.config['language_str'],
                'crawler_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),  # 采集时间
                'insert_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'update_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "crawler_type": "changsha",
                "region": 0,
                "S": "zicai",
            }
            logger.info(f"url_md5:{item['url_md5']}")
            self.export.append(item)
        except Exception:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")

    def get_dates_list(self, start_date, end_date):
        dates = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        while current_date <= end_date:
            formatted_date = current_date.strftime('%Y-%m-%d')
            dates.append(formatted_date)
            current_date += timedelta(days=1)
        return dates


if __name__ == '__main__':
    mp = Complaint()
    mp.id_split()
