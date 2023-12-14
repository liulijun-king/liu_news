# -*- coding: utf-8 -*-
# @Time    : 2023/9/1 0001 14:22
# @Author  : Liu
# @Site    : 
# @File    : header_spider.py
# @Software: PyCharm

import datetime
import json
import os
import re
import socket
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

from kafka import KafkaProducer
from loguru import logger
from lxml import etree

from base_spider import Base_spider
from tools.base_tools import req_get, get_md5, time_deal, get_date, get_file_type, url_join, str_for_time
from tools.mini_down import MiniDown


class HeadSpider(Base_spider):
    def __init__(self, is_proxies=None, hw_db=None, kafka_pro=None, redis_conn=None):
        super(HeadSpider, self).__init__(is_proxies=is_proxies)
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
        self.module = json.load(open(f'{self.base_root}/setting/one_spider.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.host_rule = json.load(open(f'{self.base_root}/setting/host_xpath.json', 'r', encoding="utf-8"))
        self.hw_db = hw_db
        self.kafka_pro = kafka_pro
        self.redis_conn = redis_conn
        # self.source_result = {}

    def get_cookie(self, url):
        if "vot.org" in url:
            response = req_get(url, headers=self.headers, proxies=self.is_proxies)
            self.headers['cookie'] = response.headers['Set-Cookie']
            print(response.headers)

    def id_split(self):
        data_dict = self.module
        for key, value in data_dict.items():
            if re.search("美国彭博社", value['website_name']):
                self.history_spider(key, value)

    def id_split_thread(self):
        data_dict = self.module
        with ThreadPoolExecutor(max_workers=50) as pool:
            for key, value in data_dict.items():
                pool.submit(self.history_spider, url=key, items=value)

    def history_spider(self, url, items):
        max_page = items.get("max_page")
        start_page = items.get("start_page")
        page_size = items.get("page_size")
        for _ in range(start_page, max_page):
            if items.get("spider_module") == 'date':
                self.date_spider(_ * page_size, url, items)
            else:
                self.list_spider(_ * page_size, url, items)
            break

    def date_spider(self, page, url, items):
        try:
            page = get_date(page)
            url = url.format(str(page))
            logger.info(f"当前采集链接：{url}，页码：{page}")
            response = req_get(url, headers=self.headers, proxies=self.is_proxies)
            if items.get("char"):
                html = etree.HTML(response.content.decode(items.get("char"), "ignore"))
            else:
                html = etree.HTML(response.content.decode())
            if items.get("lis_xpath").endswith("href"):
                lis = html.xpath(items.get("lis_xpath"))
            else:
                lis = re.findall(items.get("lis_xpath"), response.content.decode("utf-8", "ignore"))
            logger.info(f"测试站点:{items['module_name']},响应状态：{response.status_code},数据长度{len(lis)}")
            for li in lis:
                entity_url = url_join(url, li).strip()
                if not self.redis_conn.sismember("key_news:pl", entity_url):
                    self.entity_spider(entity_url, items)
                else:
                    logger.info(f"重复数据，记录redis，数据链接：{entity_url}")
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def list_spider(self, page, url, items):
        try:
            url = url.format(str(page))
            logger.info(f"当前采集链接：{url}，页码：{page}")
            if items.get("other_req"):
                other_req = items.get("other_req")
            else:
                other_req = False
            response = req_get(url, headers=self.headers, proxies=self.is_proxies, other_req=other_req, verify=True)
            if items.get("char"):
                html = etree.HTML(response.content.decode(items.get("char"), "ignore"))
            else:
                html = etree.HTML(response.content.decode())
            if items.get("lis_xpath").endswith("href"):
                lis = html.xpath(items.get("lis_xpath"))
            else:
                lis = re.findall(items.get("lis_xpath"), response.content.decode("utf-8", "ignore"))
            logger.info(f"测试站点:{items['module_name']},响应状态：{response.status_code},数据长度{len(lis)}")
            for li in lis:
                entity_url = url_join(url, li).strip()
                if not self.redis_conn.sismember("key_news:pl", entity_url):
                    self.entity_spider(entity_url, items)
                else:
                    logger.info(f"重复数据，记录redis，数据链接：{entity_url}")
        except Exception as e:
            logger.error(f"列表页请求失败！{traceback.format_exc()}")

    def entity_spider(self, entity_url, items):
        try:
            logger.info(f"实体页链接：{entity_url}")
            url_host = re.search("(?<=://).*?(?=/)", entity_url).group()
            url_host = url_host.replace("www.", "")
            entity_rule = self.host_rule.get(url_host)
            title_xpath = entity_rule['title_xpath']
            author_xpath = entity_rule['author_xpath']
            pubtime_css = entity_rule['pubtime_css']
            abstract_xpath = entity_rule['abstract_xpath']
            source_xpath = entity_rule['source_xpath']
            html_x = entity_rule['html_x']
            clear_xpath = "//script|//style"
            img_css = entity_rule['img_css']
            video_css = entity_rule['video_css']
            accessory_css = entity_rule['accessory_css']
            img_child_css = "./@src|./@data-src"
            host = items['host']
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            module_id = get_md5(items.get("module_url"))
            if items.get("other_req"):
                other_req = items.get("other_req")
            else:
                other_req = False
            responses = req_get(entity_url, headers=self.headers, proxies=self.is_proxies, other_req=other_req)
            logger.info(f"实体页链接：{entity_url},响应码：{responses.status_code}")
            if items.get("char"):
                tree = etree.HTML(responses.content.decode(items.get("char"), 'ignore'))
            else:
                tree = etree.HTML(responses.content.decode("utf-8", 'ignore'))
            title = tree.xpath(title_xpath)[0].xpath('string(.)') if tree.xpath(title_xpath) else tree.xpath("//title")[
                0].xpath('string(.)')
            author = tree.xpath(author_xpath)[0].xpath('string(.)') if tree.xpath(author_xpath) else ""
            author = re.sub(".*?作者[:：]|发表[:：].*", "", author)
            if tree.xpath(pubtime_css):
                try:
                    pubtime = tree.xpath(pubtime_css)[0].xpath('string(.)')
                except:
                    pubtime = tree.xpath(pubtime_css)[0]
            else:
                pubtime = ""
            pubtime = re.sub("(.*(发布时间|日期|时间|发表)\s{0,4}[:：]|来源[:：].*|Published)", "",
                             re.sub("[\n\r\t]", "", pubtime).strip()).strip()
            pubtime = time_deal(pubtime)
            abstract = tree.xpath(abstract_xpath)[0].xpath('string(.)') if tree.xpath(abstract_xpath) else ""
            html = tree.xpath(html_x)[0]
            for del_element in html.xpath(clear_xpath):
                # 这里必须定位至父节点删除子节点，不允许“自杀”
                del_element.getparent().remove(del_element)
            if tree.xpath(source_xpath):
                source = tree.xpath(source_xpath)[0] if source_xpath.split("/")[-1].startswith("@") else \
                    tree.xpath(source_xpath)[0].xpath('string(.)')
            else:
                source = ""
            source = re.sub(".*(来源)[:：]|(作者)[:：].*", "", re.sub("[\n\t\s\r ]", "", source)).strip()
            content, content_html = self.get_content(html_x, tree, "扫一扫，在手机打开当前页面")
            images = []
            imgs = tree.xpath(img_css)
            for img in imgs:
                relay_img = img.xpath(img_child_css)
                if relay_img:
                    if re.search("(data:image/gif|\.gif)", relay_img[0]) or not re.search("^http", relay_img[0]):
                        continue
                    images.append(url_join(entity_url, relay_img[0]))
            img_list = self.sava_img(images)
            # img_list = ""
            video = self.video_del(video_css, tree, entity_url)
            accessory = self.get_files(accessory_css, tree, entity_url, "pdf$")
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
                'module_name': items['module_name'],
                'module_url': items['module_url'],
                'ref_url': entity_url,
                'source_url': entity_url,
                'url_md5': get_md5(entity_url),
                'host': host,
                'sub_host': host.replace("www.", ''),
                'website_name': items['website_name'],  # 站点名称
                'article_type': 0,
                'language': items['language'],  # 语种
                'language_str': items['language_str'],
                'crawler_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),  # 采集时间
                'insert_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'update_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'images': img_list if img_list else '',
                'crawler_on': ip,
                "exists_typeset": 0,
            }
            if int(time.time()) - str_for_time(item.get('pubtime')) < 3600 * 24 * 5:
                self.send_data("topic_c1_original_keynewswebsites", item)
            self.redis_conn.sadd("key_news:pl", item['source_url'])
        except Exception:
            logger.error(f"实体页采集出错！{traceback.format_exc()}，详情链接：\n{entity_url}")

    def sava_img(self, images):
        end_result = []
        for img in images:
            responses = req_get(img, headers=self.headers, proxies=self.is_proxies)
            end_name = get_file_type(responses.content, img)
            file_name = f"topic_c1_original_keynewswebsite/{datetime.datetime.now().strftime('%Y-%m-%d').replace('-', '')}/{get_md5(img)}.{end_name}"
            res = self.hw_db.upload_file(file_name, responses.content)
            if res:
                logger.info("文件存储成功!")
                end_result.append(file_name)
        return end_result

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

