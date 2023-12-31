#  开发时间：2022/6/23 10:15
#  文件名称：redis_add_id2.py
#  备注：添加id程序（去重）

from GitHubAll.settings import id_key
from rediscluster import RedisCluster
from tools.bloom_filter import is_contains

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


def add_id():
    count = 0
    repeat_num = 0
    try:
        pipeline = redis_conn.pipeline()
        for _ in range(100000, 1000000):
            id_ = str(_)
            if is_contains(id_) is False:
                pipeline.lpush(id_key, id_)
                count += 1
            else:
                repeat_num += 1

            if count == 10000:
                pipeline.execute()
                print('一万个id添加完成！')
                count = 0
    except(Exception,) as e:
        print(e)

    print(f'重复id共有{repeat_num}条')


add_id()
