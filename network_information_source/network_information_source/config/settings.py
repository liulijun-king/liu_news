from enum import Enum


class TaskRegion(Enum):
    outbound = 1
    domestic = 0


class Settings(object):
    # --------任务相关--------#
    TASK_SPLIT_COUNT = 1000

    DNS_THREAD_COUNT = 100
    WEBSITE_THREAD_COUNT = 300

    WEB_SITE_PROBE_THREAD_COUNT = 300

    # ---------redis相关------#
    ENABLE_SSH_TUNNEL = False

    REDIS_CONNECT = {
        'host': '47.97.216.52',
        'port': 6379,
        'password': 'gew29YAyi',
        'db': 5,
        'decode_responses': True
    }

    SSH_HOST = '122.9.162.60'
    SSH_PORT = 522
    SSH_USER = 'isi'
    SSH_PASSWORD = 'isi%2020'

    # ---------find调试配置------#
    TASK_FIND_DEBUG = False  # 推送测试任务
    FIND_CRAWL_MODE = '1'  # 任务模式

    # ---------find运行配置------#
    DEPLOY_FIND_THREAD_COUNT = 1  # 多线程拉取任务
    DEPLOY_FIND_SINGLE_THREAD_TASK_COUNT = 5  # 单线程跑几个任务

    DEPLOY_FIND_DEBUG = False  # 调试模式
    DEPLOY_FIND_PUSH_DEBUG = True  # 是否推送

    # ---------verify调试配置------#
    TASK_VERIFY_DEBUG = False
    VERIFY_CRAWL_MODE = '1'

    DEPLOY_VERIFY_DEBUG = False
    DEPLOY_VERIFY_PUSH_DEBUG = True

    DEPLOY_VERIFY_THREAD_COUNT = 1
    DEPLOY_VERIFY_SINGLE_THREAD_TASK_COUNT = 5

    # 境内外标识
    # 默认境外
    # 1：境外 outbound
    # 0：境内 domestic
    # 2： 境内和境外
    REGION = TaskRegion.domestic


settings = Settings()
