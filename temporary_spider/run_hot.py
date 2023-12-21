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
        'http': "http://f2199815664-region-SG-period-0:k0sl96zx@as.r618.kdlfps.com:18866/",
        'https': "http://f2199815664-region-SG-period-0:k0sl96zx@as.r618.kdlfps.com:18866/"
    }
    mp = HotWeb(is_proxies=proxies, kafka_pro=producer)
    mp.id_split()

# find /tmp -type f -size +1G -exec du -h {} +