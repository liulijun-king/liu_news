# -*- coding: utf-8 -*-
# @Time    : 2023/9/7 0007 14:46
# @Author  : Liu
# @Site    : 
# @File    : req_tools.py
# @Software: PyCharm

from curl_cffi import requests


def req_chrome_get(url, headers=None, proxies=None):
    responses = requests.get(url, headers=headers, impersonate="chrome101",
                             proxies=proxies, timeout=30)
    return responses


def req_chrome_post(url, headers=None, proxies=None, data=None):
    responses = requests.post(url, headers=headers, data=data, impersonate="chrome101",
                              proxies=proxies, timeout=30)
    return responses
