import json
from copy import deepcopy
from typing import Dict, Any, List, Iterable, Union
from easy_spider_tool import jsonpath
from loguru import logger

from network_information_source.config import settings, task_backups, VerifyRedisTaskTopic, FindRedisTaskTopic, \
    TaskRegion
from network_information_source.nis_api import TaskServiceApi
from .redis_utils import r_set, r_hash


def task_pull(
        wait_tasks: list,
        redis_task_topic: Union[VerifyRedisTaskTopic, FindRedisTaskTopic],
        region: str = None,
        debug: bool = False
):
    """拉取任务  发现/验证"""
    options = {
        'topic': redis_task_topic.task.value if debug is False else redis_task_topic.test_task.value,
        'backups_topic': redis_task_topic.task_backups.value,
        'tag_topic': redis_task_topic.tag_task.value,
        'region': region
    }

    for wait_task in wait_tasks:
        common_add_task(wait_task, **options)

    if debug is True:
        exit(0)


def update_task_status(task_obj: TaskServiceApi, task_id: int):
    """更新任务执行状态"""
    res = task_obj.update_task_result(task_id, 2, '执行成功')
    if res.status_code == 200:
        logger.success(f"task_id {task_id} | 任务状态修改成功 | status_code {res.status_code}")
    else:
        logger.error(f"task_id {task_id} | 任务状态修改失败 | status_code {res.status_code}")


def update_task_tag_status(key: str, topic: str, task_tag: str) -> bool:
    """校验子任务是否都完成,注意误删除任务状态记录的情况"""
    # ---------------------------#
    is_split_task_done = False

    tags = task_tools.query_task_tag(key=key, topic=topic)
    tags_length = len(tags)

    if tags_length > 0:
        task_tools.update_task_tag(key=key, topic=topic, tag=task_tag)
        tags = task_tools.query_task_tag(key=key, topic=topic)
        tags_length = len(tags)

    if tags_length <= 0:
        is_split_task_done = True
        task_tools.del_task_tag(key=key, topic=topic)

    return is_split_task_done


def extract_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """解析任务,结构化"""
    api_params = json.loads(task.get('apiParams', {}))
    keyword = api_params.get('keyword', {})

    return {
        'task_id': jsonpath(task, '$.taskID', first=True, default=''),
        'task_id_number': jsonpath(task, '$.taskId', first=True, default=''),

        'host': jsonpath(keyword, '$.domain', first=True, default=[]) or jsonpath(keyword, '$.ip', first=True,
                                                                                  default=[]),
        'recursive_server': jsonpath(keyword, '$.dns', first=True, default=[]),
        # 使用哪个类型（ip、domain、certificate、dns）
        'search_type': jsonpath(api_params, '$.searchType', first=True, default=''),
        # 关联发现还是聚合发现 relation polymerization verify
        'find_type': jsonpath(api_params, '$.findType', first=True, default=''),
        'api_url': jsonpath(task, '$.apiUrl', first=True, default=''),
        # 采集任务标识
        'task_tag': jsonpath(api_params, '$.taskTag', first=True, default=''),
        # 任务期望完成时间(用户输入的期望完成时间)，几小时后
        'task_complet_time': jsonpath(keyword, '$.task_complet_time', first=True, default=''),
        # 任务终止时间
        'task_finish_time': jsonpath(keyword, '$.taskFinishTime', first=True, default=''),
        # 境内外
        'region': jsonpath(api_params, '$.region', first=True, default=1),
    }


def split_task(task: Dict[str, Any]) -> Iterable:
    """ 任务分割成多个子任务"""

    hosts = task.pop('host', [])
    recursive_server = task.get('recursive_server', [])
    split_hosts = [hosts[i:i + settings.TASK_SPLIT_COUNT] for i in range(0, len(hosts), settings.TASK_SPLIT_COUNT)]

    tag_count = str(len(split_hosts))

    task['recursive_server'] = list(set(recursive_server))

    for index, i in enumerate(split_hosts, start=1):
        yield {
            **deepcopy(task),
            'host': i,
            'tag_count': tag_count,
            'tag': str(index),
        }


