import sys

sys.path.append("..")

from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from network_information_source.config import settings, VerifyRedisTaskTopic
from network_information_source.nis_utils import task_tools
from network_information_source.scheduler import deploy
from task_verify_outbound import tsa

RedisTaskTopic = VerifyRedisTaskTopic
task_topic = f'{RedisTaskTopic.test_task.value}_{settings.REGION.name}' if settings.DEPLOY_VERIFY_DEBUG else f'{RedisTaskTopic.task.value}_{settings.REGION.name}'

options = {
    'topic': 'topic_c1_original_site_ch',
    'tag_topic': RedisTaskTopic.tag_task.value,
    'push_debug': settings.DEPLOY_VERIFY_PUSH_DEBUG,
    'up_status_debug': settings.DEPLOY_VERIFY_PUSH_DEBUG,
    'extract_method': 'extract_verify_data',
}

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=settings.DEPLOY_VERIFY_THREAD_COUNT) as t:
        try:
            tasks = task_tools.pull(topic=task_topic, count=settings.DEPLOY_VERIFY_SINGLE_THREAD_TASK_COUNT,
                                    is_json=True)

            logger.info(f'正常运行')

            all_task = []
            for task in tasks:
                # logger.error(f'{task}')
                # deploy(
                #     task_obj=tsa,
                #     task=task,
                #     crawl_type_method=[
                #         'website_probe'
                #     ],
                #     **options
                # )
                all_task.append(t.submit(
                    deploy,
                    task_obj=tsa,
                    task=task,
                    crawl_type_method=[
                        'website_probe'
                    ],
                    **options
                ))

            for future in as_completed(all_task):
                try:
                    print(future.result())
                except Exception as ex:
                    logger.error(f'{ex}')

        except Exception as ex:
            logger.error(f'{ex}')
