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
    proxies = {
        'http': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333',
        'https': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333'
    }

    proxy_con = requests.get('http://ipinfo.ipidea.io', proxies=proxies)
    # proxy_url = 'http://api.proxy.ipidea.io/getProxyIp?num=100&return_type=json&lb=6&sb=0&flow=1&regions=&protocol=http'
    # proxy_url = 'http://220.194.140.39:30022/getip?num=150&ip=&key=&source=zhima'
    proxy_json = proxy_con.json()
    proxy_text = []
    for i in range(15):
        pro = f'{proxy_json["ip"]}:2333'
        proxy_text.append(pro)
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
