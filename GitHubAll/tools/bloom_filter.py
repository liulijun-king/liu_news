# -*- coding: utf-8 -*-
#  开发时间：2023/1/31 16:19
#  文件名称：bloom_filter.py
#  文件作者：陈梦妮
#  备注：布隆过滤器
import hashlib
import redis
from larkspur import ScalableBloomFilter

# from redis.cluster import RedisCluster
# from redis.cluster import ClusterNode

# startup_nodes = [
#     ClusterNode("47.97.216.52", 6379),
#     ClusterNode("120.55.67.165", 6379),
#     ClusterNode("120.26.85.177", 6379),
# ]
# redis_conn = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, password='gew29YAyi')
redis_conn = redis.StrictRedis(host='47.97.216.52', port=6379, db=0, socket_connect_timeout=15, decode_responses=False,
                               password='gew29YAyi')
sbf = ScalableBloomFilter(connection=redis_conn,
                          name='bloom_filter',
                          initial_capacity=100000000,
                          error_rate=0.0001)


def add(bl_str) -> bool:
    if isinstance(bl_str, list):
        add_many([md5(b) for b in bl_str])
    if isinstance(bl_str, str):
        flg = sbf.add(md5(bl_str))
        return flg


def add_many(bl_str_list):
    sbf.bulk_add(bl_str_list)


def is_contains(bl_str) -> bool:
    flg = sbf.__contains__(md5(bl_str))
    return flg


def is_contains_many(data_list):
    results = []
    for data in data_list:
        flg = is_contains(data)
        if flg:
            results.append(1)
        else:
            results.append(0)
    return results


def md5(str_obj):
    m = hashlib.md5()
    m.update(str_obj.strip().encode(encoding='utf-8'))
    r = m.hexdigest()
    return r
