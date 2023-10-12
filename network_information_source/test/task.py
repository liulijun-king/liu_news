import json
from typing import Any, Dict, List

from network_information_source.config import VerifyRedisTaskTopic, task_backups
from network_information_source.nis_utils import r_set, common_add_task, extract_task

find_test_tasks = [

]
RedisTaskTopic = VerifyRedisTaskTopic

options = {
    'topic': RedisTaskTopic.task.value,
    'backups_topic': RedisTaskTopic.task_backups.value,
    'tag_topic': RedisTaskTopic.tag_task.value,
    'region': '2'
}


def query_backups() -> List[Dict[str, Any]]:
    # 查询备份任务
    tasks = []
    for index, i in enumerate(r_set.sscan_iter(task_backups)):
        i = json.loads(i)
        task = extract_task(i)
        task_id = task['task_id']
        if task_id == '4784eab4-1b4b-48b8-928f-43211647f906':
            print(index, i, sep=' ')
            tasks.append(i)
    return tasks


def push_test_task():
    tasks = query_backups()
    common_add_task(tasks, **options)


if __name__ == '__main__':
    query_backups()
    push_test_task()