def common_add_task(
        wait_tasks: list,
        topic: str,
        backups_topic: str,
        tag_topic: str,
        key: str = 'task_id',
        region: str = '1',
        **kwargs
):
    """
        通用任务发布
    :param region:
    :param wait_tasks:
    :param topic:
    :param backups_topic:
    :param tag_topic:
    :param key:
    :param kwargs:
    :return:
    """
    after_treatment_tasks = []

    for task in wait_tasks:
        print(task)
        src_task = extract_task(task)

        task_id = src_task.get('task_id', '')
        search_type = src_task.get('search_type', '')
        find_type = src_task.get('find_type', '')
        host_count = len(src_task.get('host', []))
        src_task['region'] = region

        logger.info(
            f'task_id 【{task_id}】 | 搜索类型 【{search_type}】 | 发现类型 【{find_type}】 | region 【{region}】 | 主机数量 【{host_count}】')

        if host_count > settings.TASK_SPLIT_COUNT:
            after_treatment_tasks.extend(list(split_task(src_task)))
        else:
            src_task.update({'tag_count': 0})
            after_treatment_tasks.append(src_task)

    domestic_tasks = []  # 境内任务
    abroad_tasks = []  # 境外任务

    for i in after_treatment_tasks:
        # 任务按境内外分流
        if region == '2':
            domestic_tasks.append(i)
            abroad_tasks.append(i)
        elif region == '1':
            abroad_tasks.append(i)
        elif region == '0':
            domestic_tasks.append(i)

    for topic, content in zip(
            [f'{topic}_{TaskRegion.domestic.name}', f'{topic}_{TaskRegion.outbound.name}'],
            [domestic_tasks, abroad_tasks]
    ):
        if not content:
            continue

        task_tools.push(tasks=content, topic=topic)
        task_tools.push(tasks=content, topic=backups_topic)
        task_tools.add_task_tag(tasks=content, key=key, topic=tag_topic)

    task_tools.push(tasks=wait_tasks, topic=task_backups)


class TaskTools:
    @staticmethod
    def push(tasks: list, topic: str) -> bool:
        """批量推送任务至redis"""
        with r_set.conn.pipeline(transaction=False) as pipe:
            for _item in tasks:
                pipe.sadd(topic, json.dumps(_item, ensure_ascii=False))
            result = pipe.execute()
        if all(result):
            logger.success(f'{topic} 全部推送成功 {len(result)}条')
            return True
        if any(result):
            logger.warning(f'{topic} 部分推送成功 {len(result)}条')
            return False
        logger.error(f'{topic} 全部推送失败或数据重复 {len(result)}条')

    @staticmethod
    def pull(topic: str, count: int = 10, is_json: bool = False) -> List[Dict[str, Any]]:
        """"""
        data_array = r_set.conn.spop(topic, count)

        if is_json:
            data_array = [json.loads(data) for data in data_array]

        return data_array if data_array else []

    def __gen_task_tag(self, task: dict, key: str) -> Dict[str, Any]:
        """生成任务标签"""
        tag_count = int(task.get('tag_count', 0))
        tags = list(range(1, tag_count + 1))
        return {
            key: task[key],
            'tag_count': tag_count,
            'tags': tags
        }

    def query_task_tag(self, key: str, topic: str) -> List[str or int]:
        """查询标签"""
        with r_hash.conn.pipeline(transaction=False) as pipe:
            pipe.hget(topic, key)
            finally_result = pipe.execute()
        finally_result = [json.loads(data) for data in finally_result if data]
        return finally_result[0]['tags'] if finally_result else []

    def add_task_tag(self, tasks: list, key: str, topic: str) -> bool:
        """添加任务标签"""

        def del_repeat(data, key):
            new_data = []
            values = []
            for d in data:
                if d[key] not in values:
                    new_data.append(d)
                    values.append(d[key])
            return new_data

        tasks = del_repeat(tasks, key)

        tasks = [self.__gen_task_tag(i, key) for i in tasks]

        if all(tasks):
            with r_hash.conn.pipeline(transaction=False) as pipe:
                for i in tasks:
                    pipe.hset(topic, i[key], json.dumps(i, ensure_ascii=False))
                result = pipe.execute()

        return True

    def del_task_tag(self, key: str, topic: str) -> bool:
        """删除任务"""
        r_hash.hdel(topic, key)
        return True

    def update_task_tag(self, key: str, topic: str, tag: Union[int, str]) -> bool:
        """更新任务标签"""
        with r_hash.conn.pipeline(transaction=False) as pipe:
            pipe.hget(topic, key)
            finally_result = pipe.execute()

        if all(finally_result):
            for data in finally_result:
                data = json.loads(data)
                if int(tag) in data['tags']:
                    data['tags'].remove(int(tag))
                r_hash.hset(topic, key, json.dumps(data, ensure_ascii=False))
                logger.success(f'更新任务成功 【{key}】')
        return True


task_tools = TaskTools()

if __name__ == '__main__':
    pass
