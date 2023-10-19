# -*- coding: UTF-8 -*-

import copy
import hashlib
import json
import os
import re
import time
import math
from datetime import datetime, timedelta
from urllib.parse import urljoin

import dateparser
import filetype
import jsonpath
import requests
from loguru import logger
from lxml import etree
from pymysql.converters import escape_string
from retrying import retry

from tools.req_tools import req_chrome_get, req_chrome_post
from tools.proxy_get import queue_empty


def retry_error(exception):
    print(exception)
    return isinstance(exception, Exception)


@retry(retry_on_exception=retry_error, stop_max_attempt_number=3, wait_fixed=500)
def send_data(data):
    url = "http://220.194.140.39:30002/_db/insert"
    sql = f"""insert ignore into major_info_0828({','.join(data.keys())}) values({','.join(['?'] * len(data.keys()))})"""
    payload = json.dumps({
        "dbSource": 1,
        "sql": sql,
        "paras": [list(data.values())],
        "batchSize": 1
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload, timeout=60)


def get_md5(val):
    """把目标数据进行哈希，用哈希值去重更快"""
    # val = str(val)
    md5 = hashlib.md5()
    md5.update(val.encode('utf-8'))
    return md5.hexdigest()


def sha256_detail(text):
    x = hashlib.sha256()
    x.update(text.encode())
    return x.hexdigest()


@retry(retry_on_exception=retry_error, stop_max_attempt_number=3, wait_fixed=500)
def req_get(url, headers, params=None, cookies=None, proxies=None, verify=True, other_req=False, stream=None):
    if other_req:
        response = req_chrome_get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url=url, headers=headers, params=params, verify=verify, cookies=cookies,
                                proxies=proxies, stream=stream, timeout=30)
    return response


@retry(retry_on_exception=retry_error, stop_max_attempt_number=3, wait_fixed=500)
def req_post(url, headers=None, data=None, params=None, verify=True, cookies=None, proxies=None, other_req=False,
             json_data=None):
    if other_req:
        response = req_chrome_post(url, headers=headers, data=data, proxies=proxies)
    else:
        response = requests.get(url=url, headers=headers, data=data, params=params, verify=verify, cookies=cookies,
                                timeout=30,
                                proxies=proxies, json=json_data)
    return response


def time_parse(time_text, time_style="%Y-%m-%d %H:%M:%S", url=""):
    """
    将时间换算成国际时间
    :param url: 文章url，用于报错处理
    :param time_text: 需要处理的文本
    :param time_style: 时间格式（例如：%Y-%m-%d %H:%M:%S）
    :return: 处理后的时间:str
    """
    time_final = None
    try:
        if "T" in time_text and "Z" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=0)
            time_final = time_dt.strftime(time_style)
        elif "BST" in time_text or "bst" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=-1)
            time_final = time_dt.strftime(time_style)
        elif "JST" in time_text or "jst" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=-9)
            time_final = time_dt.strftime(time_style)
        elif "CST" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=-8)
            time_final = time_dt.strftime(time_style)
        elif "EDT" in time_text or "ET" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=+4)
            time_final = time_dt.strftime(time_style)
        else:
            time_dt = dateparser.parse(time_text)
            time_final = time_dt.strftime(time_style)
    except(Exception,) as e:
        print(f"时间处理发生错误！ | {str(e)} | 文章url：{url}")
        # logger.error(f"时间处理发生错误！ | {str(e)} | 文章url：{url}")
    return time_final


def get_json_path(json_data, json_path):
    result = jsonpath.jsonpath(json_data, json_path)
    if type(result) == list:
        if len(result) == 1:
            return result[0]
        elif len(result) == 0:
            return ""
        else:
            return result
    else:
        return ""


