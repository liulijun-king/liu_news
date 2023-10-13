import json
from datetime import datetime

import scrapy
from loguru import logger

from config.item_config import *
from tools.common_tools import json_path, md5
from tools.proxies import queue_empty
from rediscluster import RedisCluster


class GithubForksSpider(scrapy.Spider):
    name = 'github_forks'
    allowed_domains = ['github.com']

    headers = {
        'authority': 'github.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'
    }

    config = json.load(open('./config/github_forks.json', 'r', encoding="utf-8"))
    # redis配置
    redis_key = "github_all:item_info_handle"
    startup_nodes = [
        {"host": "47.97.216.52", "port": 6379},
        {"host": "120.55.67.165", "port": 6379},
        {"host": "120.26.85.177", "port": 6379}
    ]
    # 创建 Redis 集群连接
    redis_conn = RedisCluster(
        startup_nodes=startup_nodes,
        decode_responses=True, socket_connect_timeout=30, password='gew29YAyi'
    )

    def start_requests(self):
        while True:
            if self.redis_conn.llen(self.redis_key) <= 100:
                break
            pipeline = self.redis_conn.pipeline()
            for _ in range(10000):
                pipeline.rpop(self.redis_key)
            item_list = pipeline.execute()

            for _ in item_list:
                if _:
                    item_info = eval(_.decode("utf-8"))
                    item_url = item_info.get("project_url")

                    commit_url = f"{item_url}/network/members"
                    yield scrapy.Request(url=commit_url,
                                         headers=self.headers,
                                         callback=self.parse,
                                         meta={
                                             "item": item_info
                                             # "proxy": queue_empty()
                                         })

    def parse(self, response, **kwargs):
        project_item = response.meta["item"]
        logger.info(f"正在解析forks页 | {response.url}")
        try:
            for commit_html in response.xpath(json_path(self.config, '$.forks_info.li_xpath')):
                item = forks_relation().copy()
                # 项目id
                item["project_id"] = json_path(project_item, '$.project_id')
                # 用户名
                item["user_name"] = commit_html.xpath(json_path(self.config, '$.forks_info.user_name')).get("")
                # 用户头像
                user_head = commit_html.xpath(json_path(self.config, '$.forks_info.user_head')).get("")
                item["head_img"] = response.urljoin(user_head)
                # 用户链接
                user_url = commit_html.xpath(json_path(self.config, '$.forks_info.user_url')).get("")
                item["user_url"] = response.urljoin(user_url)
                # 用户链接的md5
                item["user_id"] = md5(item["user_url"])
                # 子项目名
                item["sub_project_name"] = commit_html.xpath(
                    json_path(self.config, '$.forks_info.sub_project_name')).get("")
                # 子项目链接
                user_url = commit_html.xpath(json_path(self.config, '$.forks_info.sub_project_url')).get("")
                item["sub_project_url"] = response.urljoin(user_url)
                # 基本信息
                item["source_url"] = response.url
                item["uuid"] = md5(item["project_id"] + item["user_url"])
                item['crawler_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if item["user_name"] and item["user_url"]:
                    yield item
                else:
                    logger.error(f"实体页没有匹配到内容 | {response.url}")

        except(Exception,) as e:
            logger.error(f"提交信息页解析错误！ | {response.url} | {str(e)}")
