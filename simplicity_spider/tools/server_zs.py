# -*- coding = utf-8 -*-
# @Time : 2021/9/29 8:25
# @Author : 邓星晨
# @File : server.py
# @Software : PyCharm
from loguru import logger
from requests import request
from retrying import retry
import traceback
import json

SERVER_API_URL = 'http://122.9.143.60:3303'

headers = {
    'content-type': 'application/json'
}


def extract_key(data):
    data_keys = ','.join(list(data.keys()))
    vale = '%s,' * len(data.keys())
    return data_keys, vale[:-1]


def retry_error(exception):
    print(exception)
    return isinstance(exception, Exception)


@retry(retry_on_exception=retry_error, stop_max_attempt_number=3, wait_fixed=500)
def add_sql_server(params):
    url = SERVER_API_URL + '/addDataToMysql'
    keys, vale = extract_key(params[0])
    params = [tuple(param.values()) for param in params]
    from_data = {
        "keys": keys,
        "values": vale,
        "params": params
    }
    try:
        r = request('POST', url, json=from_data, timeout=15)
        logger.debug(f'服务器SQL添加结果：{r.json()}')
    except Exception as e:
        print(traceback.format_exc())



