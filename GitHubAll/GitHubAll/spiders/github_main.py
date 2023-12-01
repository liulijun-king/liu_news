#  开发时间：2022/5/11 10:51
#  文件名称：github_main.py
#  备注：全量采集 apiCode 10030007
from datetime import datetime
from urllib.parse import urlparse

import dateparser
import scrapy
from loguru import logger

from GitHubAll.settings import id_key, day_crawl_key, redis_conn
from config.item_config import item_main
from tools.common_tools import json_path, md5
from tools.proxies import queue_empty


class GithubMainSpider(scrapy.Spider):
    name = 'github_main'
    allowed_domains = ['github.com', 'api.github.com']
    # 采集接口（示例）
    url_interfaces = ["https://api.github.com/repositories/70318556"]

    headers = {
        'authority': 'api.github.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        while True:
            if redis_conn.llen(id_key) <= 100 or redis_conn.llen(day_crawl_key) > 50000:
                break
            pipeline = redis_conn.pipeline()
            for _ in range(10000):
                pipeline.rpop(id_key)
            id_list = pipeline.execute()

            for _ in id_list:
                if _:
                    try:
                        url = f"https://api.github.com/repositories/{_}"
                        yield scrapy.Request(url=url,
                                             headers=self.headers,
                                             callback=self.json_parse
                                             , meta={
                                "proxy": queue_empty()
                            }
                                             )
                    except(Exception,):
                        continue

    def json_parse(self, response):
        """
        从json接口中获取项目信息
        :param response:
        :return:
        """
        logger.info(f"正在解析接口页：{response.url}")
        try:
            item = item_main().copy()
            # fork的原项目ID
            item["fork_original_project"] = json_path(response.json(), '$.parent.full_name')
            # fork的根项目ID
            item["fork_root_project"] = json_path(response.json(), '$.source.full_name')
            # 项目名
            item["project_name"] = json_path(response.json(), '$.name')
            # 创建时间
            create_time = json_path(response.json(), '$.created_at')
            if create_time:
                item["create_time"] = dateparser.parse(create_time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                logger.error(f"该文章无发布时间！ | 接口url：{response.url}")
            # 项目作者
            author = json_path(response.json(), '$.owner.login')
            item["author"] = author
            item["user_id"] = author
            # 项目标签
            tags = json_path(response.json(), '$.topics')
            item["tags"] = "#".join(tags)
            # 项目星数
            stars_count = json_path(response.json(), '$.stargazers_count')
            item["stars_count"] = str(stars_count)
            # 项目浏览数
            watch_count = json_path(response.json(), '$.subscribers_count')
            item["watch_count"] = str(watch_count)
            # 项目fork数
            forks_count = json_path(response.json(), '$.forks_count')
            item["forks_count"] = str(forks_count)
            # 项目简介
            item["abstract"] = json_path(response.json(), '$.description')
            # 项目id
            project_id = json_path(response.json(), '$.id')
            # 项目url
            source_url = json_path(response.json(), '$.html_url')

            yield scrapy.Request(url=source_url,
                                 headers=self.headers,
                                 callback=self.parse,
                                 meta={
                                     "item": item,
                                     "project_id": project_id
                                     , "proxy": queue_empty()
                                 })

        except(Exception,) as e:
            logger.error(f"接口页解析错误！ | {response.url} | {str(e)}")

    def parse(self, response, **kwargs):
        """
        从html中获取项目信息
        :param response:
        :return:
        """
        logger.info(f"正在解析实体页：{response.url}")
        item = response.meta["item"]
        project_id = response.meta["project_id"]
        try:
            # 项目提交次数
            item["commit_count"] = response.xpath("//span[@class='d-none d-sm-inline']/strong/text()").get('').replace(
                ",", "")
            # 项目贡献数
            contributors_count = response.xpath("//a[contains(text(), 'Contributors')]/span/text()").get('').replace(
                ",", "")
            item["contributors_count"] = contributors_count
            # 项目url
            item["source_url"] = response.url
            # 跳转url
            ref_url = f"https://api.github.com/repositories/{project_id}"
            item["ref_url"] = ref_url
            # 用ref_url MD5
            item["uuid"] = md5(ref_url)
            # read me内容
            item["readme"] = response.xpath("//div[@data-target='readme-toc.content']").xpath('string(.)').get("")
            # item["readme_html"] = response.xpath(json_path(config, "$.item_info.readme")).get("")
            # 基本信息
            item["website_name"] = 'GitHub'
            item["website_sub_name"] = 'GitHub'
            item["host"] = 'github.com'
            netloc = urlparse(response.url).netloc.replace('www.', '')
            if netloc:
                item["sub_host"] = netloc
            else:
                item["sub_host"] = item["host"]
            item['crawler_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if item["project_name"]:
                yield item
            else:
                logger.error(f"没有提取到有效信息！请检查页面 | {response.url}")
        except(Exception,) as e:
            logger.error(f"解析实体页错误！ | {response.url} | {str(e)}")
