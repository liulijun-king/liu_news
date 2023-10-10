# -*- coding: utf-8 -*-
# @Time    : 2023/2/16 0016 14:50
# @Author  : Liu
# @Site    : 
# @File    : db_config.py
# @Software: PyCharm
local_db = {
    'host': '127.0.0.1',
    'user': 'root',
    'port': 3306,
    'password': '123456',
    'database': 'image',
    'charset': 'utf8',
}
formal_db = {
    'host': '10.99.100.40',
    'user': 'wg_dba',
    'port': 3306,
    'password': 'wgdb%2017',
    'database': 'wg_platform_kb',
    'charset': 'utf8mb4',
}
proxies = {
    'http': '127.0.0.1:7890',
    'https': '127.0.0.1:7890'
}

