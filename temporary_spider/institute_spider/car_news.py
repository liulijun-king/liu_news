# -*- coding: utf-8 -*-
# @Time    : 2023/6/12 0012 10:02
# @Author  : Liu
# @Site    : 
# @File    : car_news.py
# @Software: PyCharm
import json
import os
import re
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import urljoin

import jsonpath
from loguru import logger
from lxml import etree

from base_spider import Base_spider
from tools.base_tools import content_conversion
from tools.base_tools import req_get, time_parse, get_md5
from tools.push_service import all_push_server


class CarSpider(Base_spider):
    def __init__(self, is_proxies=None):
        super(CarSpider, self).__init__(is_proxies=is_proxies)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        self.base_root = re.sub(r"/[^/]+$", "", os.getcwd().replace("\\", "/"))
        self.log = logger.add(f'{self.base_root}/log/{self.__class__.__name__}.log')
        self.module = json.load(open(f'{self.base_root}/setting/institute_config.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.entity_rule = json.load(open(f'{self.base_root}/setting/entity_spider.json', 'r', encoding="utf-8"))
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
        for _ in range(start_page, max_page):
            self.list_spider(_ * page_size, url)

    def list_spider(self, page, url):
        try:
            url = url.format(str(page))
            logger.info(f"当前采集链接：{url}，页码：{page}")
            response = req_get(url, headers=self.headers, proxies=self.is_proxies)
            if self.config.get("char"):
                html = etree.HTML(response.content.decode(self.config.get("char")))
            else:
                html = etree.HTML(response.content.decode())
            lis = html.xpath(self.config.get("lis_xpath"))
            for li in lis:
                entity_url = urljoin(url, li).strip()
                self.entity_split(entity_url)
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def entity_split(self, url):
        logger.info(f"实体页链接：{url}")
        try:
            responses = req_get(url, headers=self.headers, proxies=False)
            entity_json = re.search("(?<=window.__PRELOADED_STATE__ =).*?(?=}};)", responses.content.decode()).group()
            entity_json = json.loads(entity_json + "}}")
            lis = jsonpath.jsonpath(
                entity_json, "$.cms.content.research/car-news/index-redesign.childEntries[*]..contentMetadata.link-url")
            for li in lis:
                if "car-news" in li:
                    entity_url = urljoin(url, li).strip()
                    self.entity_spider(entity_url)
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def video_del(self, the_xpath, tree, entity_url):
        v_id = tree.xpath(the_xpath)
        video_list = []
        if v_id:
            v_url = f"https://www.youtube.com/embed/{v_id[0].replace('vid_', '')}?rel=0&enablejsapi=1&origin=https%3A%2F%2Fwww.edmunds.com&widgetid=1"
            video_list.append(v_url)
        return video_list

    def get_content(self, the_xpath, tree, error_str):
        html = tree.xpath(the_xpath)
        content_lis = []
        if html:
            html = content_conversion(html)
            html = etree.HTML(html)
            for p in html.xpath('//p'):
                if re.search(error_str, p.xpath("string(.)")):
                    continue
                p_str = p.xpath('string(.)')
                content_lis.append(p_str)
        content = "\n".join(content_lis)
        content = re.sub("\n{2,20}", "\n", content)
        content = re.sub("\t{2,20}", "\t", content)
        content = re.sub("\r{2,20}", "\r", content)
        content = re.sub("[\n\t\r ]{2,20}", "\n", content)
        if content:
            content_html = etree.tostring(html, encoding="utf-8").decode('utf-8')
            content_html = re.sub("\n{2,20}", "\n", content_html)
            content_html = re.sub("\t{2,20}", "\t", content_html)
            content_html = re.sub("\r{2,20}", "\r", content_html)
            content_html = re.sub("[\n\t\r ]{2,20}", "\n", content_html)
        else:
            content_html = ""
        return content, content_html

    def entity_spider(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            module = re.sub("-.*", "", self.config['module_name'])
            entity_rule = self.entity_rule.get(module)
            title_xpath = entity_rule['title_xpath']
            author_xpath = entity_rule['author_xpath']
            pubtime_css = entity_rule['pubtime_css']
            abstract_xpath = entity_rule['abstract_xpath']
            source_xpath = entity_rule['source_xpath']
            html_x = entity_rule['html_x']
            clear_xpath = "//script|//style"
            img_css = entity_rule['img_css']
            video_css = entity_rule['video_css']
            img_child_css = "./@src|./@data-src"
            host = self.config['host']
            responses = req_get(entity_url, headers=self.headers, proxies=False)
            tree = etree.HTML(responses.content.decode("utf-8", 'ignore'))
            title = tree.xpath(title_xpath)[0].xpath('string(.)') if tree.xpath(title_xpath) else tree.xpath("//title")[
                0].xpath('string(.)')
            author = tree.xpath(author_xpath)[0].xpath('string(.)') if tree.xpath(author_xpath) else ""
            try:
                pubtime = tree.xpath(pubtime_css)[0].xpath('string(.)') if tree.xpath(pubtime_css) else ""
            except Exception:
                pubtime = tree.xpath(pubtime_css)[0]
            pubtime = re.sub("(.*(发布时间|日期|时间)\s{0,4}[:：]|来源[:：].*|空格|人民日报|星期.*)", "",
                             re.sub("\n|\r|\t", "", pubtime).strip()).strip()
            abstract = tree.xpath(abstract_xpath)[0].xpath('string(.)') if tree.xpath(abstract_xpath) else ""
            html = tree.xpath(html_x)[0]
            for del_element in html.xpath(clear_xpath):
                # 这里必须定位至父节点删除子节点，不允许“自杀”
                del_element.getparent().remove(del_element)
            source = tree.xpath(source_xpath)[0].xpath('string(.)') if tree.xpath(source_xpath) else ""
            source = re.sub(".*(来源)[:：]", "", re.sub("[\n\t\s\r ]", "", source)).strip()
            content, content_html = self.get_content(html_x, html, "扫一扫，在手机打开当前页面")
            video = self.video_del(video_css, tree, entity_url)
            images = []
            imgs = tree.xpath(img_css)
            for img in imgs:
                relay_img = img.xpath(img_child_css)
                if relay_img:
                    images.append(urljoin(entity_url, relay_img[0]))
            item = {
                'title': title.strip(),  # 标题
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
                'url_md5': get_md5(entity_url+"1"),
                'uuid': get_md5(entity_url+"1"),
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
                "region": 1,
                "S": "zicai",
            }
            logger.info(f"url_md5:{item['url_md5']}")
            self.export.append(item)
            if len(self.export) >= 10:
                all_push_server(self.export, "major_info")
                self.export.clear()
        except Exception:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")


if __name__ == '__main__':
    mp = CarSpider()
    mp.id_split()
