# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 0017 10:33
# @Author  : Liu
# @Site    : 
# @File    : base_spider.py
# @Software: PyCharm
import re
from urllib import parse

import loguru
from lxml import etree

from tools.base_tools import content_conversion


class Base_spider(object):
    def __init__(self, is_proxies=None, headers=None):
        self.headers = headers
        self.is_proxies = is_proxies

    @staticmethod
    def video_del(the_xpath, tree, entity_url):
        """
        视频采集
        :param the_xpath:
        :param tree:
        :param entity_url:
        :return:
        """
        video_li = []
        video_tree = tree.xpath(the_xpath)
        for file in video_tree:
            if file.xpath("./@video|./@href|./@src|./@content|./@data-video"):
                url = re.sub(r"[\n\r\t]", '', file.xpath("./@video|./@href|./@src|./@content|./@data-video")[0])
                url = re.sub(r"f=http", 'http', url)
                new_file = parse.urljoin(entity_url, url)
                video_li.append(new_file)
        return video_li

    @staticmethod
    def get_string(the_xpath, tree):
        result = tree.xpath(the_xpath)
        if result and the_xpath.split("/")[-1].startswith("@"):
            result = result[0].strip()
        elif result:
            result = result[0].xpath('string(.)').strip()
        else:
            result = ''
        return result

    def time_clear(self, this_time, normal_rule):
        this_time = re.sub(normal_rule, '', this_time)
        return this_time

    @staticmethod
    def time_search(this_time, normal_rule):
        new_time = re.search(normal_rule, this_time)
        if new_time:
            return new_time.group()
        else:
            return this_time

    @staticmethod
    def get_image(the_xpath, tree, entity_url):
        images = []
        img_child_css = "./@src|./@srcset|./@data-srcset|./@data-src|./@href"
        imgs = tree.xpath(the_xpath)
        for img in imgs:
            relay_img = img.xpath(img_child_css)[0]
            if relay_img.endswith("gif"):
                continue
            if relay_img and not re.search(r"(ejweb.*?\.png)", relay_img):
                images.append(parse.urljoin(entity_url, relay_img))
        return images

    @staticmethod
    def get_files(the_xpath, tree, entity_url, file_end=None):
        files = []
        files_tree = tree.xpath(the_xpath)
        for file in files_tree:
            if file.xpath("./@href"):
                url = re.sub(r"[\n\r\t]", '', file.xpath('./@href')[0])
                new_file = parse.urljoin(entity_url, url)
                if not file_end:
                    files.append(new_file)
                else:
                    if re.search(file_end, new_file):
                        files.append(new_file)
        return files

    @staticmethod
    def get_content(the_xpath, tree, error_str):
        html = tree.xpath(the_xpath)
        content_lis = []
        if html is not None:
            if the_xpath.endswith("/p"):
                htmls = []
                for p in tree.xpath(the_xpath):
                    if re.search(error_str, p.xpath("string(.)")):
                        continue
                    p_str = p.xpath('string(.)')
                    content_lis.append(p_str)
                    htmls.append(f"<p>{p_str}</p>")
                html = etree.HTML("\n".join(htmls))
            else:
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

    def __del__(self):
        loguru.logger.stop()
