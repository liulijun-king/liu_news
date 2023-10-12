#  开发时间：2022/6/23 10:15
#  文件名称：redis_add_id.py
#  备注：添加id程序（不去重）
import redis
import sys

sys.path.append('../')
from GitHubAll.settings import id_key
from redis.cluster import RedisCluster
from redis.cluster import ClusterNode

startup_nodes = [
    ClusterNode("47.97.216.52", 6379),
    ClusterNode("120.55.67.165", 6379),
    ClusterNode("120.26.85.177", 6379),
]
redis_conn = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, password='gew29YAyi')

#
# # id_key = "gb_all:ids"
# redis_conn = redis.StrictRedis(host='47.97.216.52', port=6379, db=5, socket_connect_timeout=15, max_connections=20,
#                                decode_responses=True)


def add_id():
    count = 0
    try:
        with open("max_id.txt","r",encoding="utf-8") as f:
            max_id =int(f.read())
        pipeline = redis_conn.pipeline()
        pipeline.llen(id_key)
        key_len = pipeline.execute()[0]
        if key_len < 1000000:
            for _ in range(max_id, max_id+10000000):
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