def time_deal(need_time):
    if re.search(r'\d{10,13}', str(need_time)):
        need_time = int(need_time)
        if len(str(need_time)) == 13:
            need_time = need_time / 1000
        time_array = time.localtime(need_time)
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', need_time):
        other_style_time = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', need_time).group()
        return other_style_time
    elif re.search(r'\d{2}-\d{2}-\d{2}$', need_time):
        time_array = time.strptime(need_time, "%Y-%m-%d")
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}:\d{2}$', need_time):
        time_array = time.strptime(need_time, "%Y年%m月%d日 %H:%M:%S")
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', need_time).group()
        time_array = time.strptime(need_time, "%Y-%m-%dT%H:%M:%S")
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}', need_time).group()
        time_array = [n.strip() for n in need_time.split('-')]
        day_array = time_array[0].split('/')
        day_str = '-'.join(day_array[::-1])
        hour_str = time_array[1] + ':00'
        return f"{day_str} {hour_str}"
    elif re.search(r'\d{4}-\d-\d\s+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{4}-\d-\d\s+\d{2}:\d{2}', need_time).group()
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r'\d{4}年\d月\d日', need_time):
        need_time = re.search(r'\d{4}年\d月\d日', need_time).group()
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}', need_time).group()
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r'\d{8}', need_time):
        need_time = f"{need_time[:4]}-{need_time[4:6]}-{need_time[6:]} 00:00:00"
        return need_time
    elif re.search("\d{2}\.\d{2}\.\d{4}", need_time):
        need_time = f"{need_time[6:]}-{need_time[3:6]}-{need_time[:2]}"
        need_time = time_parse(need_time)
        return need_time
    else:
        need_time = standardize_date(need_time)
        if not re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", need_time):
            need_time = time_parse(need_time)
        return need_time


def standardize_date(time_str, strftime_type="%Y-%m-%d %H:%M:%S"):
    if u"刚刚" in time_str:
        time_str = datetime.now().strftime(strftime_type)
    elif u"分钟" in time_str:
        minute = time_str[:time_str.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        time_str = (datetime.now() - minute).strftime(strftime_type)
    elif u"小时" in time_str:
        hour = time_str[:time_str.find(u"小时")]
        hour = timedelta(hours=int(hour))
        time_str = (datetime.now() - hour).strftime(strftime_type.replace("%M:%S", "00:00"))
    elif u"昨天" in time_str:
        day = timedelta(days=1)
        if re.match(r"\d+:\d+", time_str):
            time_str = (datetime.now() - day).strftime("%Y-%m-%d") + time_str
        else:
            time_str = (datetime.now() - day).strftime(strftime_type.replace(" %H:%M:%S", " 00:00:00"))
    elif u"天前" in time_str:
        day_last = int(time_str[:time_str.find(u"天前")])
        day = timedelta(days=day_last)
        if re.match(r"\d+:\d+", time_str):
            time_str = (datetime.now() - day).strftime("%Y-%m-%d") + time_str
        else:
            time_str = (datetime.now() - day).strftime(strftime_type.replace(" %H:%M:%S", " 00:00:00"))
    else:
        time_str = time_str
    return time_str


def get_date(day):
    start_date = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400 * day))
    return start_date.replace("-", "")


def get_dates_list(start_date, end_date):
    dates = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y-%m-%d')
        dates.append(formatted_date)
        current_date += timedelta(days=1)
    return dates


def content_conversion(html):
    if len(html) > 1:
        html = "".join(etree.tostring(li, encoding="utf-8").decode('utf-8') for li in html)
    else:
        html = etree.tostring(html[0], encoding="utf-8").decode('utf-8')
    if html:
        html = html.replace("&#13;", "\n")
        html = html.replace("<br/>", "\n")
        html = re.sub(r"<font.*?>|</font>|\xa0", "", html)
        html = re.sub(r"<span.*?>|</span>", "", html)
        html = re.sub(r"<[a-hj-zA-HJ-Z].*?>", "<p>", html)
        html = re.sub(r"</[a-hj-zA-HJ-Z].*?>", "</p>", html)
        while re.search(r"<p>[\n\t\r\\s ]{0,20}<p>", html):
            html = re.sub(r"<p>[\n\t\r\\s ]{0,20}<p>", "<p>", html)
        while re.search(r"</p>[\n\t\r\\s ]{0,20}</p>", html):
            html = re.sub(r"</p>[\n\t\r\\s ]{0,20}</p>", "</p>", html)
        error_p = clear_p(html)
        error_q = clear_q(html)
        html = obtin_text(error_p, html)
        html = obtin_p(error_q, html)
        return html
    else:
        return ""


