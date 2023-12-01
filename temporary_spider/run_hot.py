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
        bootstrap_servers=['172.22.100.90:9092'])
    # http://liulijun584268-zone-custom:9TL39WvUnboIdOI@9662f10ce723ec40.na.ipidea.online:2333
    proxies = {
        'http': "http://shengmingxing_zxcj-zone-custom:wzcj_2023@679e234e86e0ed04.na.ipidea.online:2333",
        'https': "http://shengmingxing_zxcj-zone-custom:wzcj_2023@679e234e86e0ed04.na.ipidea.online:2333"
    }
    mp = HotWeb(is_proxies=proxies, kafka_pro=producer)
    mp.id_split()
