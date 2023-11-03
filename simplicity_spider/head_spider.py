# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 0031 15:21
# @Author  : Liu
# @Site    : 
# @File    : head_spider.py
# @Software: PyCharm
from spider.Fr import Fr
from spider.td import Td
from spider.nytime import NyTime
from spider.bcb import Bcb
from kafka import KafkaProducer
from tools.hw_obs import HwObs

if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['8.130.131.161:9092', '8.130.94.243:9092', '8.130.37.191:9092'])
    hw_obs = HwObs()
    is_proxies = {
        'http': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@9662f10ce723ec40.na.ipidea.online:2333',
        'https': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@9662f10ce723ec40.na.ipidea.online:2333'
    }
    Fr(hw_db=hw_obs, kafka_pro=producer, is_proxies=is_proxies).id_split()
    Td(hw_db=hw_obs, kafka_pro=producer, is_proxies=is_proxies).id_split()
    Bcb(hw_db=hw_obs, kafka_pro=producer, is_proxies=is_proxies).id_split()
    NyTime(hw_db=hw_obs, kafka_pro=producer, is_proxies=is_proxies).id_split()
