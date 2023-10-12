from typing import Dict, Any
from loguru import logger
from network_information_source.nis_api import TaskServiceApi
from network_information_source.nis_utils import (update_task_status, kafka_utils, update_task_tag_status)

# --------切勿删除以下导入-----------#
from network_information_source.push_program import MappingKafka
from network_information_source.nis_find import website_find
from network_information_source.nis_verify import website_probe

"""
from network_information_source.push_program import MappingKafka
from network_information_source.nis_find import website_find
from network_information_source.nis_verify import website_probe
"""


def deploy(task_obj: TaskServiceApi, task: Dict[str, Any], crawl_type_method: list, topic: str, tag_topic: str,
           push_debug: bool = True, up_status_debug: bool = True, extract_method: str = 'extract_data'):
    # -------------初始配置，根据采集类型采用不同配置--------------#

    logger.warning(f"任务 【{task.get('task_id', '')}】 | 共计域名 【{len(task.get('host', ''))}】")

    for method in crawl_type_method:
        try:
            for info in globals()[method](**task):
                # print(info)
                if info is None:
                    continue

                task_id = info.get('task_id', '')
                task_id_number = info.get('task_id_number', '')
                task_time_consuming = info.get('time_consuming', '')
                task_tag = info.get('tag', False)

                finally_data = eval(f'MappingKafka(info).{extract_method}()')

                finally_data = dict(list(filter(lambda x: x[1] or x[1] is False, finally_data.items())))

                # print(format_json(finally_data))
                if push_debug:
                    kafka_utils.push_new_server([finally_data], topic)

                logger.success(f"task_id {task_id} | {task_id_number} | tag【{task_tag}】 | 耗时【{task_time_consuming}】")

                # 是否为分割的子任务
                is_split_task = True if task_tag else False

                is_task_done = update_task_tag_status(key=task_id, topic=tag_topic,
                                                      task_tag=task_tag) if is_split_task else False

                if up_status_debug is True and (is_task_done or is_split_task is False):
                    update_task_status(task_obj, task_id_number)

        except Exception as ex:
            logger.error(f'{ex}')
