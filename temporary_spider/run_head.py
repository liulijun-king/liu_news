# -*- coding: utf-8 -*-
# @Time    : 2023/9/6 0006 16:49
# @Author  : Liu
# @Site    : 
# @File    : run_head.py
# @Software: PyCharm
import time

from kafka import KafkaProducer
from rediscluster import RedisCluster
import json
from header_spider.header_spider import HeadSpider
from tools.mini_down import MiniDown

if __name__ == '__main__':
    startup_nodes = [
        {"host": "47.97.216.52", "port": 6379},
        {"host": "120.55.67.165", "port": 6379},
        {"host": "120.26.85.177", "port": 6379}
    ]
    # 创建 Redis 集群连接
    redis_conn = RedisCluster(
        startup_nodes=startup_nodes,
        decode_responses=True, socket_connect_timeout=30, password='gew29YAyi'
    )
    print(redis_conn.sismember("key_news:pl", "https://www.rfi.fr/fr/afrique/20230111-en-visite-au-burkina-faso-sissoco-embalo-r%C3%A9affirme-le-soutien-de-la-c%C3%A9d%C3%A9ao"))
    print(redis_conn.sismember("key_news:pl", "https://cn.wsj.com/articles/报道-私募股权投资公司thoma-bravo考虑收购twitter-11649979906"))
    # producer = KafkaProducer(
    #     bootstrap_servers=['172.22.100.90:9092'])
    # hw_obs = MiniDown()
    # # http://shengmingxing_zxcj-zone-custom:wzcj_2023@679e234e86e0ed04.na.ipidea.online:2333
    # # "http://f2199815664-region-SG-period-0:k0sl96zx@as.r618.kdlfps.com:18866/"
    # proxies = {
    #     'http': "http://f2199815664-region-SG-period-0:k0sl96zx@as.r618.kdlfps.com:18866/",
    #     'https': "http://f2199815664-region-SG-period-0:k0sl96zx@as.r618.kdlfps.com:18866/"
    # }
    # mp = HeadSpider(is_proxies=proxies, hw_db=hw_obs, kafka_pro=producer, redis_conn=redis_conn)
    # # mp.id_split()
    # mp.id_split_thread()


