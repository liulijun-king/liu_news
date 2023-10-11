# -*- coding: utf-8 -*-
# @Time    : 2023/3/17 0017 10:09
# @Author  : Liu
# @Site    : 
# @File    : nytime.py
# @Software: PyCharm


import json
import os
import re
import socket
import time
import traceback
import random
from concurrent.futures.thread import ThreadPoolExecutor
from urllib import parse
from urllib.parse import urljoin
import datetime
from loguru import logger
from lxml import etree

from settings.db_config import proxies, USER_AGENT_LIST
from spider.base_spider import Base_spider
from tools.base_tools import req_get, time_parse, get_md5


class NyTime(Base_spider):
    def __init__(self, is_proxies=None, hw_db=None, kafka_pro=None):
        super(NyTime, self).__init__(is_proxies=is_proxies)
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
        self.kafka_pro = kafka_pro
        self.hw_db = hw_db
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
        for _ in range(start_page, max_page):
            self.list_spider(_ * page_size, url)

    def list_spider(self, page, url):
        try:
            logger.info(f"当前采集链接：{url.format(page)}，页码：{page}")
            response = req_get(url.format(page), headers=self.headers, proxies=self.is_proxies)
            html = etree.HTML(response.content.decode())
            lis = html.xpath(self.config.get('lis_xpath'))
            for li in lis:
                if li:
                    entity_url = urljoin(url, li.strip())
                    self.entity_spider(entity_url)
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def video_del(self, the_xpath, html, entity_url):
        """
        视频采集
        :param the_xpath:
        :param tree:
        :param entity_url:
        :return:
        """
        video_li = []
        video_list = re.search("(?<=contentUrl\":\").*?(?=\",\"thumbnailUrl)",
                               html)
        if video_list:
            video_li.append(re.sub(r'\\/', '/', video_list.group()))
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
                    if im and re.search(r"(jpg|png)$", im):
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
                end_result.append(file_name)
        return end_result

    def entity_spider(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            title_xpath = "//div[@class='article-header']/header/h1"
            author_xpath = "//div[@class='byline']/address"
            pubtime_css = "//div[@class='byline']/time/@datetime"
            abstract_xpath = "//p[@class='t-content__chapo']"
            source_xpath = "//p[@class='info']/span[@class='cate']/a|//span[@class='column']/a|//div[@class='info']/span[@class='subtext']/a"
            html_x = "//section[@class='article-body']/div[@class='article-partial']/div[@class='article-body-item col-lg-5']"
            clear_xpath = "//section[@class='article-body']/div[@class='article-partial']/div[@class='article-body-item col-lg-5']/div[@class='article-paragraph']/figure[@class='article-inline-photo large']/figcaption/span"
            img_css = "//section[@class='article-body']/div[@class='article-partial']/div[@class='article-body-item col-lg-5']//img|//article[@class='article-content font-normal']/figure[@class='article-span-photo']/img"
            video_xpath = "//div[contains(@class,'dk-player')]"
            accessory_css = "//div[@class='entry clearfloat']/p//a"
            error_str = "(下載解振華簡報|影片重溫)"
            host = self.config['host']
            module_id = self.config['module_id']
            responses = req_get(entity_url, headers=self.headers, proxies=self.is_proxies)
            tree = etree.HTML(responses.content.decode())
            accessory = self.get_files(accessory_css, tree, entity_url, "pdf$")
            title = self.get_string(title_xpath, tree)
            author = self.get_string(author_xpath, tree)
            pubtime = time_parse(self.time_clear(self.get_string(pubtime_css, tree), '(发布|/)'))
            abstract = self.get_string(abstract_xpath, tree)
            source = self.get_string(source_xpath, tree)
            source = re.sub(r".*(来源)[:：]", "", source)
            source = self.config.get("source") if not source else source
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            for del_element in tree.xpath(clear_xpath):
                # 这里必须定位至父节点删除子节点，不允许“自杀”
                del_element.getparent().remove(del_element)
            content, content_html = self.get_content(html_x, tree, error_str)
            video = self.video_del(video_xpath, responses.content.decode(), entity_url)
            images = self.get_image(img_css, tree, entity_url)
            img_list = self.sava_img(images)
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
            self.send_data("topic_c1_original_keynewswebsites", item)
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
    mp = NyTime(is_proxies=proxies)
    mp.id_split()
    # mp.entity_spider("https://svop.ru/%d0%bf%d1%80%d0%be%d0%b5%d0%ba%d1%82%d1%8b/strategyforrussia/1920/")
