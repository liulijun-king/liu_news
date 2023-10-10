# -*- coding: utf-8 -*-
# @Time    : 2023/9/21 0021 14:12
# @Author  : Liu
# @Site    : 
# @File    : run_hot.py
# @Software: PyCharm
from kafka import KafkaProducer

from header_spider.hot_web import HotWeb

if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['140.210.203.161:9092', '140.210.219.168:9092', '140.210.207.185:9092'])
    proxies = {
        "http": "127.0.0.1:7890",
        "https": "127.0.0.1:7890"
    }
    mp = HotWeb(is_proxies=proxies, kafka_pro=producer)
    mp.id_split()