def clear_p(html):
    error_list = []
    html_ind = html.index("<p>")
    p_index = 0
    while html_ind != -1:
        new_ind = html_ind
        while True:
            if new_ind <= 0:
                break
            need_html = copy.deepcopy(html[new_ind - 1:new_ind])
            if re.sub("\r|\t|\n|\\s| ", "", need_html).strip() == "":
                new_ind -= 1
            elif re.sub("\r|\t|\n|\\s| ", "", need_html) == ">":
                if html[new_ind - 4:new_ind] != "</p>":
                    error_list.append(p_index)
                    break
                else:
                    break
            else:
                error_list.append(p_index)
                break
        html_ind = html.find("<p>", html_ind + 1)
        p_index += 1
    return error_list


def clear_q(html):
    error_list = []
    html_ind = html.index("</p>")
    p_index = 0
    while html_ind != -1:
        new_ind = html_ind + 4
        while True:
            if new_ind >= len(html):
                break
            need_html = copy.deepcopy(html[new_ind:new_ind + 1])
            if re.sub("\r|\t|\n|\\s| ", "", need_html).strip() == "":
                new_ind += 1
            elif re.sub("\r|\t|\n|\\s| ", "", need_html) == "<":
                if html[new_ind:new_ind + 3] != "<p>":
                    error_list.append(p_index)
                    break
                else:
                    break
            else:
                error_list.append(p_index)
                break
        html_ind = html.find("</p>", html_ind + 1)
        p_index += 1
    return error_list


def obtin_text(error_p, html):
    html_ind = html.find("<p>")
    first_index = 0
    last_content = ""
    p_index = 0
    while html_ind != -1:
        need_html = html[first_index:html_ind]
        if p_index in error_p:
            last_content += need_html
            first_index = html_ind + 3
        else:
            last_content += need_html
            first_index = html_ind
        html_ind = html.find("<p>", html_ind + 1)
        p_index += 1
        if html_ind == -1:
            last_content += html[first_index:]
    return last_content


def obtin_p(error_q, html):
    html_ind = html.find("</p>")
    first_index = 0
    last_content = ""
    p_index = 0
    while html_ind != -1:
        need_html = html[first_index:html_ind]
        if p_index in error_q:
            last_content += need_html
            first_index = html_ind + 4
        else:
            last_content += need_html
            first_index = html_ind
        html_ind = html.find("</p>", html_ind + 1)
        p_index += 1
        if html_ind == -1:
            last_content += html[first_index:]
    return last_content


def dict_to_sql(item, table_name):
    key_list = []
    value_list = []
    for key, value in item.items():
        key_list.append(key)
        if type(value) == str:
            value_list.append(escape_string(value))
        else:
            value_list.append(value)
    key_list = ",".join(key_list)
    value_list = tuple(value_list)
    sql = f"insert into {table_name} ({key_list}) values {value_list}"
    return sql


def get_past_times(num):
    """
    获取前num天的时间
    :param num: 前num天
    :return:
    """
    need_time = int(time.time()) - num * 3600 * 24
    time_array = time.localtime(need_time)
    other_style_time = time.strftime("%Y-%m-%d", time_array)
    return other_style_time


def get_proxies():
    url = f'http://220.194.140.39:30022/getip?num=1&ip=&key=&source=zhima'
    rep = requests.get(url=url, timeout=10)
    proxies_data = rep.json().get('data', '')
    if proxies_data:
        proxies = {
            "http": f'{proxies_data[0]["ip"]}:{proxies_data[0]["port"]}',
            "https": f'{proxies_data[0]["ip"]}:{proxies_data[0]["port"]}'
        }
        return proxies
    return {}


def check_dict(item):
    for key, value in item.items():
        if type(value) == str and value == "":
            return True
    return False


