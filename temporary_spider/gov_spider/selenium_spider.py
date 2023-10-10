# -*- coding: utf-8 -*-
# @Time    : 2023/7/17 0017 10:03
# @Author  : Liu
# @Site    : 
# @File    : selenium_spider.py
# @Software: PyCharm

import json
import os
import re
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import urljoin

from loguru import logger
from lxml import etree
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from base_spider import Base_spider
from tools.base_tools import req_get, time_parse, get_md5, wen_hai_parser_server
from tools.push_service import all_push_server


class SeleniumSpider(Base_spider):
    def __init__(self, is_proxies=None):
        super(SeleniumSpider, self).__init__(is_proxies=is_proxies)
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
        self.log = logger.add(f'{self.base_root}/log/{self.__class__.__name__}.log')
        self.module = json.load(open(f'{self.base_root}/setting/config.json', 'r', encoding="utf-8")).get(
            self.__class__.__name__)
        self.entity_rule = json.load(open(f'{self.base_root}/setting/entity_spider.json', 'r', encoding="utf-8"))
        self.host_rule = json.load(open(f'{self.base_root}/setting/host_xpath.json', 'r', encoding="utf-8"))
        self.config = None
        self.export = []
        self.is_break = False

    def selnium_content(self, url):
        option = Options()
        option.add_argument("--incognito")  # 配置隐私模式
        option.add_argument('--headless')  # 配置无界面
        driver = webdriver.Firefox(executable_path=f"{self.base_root}/gov_spider/geckodriver.exe", options=option)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get(url)
        time.sleep(5)
        content = driver.page_source
        driver.quit()
        return content

    def id_split(self):
        data_dict = self.module
        for key, value in data_dict.items():
            if "国家税务总局陕西省税务局" in value['module_name']:
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
        if not re.search("\{\}", url):
            max_page = 2
        for _ in range(start_page, max_page):
            if self.is_break:
                self.is_break = False
                break
            self.list_spider(_ * page_size, url)

    def list_spider(self, page, url):
        try:
            if self.config['split_module'] == "_{}" and self.config['start_page'] == 1 and page == 1:
                url = url.replace("_{}", "")
            elif self.config['split_module'] == "_{}" and self.config['start_page'] == 0 and page == 0:
                url = url.replace("_{}", "")
            elif self.config['split_module'] == "index{}" and self.config['start_page'] == 0 and page == 0:
                url = url.replace("{}", "")
            elif self.config['split_module'] == "index{}" and self.config['start_page'] == 1 and page == 1:
                url = url.replace("{}", "")
            else:
                url = url.format(str(page))
            logger.info(f"当前采集链接：{url}，页码：{page}")
            response = self.selnium_content(url)
            html = etree.HTML(response)
            lis = html.xpath(self.config.get("lis_xpath"))
            if len(lis) == 0 and page > 50:
                self.is_break = True
            for li in lis:
                entity_url = urljoin(url, li)
                self.entity_spider(entity_url)
                # print(entity_url)
            if len(self.export) > 0:
                # print(json.dumps(self.export, ensure_ascii=False, indent=4))
                all_push_server(self.export, "major_info")
                self.export.clear()
        except Exception as e:
            logger.error(f"列表页请求失败！{e}")

    def entity_spider(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            module = re.sub("-.*", "", self.config['module_name'])
            url_host = re.search("(?<=://).*?(?=/)", entity_url).group()
            url_host = url_host.replace("www.", "")
            if self.host_rule.get(url_host):
                entity_rule = self.host_rule.get(url_host)
            else:
                entity_rule = self.entity_rule.get(module)
            title_xpath = entity_rule['title_xpath']
            author_xpath = entity_rule['author_xpath']
            pubtime_css = entity_rule['pubtime_css']
            abstract_xpath = entity_rule['abstract_xpath']
            source_xpath = entity_rule['source_xpath']
            html_x = entity_rule['html_x']
            clear_xpath = "//div[@id='main']/div[@class='ewm']|//script|//style|//div[@id='pagefoot']|//div[@class='footer']|//div[@id='articleEwm']|//div[@class='foot_middle']|//div[@class='ewmFont']"
            img_css = entity_rule['img_css']
            video_css = entity_rule['video_css']
            img_child_css = "./@src|./@data-src"
            host = self.config['host']
            if re.search(r"(hunan.chinatax.gov.cn|yunnan.chinatax.gov.cn|shaanxi.chinatax.gov.cn)", entity_url):
                responses = self.selnium_content(entity_url)
                tree = etree.HTML(responses)
            else:
                responses = req_get(entity_url, headers=self.headers, proxies=False)
                tree = etree.HTML(responses.content.decode())
            title = tree.xpath(title_xpath)[0].xpath('string(.)') if tree.xpath(title_xpath) else tree.xpath("//title")[
                0].xpath('string(.)')
            author = tree.xpath(author_xpath)[0].xpath('string(.)') if tree.xpath(author_xpath) else ""
            try:
                pubtime = tree.xpath(pubtime_css)[0].xpath('string(.)') if tree.xpath(pubtime_css) else ""
            except Exception:
                pubtime = tree.xpath(pubtime_css)[0]
            pubtime = re.sub("(.*(发布时间|日期|时间)\s{0,4}[:：]|来源[:：].*|空格|人民日报|星期.*)", "",
                             re.sub("\n|\r|\t", "", pubtime).strip()).strip()
            if "weixin" in entity_url:
                pubtime = re.search("(?<=getXmlValue\('ct'\) : ').*?(?=' \|\| ')|(?<=ct = \").*?(?=\";)",
                                    responses.content.decode()).group()
            abstract = tree.xpath(abstract_xpath)[0].xpath('string(.)') if tree.xpath(abstract_xpath) else ""
            html = tree.xpath(html_x)[0]
            for del_element in html.xpath(clear_xpath):
                # 这里必须定位至父节点删除子节点，不允许“自杀”
                del_element.getparent().remove(del_element)
            source = tree.xpath(source_xpath)[0].xpath('string(.)') if tree.xpath(source_xpath) else ""
            source = re.sub(".*(来源)[:：]", "", re.sub("[\n\t\s\r ]", "", source)).strip()
            content, content_html = self.get_content(html_x, html, "扫一扫，在手机打开当前页面")
            if "mp.weixin.qq.com" in entity_url:
                videos = re.findall("(?<=url: ').*?(?=',)", responses.content.decode())
                dup_lis = []
                video = []
                for v in videos:
                    dup_li = re.sub("mp4.*", "", v)
                    if dup_li not in dup_lis and v.startswith("http"):
                        dup_lis.append(dup_li)
                        video.append(v.replace("\\x26amp;", "&"))
            else:
                video = self.video_del(video_css, tree, entity_url)
            images = []
            imgs = tree.xpath(img_css)
            for img in imgs:
                relay_img = img.xpath(img_child_css)[0]
                if relay_img:
                    images.append(urljoin(entity_url, relay_img))
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
                'ref_url': entity_url,
                'source_url': entity_url,
                'url_md5': get_md5(entity_url),
                'uuid': get_md5(entity_url),
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
            self.export.append(item)
        except Exception:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")

    def get_event(self, entity_url):
        try:
            logger.info(f"实体页链接：{entity_url}")
            responses = req_get(entity_url, headers=self.headers, proxies=self.is_proxies)
            item = wen_hai_parser_server(entity_url, responses.text)
            return item
        except Exception:
            logger.error(f"实体页采集出错！{traceback.format_exc()}")
            return {}


if __name__ == '__main__':
    mp = SeleniumSpider()
    mp.id_split()
