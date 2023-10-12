import sys

# import redis

# import threading
sys.path.append('../../')

import os
from loguru import logger
import subprocess
from datetime import datetime, timedelta

FilePath = '/u01/isi/CenterProject/network_information_source/run/'


def monitor_detail(t_info):
    now_time = datetime.now()
    task_name = t_info['task_name']
    file_num = t_info['file_num']
    run_time = t_info['run_time']
    start_time = t_info['start_time']
    end_time = t_info['end_time']
    if not start_time:
        t_info['start_time'] = now_time.strftime('%Y-%m-%d %H:%M:%S')
        t_info['end_time'] = (now_time + timedelta(minutes=run_time)).strftime('%Y-%m-%d %H:%M:%S')
        log_run_detail(t_info, task_name, file_num)
    elif start_time and end_time < now_time.strftime('%Y-%m-%d %H:%M:%S'):
        t_info['start_time'] = end_time
        t_info['end_time'] = (now_time + timedelta(minutes=run_time)).strftime('%Y-%m-%d %H:%M:%S')
        log_run_detail(t_info, task_name, file_num)
    elif start_time and end_time > now_time.strftime('%Y-%m-%d %H:%M:%S'):
        return


def log_run_detail(t_info, task_name, file_num):
    file_name = f"{FilePath}/info/{task_name}.log"
    if not os.path.exists(file_name):
        if not os.path.isdir(f"{FilePath}/info"):
            os.makedirs(f"{FilePath}/info")
        open(file_name, 'w').close()
    file_stats = os.stat(file_name)
    file_size = int(file_stats.st_size)
    if file_size != file_num:
        num = file_size
        logger.info(
            f'程序名称：{task_name}.py---' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '---程序情况良好: ' + str(
                num))
    else:
        subprocess.call(f"sh {FilePath}/main.sh restart {task_name}", shell=True)
        logger.info(f'程序名称：{task_name}.py---' + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + "---启动完成,新: 0" + '---旧: ' + str(file_size))
        num = int(file_size)
    t_info['file_num'] = num


def logs_monitor():
    try:
        while True:
            # threading_list = []
            for t_info in task_info:
                monitor_detail(t_info)
            #     tl = threading.Thread(target=monitor_detail, kwargs={'t_info': t_info})
            #     threading_list.append(tl)
            #     tl.start()
            # for t in threading_list:
            #     t.join()
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    task_info = [
        {'task_name': 'deploy_find.py', 'run_time': 10, 'file_num': 0, 'start_time': '', 'end_time': ''},
        {'task_name': 'deploy_verify.py', 'run_time': 10, 'file_num': 0, 'start_time': '', 'end_time': ''},
    ]
    logs_monitor()
