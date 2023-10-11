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
        bootstrap_servers=['8.130.131.161:9092', '8.130.94.243:9092', '8.130.37.191:9092'])
    proxies = None
    mp = HotWeb(is_proxies=proxies, kafka_pro=producer)
    mp.id_split()
