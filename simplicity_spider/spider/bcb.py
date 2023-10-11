# -*- coding: utf-8 -*-
# @Time    : 2023/3/20 0020 10:44
# @Author  : Liu
# @Site    : 
# @File    : bcb.py
# @Software: PyCharm
import datetime
import json
import os
import re
import socket
import time
import random
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from urllib import parse
from urllib.parse import urljoin

import jsonpath
from kafka import KafkaProducer
from loguru import logger
from lxml import etree
from tools.hw_obs import HwObs

from settings.db_config import proxies, USER_AGENT_LIST
from spider.base_spider import Base_spider
from tools.base_tools import req_get, time_deal, get_md5


class Bcb(Base_spider):
    def __init__(self, is_proxies=None, hw_db=None, kafka_pro=None):
        super(Bcb, self).__init__(is_proxies=is_proxies)
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': USER_AGENT_LIST[random.randint(0, 32)],
        }
        self.path = "/".join(os.path.split(os.path.realpath(__file__))[0].split('/')[:-1])
        self.log = logger.add(f'{self.path}/log/{self.__class__.__name__}.log')
        self.module_dict = json.load(open(f'{self.path}/settings/head_config.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.hw_db = hw_db
        self.kafka_pro = kafka_pro
        self.config = None

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
        if self.config['spider_module'] == 'html':
            self.one_spider(url)
        elif self.config.get("json_spider"):
            for _ in range(start_page, max_page):
                self.json_spider(_ * page_size, url)
        else:
            for _ in range(start_page, max_page):
                self.list_spider(_ * page_size, url)

    def json_spider(self, page, url):
        try:
            logger.info(f"当前采集链接：{url.format(page)}，页码：{page}")
            response = req_get(url.format(page), headers=self.headers, proxies=self.is_proxies)
            lis = jsonpath.jsonpath(response.json(), self.config['json_spider'])
            for li in list(set(lis)):
                if re.search(r"javascript", li):
                    continue
                if li:
                    entity_url = urljoin(url, li.strip())
                    self.entity_spider(entity_url)
                break
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def list_spider(self, page, url):
        try:
            logger.info(f"当前采集链接：{url.format(page)}，页码：{page}")
            response = req_get(url.format(page), headers=self.headers, proxies=self.is_proxies)
            html = etree.HTML(response.content.decode("gbk", 'ignore'))
            lis = html.xpath(self.config.get('lis_xpath'))
            for li in list(set(lis)):
                if re.search(r"javascript", li):
                    continue
                if li:
                    if self.config.get('spice_spider'):
                        entity_url = self.config.get('spice_spider') + li.strip()
                        self.entity_spider(entity_url)
                    else:
                        entity_url = urljoin(url, li.strip())
                        self.entity_spider(entity_url)
                break
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def one_spider(self, url):
        try:
            logger.info(f"当前采集链接：{url}")
            response = req_get(url, headers=self.headers, proxies=self.is_proxies)
            html = etree.HTML(response.content.decode('gbk'))
            lis = html.xpath(self.config.get('lis_xpath'))
            for li in list(set(lis)):
                if re.search(r"javascript", li):
                    continue
                if li:
                    entity_url = urljoin(url, li.strip())
                    self.entity_spider(entity_url)
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def video_del(self, the_xpath, tree, entity_url):
        """
        视频采集
        :param the_xpath:
        :param tree:
        :param entity_url:
        :return:
        """
        video_li = []
        for v in tree.xpath(the_xpath):
            if re.search(r"youtube.com/embed/", v):
                video_li.append(v)
        return video_li

    def get_image(self, the_xpath, tree, entity_url):
        images = []
        img_child_css = './@srcset|./@src'
        imgs = tree.xpath(the_xpath)
        for img in imgs:
            for im in img.xpath(img_child_css):
                if im.endswith("gif"):
                    continue
                if re.search('https.*?(png|webp)', im):
                    im = re.search('https.*?(png|webp)', im).group()
                    images.append(parse.urljoin(entity_url, im))
                else:
                    if im and re.search(r"(jpg|png)", im):
                        images.append(parse.urljoin(entity_url, im))
        images = list(set(images))
        return images

    def sava_img(self, images):
        end_result = []
        for img in images:
            if re.search("(jpg|png|webp)", img):
                end_name = re.search("(jpg|png|webp)", img).group()
            else:
                end_name = 'png'
            file_name = f"topic_c1_original_keynewswebsite/{datetime.datetime.now().strftime('%Y-%m-%d').replace('-', '')}/{get_md5(img)}.{end_name}"
            responses = req_get(img, headers=self.headers, proxies=self.is_proxies)
            res = self.hw_db.up_data(file_name, responses.content)
            if res:
                logger.info("文件存储成功!")
                end_result.append(file_name)
        return end_result

    def entity_spider(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            if re.search("/news/t/", entity_url):
                return
            title_xpath = "//span[contains(@class,'title')]|//div[@class='title']|//div[@class='in_top_tt']/h2"
            author_xpath = "//article[@id='story']/header[@class='css-7gc7xj euiyums1']/div[@class='css-103l8m3']/div[@class='css-iixmjo epjyd6m1']/div[@class='css-233int epjyd6m0']/p[@class='css-4anu6l e1jsehar1']"
            pubtime_css = "//span[contains(@class,'STYLE4')]|//div[@class='title_info']|//div[@class='in_top_tt']/p"
            abstract_xpath = "//p[@class='t-content__chapo']"
            source_xpath = "//p[@class='info']/span[@class='cate']/a|//span[@class='column']/a|//div[@class='info']/span[@class='subtext']/a"
            html_x = "//div[@id='cont']|//div[@class='content_info']|//div[@class='real_cont']"
            clear_xpath = "//div[@class='m-interstitial']|//p[@class='t-copyright']|//script|//style|//div[@id='comment']|//div[@class='you']|//div[@class='dibu']"
            img_css = "//div[@id='cont']//img|//div[@class='content_info']//img|//div[@class='real_cont']//img"
            video_xpath = "//div[@class='zuo']//iframe/@src"
            accessory_css = "//div[@class='entry clearfloat']/p//a"
            error_str = "(下載解振華簡報|影片重溫)"
            host = self.config['host']
            module_id = int(self.config['module_id'])
            responses = req_get(entity_url, headers=self.headers, proxies=self.is_proxies)
            # itm = wen_hai_parser_server(entity_url, responses.content.decode())
            tree = etree.HTML(responses.content.decode('gbk', 'ignore'))
            accessory = self.get_files(accessory_css, tree, entity_url, "pdf$")
            title = self.get_string(title_xpath, tree)
            author = self.get_string(author_xpath, tree)
            pubtime = time_deal(
                self.time_search(self.get_string(pubtime_css, tree),
                                 '(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2})'))
            if not pubtime:
                pubtime = time_deal(self.time_search(entity_url, '\d{4}/\d{2}/\d{2}'))
            abstract = self.get_string(abstract_xpath, tree)
            source = self.get_string(source_xpath, tree)
            source = re.sub(r".*(来源)[:：]", "", source)
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            for del_element in tree.xpath(clear_xpath):
                # 这里必须定位至父节点删除子节点，不允许“自杀”
                del_element.getparent().remove(del_element)
            content, content_html = self.get_content(html_x, tree, error_str)
            video = self.video_del(video_xpath, tree, entity_url)
            images = self.get_image(img_css, tree, entity_url)
            img_list = self.sava_img(images)
            # img_list = ""
            item = {
                "module_id": module_id,  # 模块id
                'title': title.strip(),  # 标题
                'headline': '',  # 不太明白
                'author': re.sub(r"[\n\r\t]", '', author).strip(),  # 作者
                'source': source,
                'pubtime': pubtime,  # 发布时间
                'abstract': abstract.strip(),
                'content': content,  # 内容
                'content_html': content_html,  # 内容
                'pictures': "#".join(images),  # 图片链接
                'videos': "#".join(video),  # 视频链接
                'accessory': "#".join(accessory),  # 附件链接
                'module_name': self.config['module_name'],
                'module_url': self.config['module_url'],
                'module_url_md5': get_md5(self.config['module_url']),
                'ref_url': entity_url,
                'source_url': entity_url,
                'url_md5': get_md5(entity_url),
                'host': host,
                'sub_host': host.replace("www.", ''),
                'website_name': self.config['website_name'],  # 站点名称
                'website_sub_name': self.config['website_name'],
                'article_type': self.config['article_type'],
                'language': self.config['language'],  # 语种
                'language_str': self.config['language_str'],
                'crawler_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),  # 采集时间
                'insert_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'update_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'images': img_list if img_list else '',
                'crawler_on': ip,
                "exists_typeset": 0,
            }
            if pubtime:
                self.send_data("topic_c1_original_keynewswebsites", item)
            # print(json.dumps(item, ensure_ascii=False, indent=4))
        except Exception as e:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")

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
    hw_obs = HwObs()
    mp = Bcb(is_proxies=proxies, hw_db=hw_obs, kafka_pro=producer)
    mp.id_split()