def get_item():
    items = {
        "S": "zicai",  # 数据来源
        "title": "",  #
        "content": "",  #
        "source_url": "",  # 博文地址url
        "pictures": "",  # 图片链接
        "user_id": "",  # 博主id
        "thread_id": "",  # 博主id
        "user_name": "",  # 作者
        "author": "",  # 作者
        "user_url": "",  # 用户主页
        "author_url": "",  # 用户主页
        "sex": "",  # 性别(1-女；2-男)
        "article_id": "",  # 文章id
        "pid": "",  # 文章id
        "language": "",  #
        "host": "",  # 域名
        "website_name": "",  # 论坛名称
        "channel_name": "",  # 频道名称
        "pubtime": "",  # 发布时间
        "crawler_no": "",  # 采集节点
        "crawler_type": "",  # 采集类型标识
        "read_count": "",  # 阅读数
        "review_count": "",  # 阅读数
        "cmt_count": "",  # 评论量
        "region": "",  # 0-境内，1-境外
        "insert_time": "",  # 入kafka时间
        "md5": "",  # md5(source_url)
        "uuid": "",  #
        "article_type": "",  # 文章类型(0-1楼，1-评论)
        "unique_art_id": "",  # 文章唯一标识
        "links_type": "",  # 文章类型标识（文本，图片，视频）
        "pictures_array": "",  # 图片链接
        "ref_unique_art_id": "",  # 关联文章唯一标识
        "source_id": "",  # 一级评论根id
        "comments_id": "",  # 评论id
        "source_content": "",  # 评论的原文内容
        "page": "",  # 页数
        "floor": "",  # 楼层
        "interaction_count": "",  #
    }


def data_clear(data: dict):
    das = ['title', 'content', 'pubtime', 'source_url', 'author', 'website_name', 'source', 'read_count', 'cmt_count',
           'likes_count']
    new_items = {}
    for key, value in data.items():
        if key in das:
            new_items[key] = value
    return new_items


def dds(need_time):
    if type(need_time) == str:
        # re.search(r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}", need_time)
        time_array = time.strptime(need_time, "%Y/%m/%d %H:%M:%S")
        return int(time.mktime(time_array))
    else:
        return need_time


def inspection_time(date_list, min_time):
    for data in date_list:
        if dds(data) > min_time:
            return False
    return True


def wen_hai_parser_server(source_url, source_html, encoding=None):
    """闻海内容抽取服务"""
    if not encoding:
        encoding = 'utf-8'
    url = 'http://111.53.223.241:30072/extractor/detail'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'provider': 'datagroup',
        'html': source_html,
        'queue_info': {
            'type': 'news',
            'source_url': source_url
        },
        'encoding': encoding,
        'url': source_url
    }
    r = req_post(url, headers=headers, json_data=payload)
    return r.json()


def time_check(spider_time, stipulate_time):
    # 转换成时间数组
    spider_time = time.strptime(spider_time, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    spider_time = time.mktime(spider_time)
    # 转换成时间数组
    stipulate_time = time.strptime(stipulate_time, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    stipulate_time = time.mktime(stipulate_time)
    if spider_time <= stipulate_time:
        return True
    else:
        return False


def push_single_server(push_data, topic):
    """
    单条数据推送
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
        if res_json.get('status', '') == 1:
            logger.info(f"【推送new】 成功 返回结果：{res_json['msg']}")
        else:
            logger.error(f"【推送new】 失败 返回结果：{res_json['msg']}")
    except Exception as e:
        logger.error(f"【推送new】 错误：{e}")


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


def get_file_type(file_stream, img_url):
    if re.search("jpg|png|webp|jpeg|bmp|svg", img_url):
        return re.search("jpg|png|webp|jpeg|bmp|svg", img_url).group()
    else:
        file_type = get_type(file_stream)
        if file_type:
            return file_type
        else:
            return "jpg"


def get_type(file_stream):
    try:
        kind = filetype.guess(file_stream)
        return kind.extension
    except Exception as e:
        return None


def url_join(base_url, url):
    if re.search("news.google.com", base_url) and re.search("\./articles", url):
        new_url = re.sub("\./articles", "https://news.google.com/articles", url)
    else:
        new_url = urljoin(base_url, url).strip()
    return new_url


def ergodic_file(base):
    all_f = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            all_f.append(f"{root}/{f}")
    return all_f


def get_files_type(file_url):
    if re.search(r"\.pdf", file_url):
        return "pdf"
    elif re.search(r"\.xls", file_url):
        return "xls"
    elif re.search(r"\.xlsx", file_url):
        return "xlsx"
    elif re.search(r"\.doc", file_url):
        return "doc"
    elif re.search(r"\.docx", file_url):
        return "docx"
    elif re.search(r"\.zip", file_url):
        return "zip"
    elif re.search(r"\.jpg", file_url):
        return "jpg"
    elif re.search(r"\.png", file_url):
        return "png"
    else:
        return "pdf"


if __name__ == '__main__':
    print(get_date(1))
