import hashlib
import json
import re
import time
from typing import Dict, Optional

import requests
from jsonpath import jsonpath
from parsel import Selector


def md5(s):
    """
    md5加密字符串
    :param s:
    :return:
    """
    if s:
        if isinstance(s, dict):
            s = json.dumps(s, ensure_ascii=False)
        m = hashlib.md5()
        m.update(s.encode())
        md5_str = m.hexdigest()
        return md5_str
    else:
        print(s)
        raise Exception("不能对空值进行哈希")


def del_data_none(data: dict):
    """
    字典空值删除,包括无,暂无,/,空
    :param data: 需要删除的字典
    :return: 删除完毕的字典
    """
    for key in list(data.keys()):
        if not data.get(key) or data.get(key) is None:
            # or data.get(key) == '无' or data.get(key) == '暂无' or data.get(key) == '空' or data.get(key) == '/'
            del data[key]
        if isinstance(data.get(key), list):
            if len(data.get(key)) == 0 or len(data.get(key)) == 1 and data.get(key)[0] == "":
                del data[key]
    return data


def json_print(data: dict or list):
    """
    json格式美化打印
    :param data:
    :return:
    """
    print(json.dumps(data, sort_keys=False, indent=4, separators=(',', ':'), ensure_ascii=False))


def time_handle(time_stamp):
    """
    时间戳转化
    :param time_stamp: 十位数时间戳
    :return:
    """
    time_array = time.localtime(time_stamp)
    time_data = time.strftime('%Y-%m-%d %H:%M:%S', time_array)
    return time_data


def json_path(obj: Dict, expr: str, default: Optional = '', is_list: bool = False):
    """
    jsonpath解析
    :param obj: 解析对象
    :param expr: jsonpath
    :param default: 未获取到返回默认值， 默认空字符串
    :param is_list: 是否保留list， 默认不保留
    :return: 解析值或者defult
    """
    value = jsonpath(obj, expr)
    if value:
        if not is_list:
            return value[0]
        else:
            return value
    else:
        return default


def turn_page(start_url, xpath_text):
    """
    翻页
    :param start_url: 首页链接
    :param xpath_text: 翻页xpath
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }
    while True:
        response = requests.get(start_url, headers=headers)
        html_sel = Selector(response.text)
        turn_url = html_sel.xpath(xpath_text).get()
        yield response
        if not turn_url:
            break
        start_url = turn_url


def re_match(match_rule, match_data, get_data=False):
    """
    正则匹配
    :param get_data: 返回原始数据
    :param match_rule: 匹配规则
    :param match_data: 需要匹配的数据
    :return:
    """
    result_mat = re.compile(match_rule).search(match_data)
    if result_mat is not None:
        result = result_mat.group('group1')
        return result
    elif get_data:
        return match_data
    else:
        return ''
