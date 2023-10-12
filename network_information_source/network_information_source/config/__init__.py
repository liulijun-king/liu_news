"""
境内外任务直接在task表后加_domestic,_abroad
"""
from enum import Enum

from .settings import settings, TaskRegion

task_backups = 'nis:backups:tasks'


# nis:find:tasks_abroad
# nis:find:tasks_domestic


class FindRedisTaskTopic(Enum):
    # 发现任务
    task = f'nis:find:tasks'
    test_task = f'nis:find:test:tasks'
    task_backups = f'nis:find:backups:tasks'

    tag_task = f'nis:find:tag:tasks'


class VerifyRedisTaskTopic(Enum):
    # 验证任务
    task = f'nis:verify:tasks'
    test_task = f'nis:verify:test:tasks'
    task_backups = f'nis:verify:backups:tasks'

    tag_task = f'nis:verify:tag:tasks'
