# -*- coding: utf-8 -*-
# @Time    : 2023-11-22 14:39
# @Author  : Liu
# @Site    : 
# @File    : case_redis.py
# @Software: PyCharm

import sys

sys.path.append('../')
from rediscluster import RedisCluster
from GitHubAll.settings import user_url_key

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

print(redis_conn.llen(user_url_key))
