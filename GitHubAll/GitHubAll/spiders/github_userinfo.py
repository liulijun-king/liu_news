import json
from datetime import datetime

import scrapy
from loguru import logger

from GitHubAll.settings import user_url_key, redis_conn
from config.item_config import user_info
from tools.common_tools import json_path, md5
from tools.proxies import queue_empty


class GithubUserinfoSpider(scrapy.Spider):
    name = 'github_userinfo'
    allowed_domains = ['github.com']

    headers = {
        'authority': 'github.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    }

    config = json.load(open('./config/github_user.json', 'r', encoding="utf-8"))

    def start_requests(self):
        while True:
            if redis_conn.llen(user_url_key) <= 100:
                break
            pipeline = redis_conn.pipeline()
            for _ in range(10000):
                pipeline.rpop(user_url_key)
            user_list = pipeline.execute()

            for _ in user_list:
                if _:
                    yield scrapy.Request(url=_,
                                         headers=self.headers,
                                         callback=self.parse,
                                         meta={
                                             "proxy": queue_empty()
                                         })

    def parse(self, response, **kwargs):
        logger.info(f"正在解析用户信息 | {response.url}")
        try:
            item = user_info().copy()
            # 用户id
            item["user_id"] = response.url.replace("https://github.com/", "")
            # 姓名
            user_name = response.xpath(json_path(self.config, '$.item_info.user_name')).get("").strip()
            if user_name:
                item["user_name"] = user_name
            else:
                item["user_name"] = response.xpath(json_path(self.config, '$.item_info.user_name2')).get("").strip()
            # 头像
            item["head_img"] = response.xpath(json_path(self.config, '$.item_info.head_img')).get("")
            # 粉丝数
            item["fans_count"] = response.xpath(json_path(self.config, '$.item_info.fans_count')).get("")
            # 关注量
            item["follow_count"] = response.xpath(json_path(self.config, '$.item_info.follow_count')).get("")
            # 简介
            item["abstract"] = response.xpath(json_path(self.config, '$.item_info.abstract')).xpath('string(.)').get("").strip()
            # 所在机构
            item["organization"] = "".join(response.xpath(json_path(self.config, '$.item_info.organization')).getall()).strip()
            # 所在地址
            item["address"] = "".join(response.xpath(json_path(self.config, '$.item_info.address')).getall()).strip()
            # 邮箱
            # item["email"] = response.xpath(json_path(config, '$.item_info.email')).get("").strip()
            # 个人主页url
            item["user_url"] = response.xpath(json_path(self.config, '$.item_info.user_url')).get("")
            # twitter url
            item["twitter_url"] = response.xpath(json_path(self.config, '$.item_info.twitter_url')).get("")
            # 星数
            item["stars_count"] = response.xpath(json_path(self.config, '$.item_info.stars_count')).get("")
            # 文章URL
            item['source_url'] = response.url
            # source_url的MD5加密
            item['uuid'] = md5(item['source_url'])

            item['crawler_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if item["user_id"]:
                yield item
            else:
                logger.error(f"实体页没有匹配到有效内容 | {response.url}")
                redis_conn.srem(user_url_key, response.url)

        except(Exception,) as e:
            logger.error(f"用户信息页解析错误！ | {response.url} | {str(e)}")
