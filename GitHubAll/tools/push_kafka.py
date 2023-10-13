# -*- coding: utf-8 -*-
#  开发时间：2022/8/11 18:08
#  文件名称：push_kafka.py
#  文件作者：陈梦妮
#  备注：数据推送
import json

import requests
from loguru import logger
from kafka import KafkaProducer

kafka_pro = KafkaProducer(
    bootstrap_servers=['8.130.131.161:9092', '8.130.94.243:9092', '8.130.37.191:9092'])


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
    try:
        data = {
            "msg": json.dumps(data_list),
            "topic": topic,
            "ip": "222.244.146.53"
        }
        url = 'http://140.210.203.161:8081/kafka/allMediaBatchTokafka'
        res = requests.post(url, data=data, timeout=8)
        res_json = res.json()
        if res_json.get('status', '') == 1:
            logger.info(f"【推送二】 成功 返回结果：{res_json['msg']}")
        else:
            logger.error(f"【推送二】 失败 返回结果：{res_json['msg']}")
    except Exception as e:
        logger.error(f"【推送二】 错误：{e}")


# def all_push_server(data_list, topic):
#     """
#     ES推送+字典清洗
#     :param data_list: 推送字典数据列表
#     :param topic: es表名
#     :return:
#     """
#     if data_list:
#         data_list = [check_item(data) for data in data_list]
#         push_server(data_list, topic)
#     else:
#         logger.debug(f'【聚合推送】 长度:[{len(data_list)}]')

def all_push_server(data_list, topic):
    """
    ES推送+字典清洗
    :param data_list: 推送字典数据列表
    :param topic: es表名
    :return:
    """
    if data_list:
        data_list = [check_item(data) for data in data_list]
        for data in data_list:
            send_data(topic, data)
    else:
        logger.debug(f'【聚合推送】 长度:[{len(data_list)}]')


def send_data(topic, item):
    d_count = 0
    while d_count < 3:
        try:
            send_data = json.dumps(item)
            future = kafka_pro.send(topic, send_data.encode())
            record_metadata = future.get(timeout=20)
            if record_metadata:
                logger.info(f'插入kafka成功')
                break
        except Exception as e:
            d_count = d_count + 1
            logger.error(str(e))
