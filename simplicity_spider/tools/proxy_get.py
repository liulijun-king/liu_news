# -*- coding: utf-8 -*-
# @Time    : 2023/7/6 0006 11:47
# @Author  : Liu
# @Site    : 
# @File    : proxy_get.py
# @Software: PyCharm
import json
import queue

import requests

queue = queue.Queue()


def proxy_pool() -> list:
    """
    使用境外动态代理
    :return: 代理列表
    """
    proxy_url = 'http://api.proxy.ipidea.io/getProxyIp?num=100&return_type=json&lb=6&sb=0&flow=1&regions=&protocol=http'
    # proxy_url = 'http://220.194.140.39:30022/getip?num=150&ip=&key=&source=zhima'
    proxy_con = requests.get(proxy_url).text
    proxy_json = json.loads(proxy_con)
    proxy_text = [(proxy["ip"] + ':' + str(proxy["port"])) for proxy in proxy_json["data"]]
    return proxy_text


def queue_empty():
    while True:
        if queue.empty():
            proxy_list = proxy_pool()
            for i in proxy_list:
                queue.put(i)
        pro = queue.get()
        if pro:
            if "http" not in pro:
                pro = "http://" + pro
            break
    proxies = str(pro)
    return proxies
