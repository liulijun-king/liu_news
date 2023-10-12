# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from loguru import logger

from GitHubAll.settings import is_put_data, user_url_key, day_crawl_key, redis_conn
from sql_alchemy.crud import create_post_data
from tools.bloom_filter import add
from tools.common_tools import json_print
from tools.push_kafka import all_push_server


class GithuballPipeline:

    def __init__(self):
        # 数据库表名
        self.project_table = "topic_c1_original_github_projectinformation"
        self.fork_table = "git_hub_forks_relation"
        self.user_table = "topic_c1_original_github_basicuserinformation"

    def process_item(self, item, spider):
        json_print(item)
        if spider.name == "github_main":
            logger.info("正在处理项目信息表")
            # 存入redis
            # redis_item = {
            #     "uuid": item["uuid"],
            #     "project_url": item["source_url"],
            # }
            # item_byte = json.dumps(redis_item, ensure_ascii=False).encode("utf-8")
            # self.redis_conn.lpush(item_info_key, item_byte)

            # 存入布隆过滤器；存入日采集量；添加用户信息采集；推送入库
            if is_put_data:
                project_id = item["ref_url"].replace("https://api.github.com/repositories/", "")
                add(project_id)
                redis_conn.lpush(day_crawl_key, project_id)
                redis_conn.lpush(user_url_key, f'https://github.com/{item["author"]}')
                all_push_server([item], self.project_table)

        elif spider.name == "github_forks":
            logger.info("正在处理forks用户关系表")
            redis_conn.lpush(user_url_key, item["user_url"])
            # 入库
            if is_put_data:
                create_post_data(table_name=self.fork_table,
                                 data=item,
                                 filters={
                                     "uuid": item.get("uuid")
                                 })

        elif spider.name == "github_userinfo":
            logger.info("正在处理用户信息表")
            # 入库
            if is_put_data:
                all_push_server([item], self.user_table)
        return item
