# -*- coding = utf-8 -*-
# @Time : 2021/10/20 19:58
# @Author : 邓星晨
# @File : push_service.py
import json

import requests
from loguru import logger


def check_item(item):
    """
    字典空字符清除
    :param item:
    :return:
    """
    keys = list(item.keys())
    for key in keys:
        value = item[key]
        if not value and value != 0:
            del item[key]
    return item


def push_server(data_list, topic):
    data = {
        "msg": json.dumps(data_list),
        "topic": topic,
        "ip": "222.244.146.53"
    }
    url = 'http://220.194.140.39:30015/kafka/allMediaBatchTokafka'
    res = requests.post(url, data=data, timeout=10)
    res_json = res.json()
    if res_json.get('status', '') != 1:
        logger.error(f"【推送二】 失败 返回结果：{res_json['msg']}")
    else:
        logger.success(f"【推送二】 成功 返回结果：{res_json['msg']}")


def push_single_server(push_data, topic):
    """
    :param push_data: 
    :param topic:
    :return: 
    """
    try:
        push_data = check_item(push_data)
        data = {
            "msg": json.dumps(push_data),
            "topic": topic,
            "ip": "222.244.146.53"
        }
        url = 'http://220.194.140.39:30015/kafka/allMediaTokafka'
        res = requests.post(url, data=data, timeout=8)
        res_json = res.json()
        if res_json.get('status', '') != 1:
            logger.error(f"【推送new】 失败 返回结果：{res_json['msg']}")
        else:
            logger.info(f"【推送new】 {push_data['uuid']} 成功 返回结果：{res_json['msg']}")
    except Exception as e:
        logger.error(f"【推送new】 错误：{e}")


def all_push_server(data_list, topic):
    """
        ES推送+字典清洗
    :param data_list: 推送字典数据列表
    :param topic: es表名
    :return:
    """
    if data_list:
        data_list = [check_item(data) for data in data_list]
        push_server(data_list, topic)
    else:
        logger.debug(f'【聚合推送】 长度:[{len(data_list)}]')


def slice_push_server(data_list, topic, n=100):
    """
        切片 ES推送+字典清洗
    :param data_list: 推送字典数据列表
    :param topic: es表名
    :param n: 切片list长度 默认100
    :return:
    """
    if data_list:
        data_list = [check_item(data) for data in data_list]
        if len(data_list) >= n:
            for i in range(0, len(data_list), n):
                slice_list = data_list[i:i + n]
                push_server(slice_list, topic)
        else:
            push_server(data_list, topic)
    else:
        logger.debug(f'【ES切片推送】 不能为空 长度:[{len(data_list)}]')
