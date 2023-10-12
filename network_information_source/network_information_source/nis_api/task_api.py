# -*- coding = utf-8 -*-
# @Time : 2022/8/4 10:04
# @File : task_api.py
# @Author : xingc
# @Desc :
from urllib.parse import urljoin
from typing import Union, Iterable, List, Tuple

import pymysql
import requests
from pymysql import OperationalError
from pymysql.cursors import DictCursor
from requests import Response, RequestException
from loguru import logger
from easy_spider_tool import jsonpath, current_date

# 正式和测试环境下，api地址、数据库连接的信息
BASE_URL = 'http://140.210.219.168:38080'
TEST_BASE_URL = 'https://test.gagatao.com'
DB_CONF = {
    'host': '140.210.219.168',
    'port': 33306,
    'user': 'root',
    'password': 'wg%2020',
    'database': 'wenhai_ctms'
}

TEST_DB_CONF = {
    'host': '140.210.219.168',
    'port': 33306,
    'user': 'root',
    'password': 'wg%2020',
    'database': 'wenhai_ctms'
}


class MaxRequestRetryCount(Exception):
    pass


class TaskServiceApi:
    def __init__(
            self,
            name: str,
            api_code: Union[int, str],
            access_token: str = None,
            cookie_fields: Union[List, Tuple] = None,
            retry_num: int = 3,
            debug: bool = False
    ):
        # 渠道名
        self.name = name
        # apiCode
        self.api_code = api_code
        # 获取cookie需要的字段
        self.cookie_fields = cookie_fields or ['*']
        # X-Access-Token
        self.access_token = access_token
        # 请求错误重试次数
        self.retry_num = retry_num

        if debug is False:
            self.base_url = BASE_URL
            db_conf = DB_CONF
        else:
            self.base_url = TEST_BASE_URL
            db_conf = TEST_DB_CONF
        self.db_conn = None
        try:
            self.db_conn = pymysql.connect(**db_conf, cursorclass=DictCursor)
        except OperationalError as e:
            pass

    def get_headers(self, use_token):
        header = {}
        if use_token is True:
            header['X-Access-Token'] = self.access_token
        return header

    def request(self, method: str, url_path: str, use_token: bool = True, **kwargs) -> Response:
        url = urljoin(self.base_url, url_path)
        headers = kwargs.pop('headers', {})
        headers.update(self.get_headers(use_token=use_token))
        retry_count = 0
        while self.retry_num >= retry_count:
            try:
                return requests.request(method, url, headers=headers, **kwargs)

            except RequestException as rex:
                logger.error(
                    f'request exception: {rex}' + f', kwargs: {kwargs}, next retry ...' if retry_count < self.retry_num else 'exit retry')
                retry_count += 1

        raise MaxRequestRetryCount(f'retry count: {retry_count}')

    def query_wait_tasks(
            self,
            collect_type_code: str = '',
            crawl_mode: str = '',
            region: str = None,
            task_level: str = '',
            task_name: str = '',
            page: int = 1,
            page_size: int = 10,
            data_path: str = '$..records[*]'
    ) -> Iterable:
        # 提取待执行任务
        url_path = '/wenhai-ctms-boot/api/collect/queryWaitingTaskList'
        total = 0

        while True:
            params = {
                'apiCode': self.api_code,
                'collectTypeCode': collect_type_code,
                'crawlMode': crawl_mode,
                'region': region,
                'taskLevel': task_level,
                'taskName': task_name,
                'pageNo': page,
                'pageSize': page_size
            }
            result = self.request(method='GET', url_path=url_path, params=params)
            result_json = result.json()
            records = jsonpath(result_json, data_path, default=[])
            if not records:
                logger.debug(f'no task, records result:{records}')
                return records

            yield records

            if page <= 1:
                total = jsonpath(result_json, '$.result.total', first=True, default=0)

            # 总待执行任务数小于page_size，不继续请求任务
            if all([
                page <= 1,
                total <= page_size
            ]):
                logger.debug(f'task total {total}')
                return
            page += 1

    def update_task_result(self, task_id: int, status: int, result_data):
        """更新任务类型"""
        url_path = '/wenhai-ctms-boot/api/collect/updateTaskResult'
        payload = {
            "apiCode": self.api_code,
            "resultData": result_data,
            "status": status,
            "taskId": task_id
        }
        result = self.request('POST', url_path=url_path, json=payload)
        return result

    def get_cookies(self) -> List:
        sql = f"select {','.join(self.cookie_fields)} from ctms_collect_account where account_type='{self.name}' and `status`=1"
        # 测试db连接是否中断
        self.db_conn.ping()
        with self.db_conn.cursor() as cursor:
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
            except Exception as e:
                result = []
                logger.error(f'cookie提取错误{e}')
        return result

    def update_cookie_state(self, state: int, value: str, unique_field: str = 'phone'):
        """
        渠道cookie状态更新, 唯一
        :param state: 状态(1-有效,2-失效,3-封禁,4-限制)
        :param value: 唯一字段的值
        :param unique_field: 记录的唯一字段名
        :return:
        """
        sql = f"update ctms_collect_account set `status`={state}, `update_time`='{current_date()}' where `account_type`='{self.name}' and `{unique_field}`='{value}'"
        # 测试db连接是否中断
        self.db_conn.ping()
        with self.db_conn.cursor() as cursor:
            try:
                cursor.execute(sql)
                self.db_conn.commit()
                logger.success(f'{unique_field}：{value} cookie状态更新成功')
            except Exception as e:
                self.db_conn.rollback()
                logger.error(f'{e} {sql}')

    def __del__(self):
        if self.db_conn:
            self.db_conn.close()
