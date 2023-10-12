import sys

sys.path.append("..")
from loguru import logger
from network_information_source.nis_api import TaskServiceApi
from network_information_source.nis_utils import task_pull
from network_information_source.config import settings, FindRedisTaskTopic

tsa = TaskServiceApi(
    name='nis',
    api_code=10050001,
    access_token='E2DC2844F249567D75AF5FA0846A764B',
    debug=False
)

region = '2'

if __name__ == '__main__':
    try:
        wait_tasks = tsa.query_wait_tasks(crawl_mode=settings.FIND_CRAWL_MODE, region=region)
        print(len(wait_tasks))
        task_pull(
            wait_tasks,
            FindRedisTaskTopic,
            region,
            settings.TASK_FIND_DEBUG,
        )
    except Exception as ex:
        logger.error(f'{ex}')
