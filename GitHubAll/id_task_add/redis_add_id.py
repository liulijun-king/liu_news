#  开发时间：2022/6/23 10:15
#  文件名称：redis_add_id.py
#  备注：添加id程序（不去重）
import redis
import sys

sys.path.append('../')
from GitHubAll.settings import id_key
from rediscluster import RedisCluster

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
    try:
        with open("max_id.txt", "r", encoding="utf-8") as f:
            max_id = int(f.read())
        pipeline = redis_conn.pipeline()
        pipeline.llen(id_key)
        key_len = pipeline.execute()[0]
        if key_len < 1000000:
            for _ in range(max_id, max_id + 10000000):
                id_ = str(_)
                pipeline.lpush(id_key, id_)
                count += 1
                if count == 10000:
                    with open("max_id.txt", "w", encoding="utf-8") as f:
                        f.write(str(_))
                    pipeline.execute()
                    print('一万个id添加完成！')
                    count = 0
    except(Exception,) as e:
        print(e)


add_id()
