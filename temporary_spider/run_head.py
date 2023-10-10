# -*- coding: utf-8 -*-
# @Time    : 2023/9/6 0006 16:49
# @Author  : Liu
# @Site    : 
# @File    : run_head.py
# @Software: PyCharm
from kafka import KafkaProducer
from tools.hw_obs import HwObs
from header_spider.header_spider import HeadSpider

if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['140.210.203.161:9092', '140.210.219.168:9092', '140.210.207.185:9092'])
    hw_obs = HwObs()
    proxies = {
        "http": "127.0.0.1:7890",
        "https": "127.0.0.1:7890"
    }
    mp = HeadSpider(is_proxies=proxies, hw_db=hw_obs, kafka_pro=producer)
    mp.id_split()
