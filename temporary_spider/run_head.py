# -*- coding: utf-8 -*-
# @Time    : 2023/9/6 0006 16:49
# @Author  : Liu
# @Site    : 
# @File    : run_head.py
# @Software: PyCharm
from kafka import KafkaProducer
from tools.mini_down import MiniDown
from header_spider.header_spider import HeadSpider

if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['172.22.100.90:9092'])
    hw_obs = MiniDown()
    proxies = {
        'http': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@9662f10ce723ec40.na.ipidea.online:2333',
        'https': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@9662f10ce723ec40.na.ipidea.online:2333'
    }
    mp = HeadSpider(is_proxies=proxies, hw_db=hw_obs, kafka_pro=producer)
    mp.id_split()
