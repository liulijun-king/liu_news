import json
from typing import Dict, Any, Optional, List, Iterator, Set, Iterable

import redis
from easy_spider_tool import is_format_json
from sshtunnel import SSHTunnelForwarder

from network_information_source.config import settings

SSH_HOST = '122.9.162.60'
SSH_PORT = 522
SSH_USER = 'isi'
SSH_PASSWORD = 'isi%2020'

REDIS_CONNECT = settings.REDIS_CONNECT


def is_json_string(wait_json_string: str) -> bool:
    try:
        json.loads(wait_json_string)
        return True
    except (ValueError, TypeError) as _:
        pass
    return False


def format_json2obj(wait_loads_obj: str) -> Dict[str, Any]:
    return json.loads(wait_loads_obj)


def create_ssh_tunnel():
    server = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),  # Remote server IP and SSH port
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(REDIS_CONNECT['host'], REDIS_CONNECT['port'])
    )

    return server


ENABLE_SSH_TUNNEL = False


class Redis(object):
    def __init__(self, redis_prepare: Dict[str, Any]):
        """"""
        if ENABLE_SSH_TUNNEL is True:
            server = create_ssh_tunnel()
            server.start()
            redis_prepare['port'] = server.local_bind_port

        pool = redis.ConnectionPool(**redis_prepare)
        self.conn = redis.Redis(connection_pool=pool)


class RedisString(Redis):
    def get(self, name: str, is_json: bool = False) -> Optional[Dict[str, Any]]:
        """取出值"""
        finally_data = self.conn.get(name)

        finally_data = format_json2obj(finally_data) if is_json is True else finally_data

        return finally_data

    def mget(self, keys: List[str], *args, is_json: bool = False) -> Optional[Dict[str, Any]]:
        """批量获取"""
        finally_datas = self.conn.mget(keys, *args)

        # finally_data = finally_data.decode('utf-8') if isinstance(finally_data, bytes) else finally_data

        finally_datas = [format_json2obj(finally_data) for finally_data in
                         finally_datas] if is_json is True else finally_datas

        return finally_datas


class RedisHash(Redis):
    def hset(self, name: Any, key: Any, value: Any):
        """
        name对应的hash中设置一个键值对（不存在，则创建；否则，修改）
        :param name:
        :param key:
        :param value:
        :return:
        """
        self.conn.hset(name, key, value)

    def hget(self, name: Any, key: Any, is_json: bool = False) -> Optional[Dict[str, Any]]:
        """

        :param is_json:
        :param key:
        :param name:
        :return:
        """
        finally_data = self.conn.hget(name, key)

        finally_data = format_json2obj(finally_data) if is_json is True and finally_data else finally_data

        return key, finally_data

    def hmset(self, name: Any, mapping: Any):
        """
        在name对应的hash中批量设置键值对

        :param name: redis的name
        :param mapping:字典，如：{'k1':'v1', 'k2': 'v2'}
        :return:
        """
        self.hmset(name, mapping)

    def hmget(self, name: Any, keys: Any, *args: Any, is_json: bool = False) -> Optional[Dict[str, Any]]:
        """
        在name对应的hash中获取多个key的值

        :param is_json:
        :param name:reids对应的name
        :param keys:要获取key集合，如：['k1', 'k2', 'k3']
        :param args:要获取的key，如：k1,k2,k3
        :return:
        """
        finally_datas = self.conn.hmget(name, keys, *args)

        finally_datas = [format_json2obj(finally_data) for finally_data in
                         finally_datas] if is_json is True else finally_datas

        finally_datas = [(k, v) for k, v in zip(keys, finally_datas)]

        for i in finally_datas:
            yield i

    def hgetall(self, name: Any, is_json: bool = False) -> Optional[Dict[str, Any]]:
        """获取name对应hash的所有键值"""

        finally_datas = self.conn.hgetall(name)

        finally_datas = [{k: format_json2obj(v)} for k, v in finally_datas.items() if
                         is_json_string(v)] if is_json is True else finally_datas

        return finally_datas

    def hlen(self, name: Any) -> int:
        """获取name对应的hash中键值对的个数"""
        return self.conn.hlen(name)

    def hdel(self, name: Any, *keys: Any) -> int:
        """将name对应的hash中指定key的键值对删除"""
        return self.conn.hdel(name, *keys)

    def hscan_iter(self, name: Any, match: Any = None, count: int = None) -> Iterable:
        """
        利用yield封装hscan创建生成器，实现分批去redis中获取数据

        :param name:
        :param match:匹配指定key，默认None 表示所有的key
        :param count:每次分片最少获取个数，默认None表示采用Redis的默认分片个数
        :return:
        """
        for i in self.conn.hscan_iter(name, match, count):
            yield i


class RedisList(Redis):
    def llen(self, name: Any) -> int:
        return self.conn.llen(name)

    def lpush(self, name: Any, *values: Any):
        """在name对应的list中添加元素，每个新的元素都添加到列表的最左边"""
        return self.conn.lpush(name, *values)

    def rpop(self, name: Any, count: int = None, is_json: bool = True) -> Iterable:
        """从右边移除count个元素，并且返回删除的元素"""
        # values = self.conn.rpop(name, count=count)
        with self.conn.pipeline(transaction=False) as pipeline:
            for _ in range(count):
                pipeline.rpop(name)
            values = pipeline.execute()

        for i in values:
            if i is None:
                continue
            if is_json and is_format_json(i):
                i = json.loads(i)
            yield i

    def lindex(self, name: Any, index: int) -> Optional[str]:
        """在name对应的列表中根据索引获取列表元素"""
        return self.conn.lindex(name, index)

    def list_iter(self, name):
        """
        自定义redis列表增量迭代
        :param name: redis中的name，即：迭代name对应的列表
        :return: yield 返回 列表元素
        """
        list_count = self.llen(name)
        for index in range(list_count):
            yield self.lindex(name, index)


class RedisSet(Redis):
    def sadd(self, name: Any, *values: Any) -> int:
        """name - 对应的集合中添加元素"""
        return self.conn.sadd(name, *values)

    def scard(self, name: Any) -> int:
        """获取name对应的集合中元素个数"""
        return self.conn.scard(name)

    def smembers(self, name: Any) -> Set[set]:
        """获取name对应的集合的所有成员"""
        return self.conn.smembers(name)

    def sscan(self, name: Any, cursor: int = 0, match: Any = None, count: Any = None) -> Any:
        """
        获取集合中所有的成员--元组形式
        :param name:
        :param cursor:
        :param match:
        :param count:
        :return:
        """
        return self.sscan(name, cursor, match, count)

    def sscan_iter(self, name: Any, match: Any = None, count: Any = None) -> Iterator[str]:
        """
        获取集合中所有的成员--迭代器的方式

        :param name:
        :param match:
        :param count:
        :return:
        """
        for i in self.conn.sscan_iter(name, match, count):
            yield i

    def spop(self, name: Any) -> Any:
        """从集合移除一个成员，并将其返回,说明一下，集合是无序的，所有是随机删除的"""
        return self.conn.spop(name)

    def srem(self, name: Any, values: Any) -> Any:
        """在name对应的集合中删除某些值"""
        return self.conn.srem(name, values)


class RedisSortSet(Redis):
    pass


r_hash = RedisHash(REDIS_CONNECT)
r_set = RedisSet(REDIS_CONNECT)
r_list = RedisList(REDIS_CONNECT)
