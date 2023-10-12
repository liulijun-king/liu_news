import sys

sys.path.append("..")

from GitHubAll.settings import redis_conn, day_crawl_key

redis_conn.delete(day_crawl_key)
