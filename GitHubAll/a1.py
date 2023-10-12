import json
import queue
from typing import Dict, Optional
import requests
from jsonpath import jsonpath
import dateparser
from urllib.parse import urlparse
import hashlib
from datetime import datetime
from lxml import etree

queue = queue.Queue()


def proxy_pool() -> list:
    """
    使用境外动态代理
    :return: 代理列表
    """
    proxy_url = 'http://api.proxy.ipidea.io/getProxyIp?num=100&return_type=json&lb=6&sb=0&flow=1&regions=&protocol=http'
    # proxy_url = 'http://220.194.140.39:30022/getip?num=150&ip=&key=&source=zhima'
    proxy_con = requests.get(proxy_url).text
    proxy_json = json.loads(proxy_con)
    print(proxy_json)
    proxy_text = [(proxy["ip"] + ':' + str(proxy["port"])) for proxy in proxy_json["data"]]
    return proxy_text


def queue_empty():
    while True:
        if queue.empty():
            proxy_list = proxy_pool()
            for i in proxy_list:
                queue.put(i)
        pro = queue.get()
        if pro:
            if "http" not in pro:
                pro = "http://" + pro
            break
    proxies = str(pro)
    return proxies


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


def item_main():
    """
    项目字段设置
    :return:
    """
    item = {
        # 采集关键字
        "module_name": "",
        # fork的原项目ID
        "fork_original_project": "",
        # fork的根项目ID
        "fork_root_project": "",
        # 项目名
        "project_name": "",
        # 用户id
        "user_id": "",
        # 项目作者
        "author": "",
        # 创建时间
        "create_time": "",
        # 项目提交次数
        "commit_count": "",
        # 项目标签
        "tags": "",
        # 项目星数
        "stars_count": "",
        # 项目浏览数
        "watch_count": "",
        # 项目fork数
        "forks_count": "",
        # 项目贡献数
        "contributors_count": "",
        # 项目简介
        "abstract": "",
        # read me内容
        "readme": "",
        # 基本信息
        "source_url": "",
        # 接口url
        "ref_url": "",
        # github二月新增需求
        "host_ip": "140.82.121.4",
        "AlexaInfo": 36,
        "host": "",
        "sub_host": "",
        "website_name": "",
        "website_sub_name": "",
        "uuid": "",
        "crawler_time": "",
        "insert_time": "",
        "update_time": "",
    }
    return item


headers = {
    'authority': 'api.github.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}


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


def hsd():
    pro = queue_empty()
    response = requests.get('https://api.github.com/repositories/129007092', headers=headers, proxies={
        'http': pro,
        'https': pro
    })
    item = item_main().copy()
    # fork的原项目ID
    item["fork_original_project"] = json_path(response.json(), '$.parent.full_name')
    # fork的根项目ID
    item["fork_root_project"] = json_path(response.json(), '$.source.full_name')
    # 项目名
    item["project_name"] = json_path(response.json(), '$.name')
    # 创建时间
    create_time = json_path(response.json(), '$.created_at')
    if create_time:
        item["create_time"] = dateparser.parse(create_time).strftime("%Y-%m-%d %H:%M:%S")
    else:
        print(f"该文章无发布时间！ | 接口url：{response.url}")
    # 项目作者
    author = json_path(response.json(), '$.owner.login')
    item["author"] = author
    item["user_id"] = author
    # 项目标签
    tags = json_path(response.json(), '$.topics')
    item["tags"] = "#".join(tags)
    # 项目星数
    stars_count = json_path(response.json(), '$.stargazers_count')
    item["stars_count"] = str(stars_count)
    # 项目浏览数
    watch_count = json_path(response.json(), '$.subscribers_count')
    item["watch_count"] = str(watch_count)
    # 项目fork数
    forks_count = json_path(response.json(), '$.forks_count')
    item["forks_count"] = str(forks_count)
    # 项目简介
    item["abstract"] = json_path(response.json(), '$.description')
    # 项目id
    project_id = json_path(response.json(), '$.id')
    # 项目url
    source_url = json_path(response.json(), '$.html_url')
    gets(source_url, item, project_id)


def gets(source_url, item, project_id):
    pro = queue_empty()
    response = requests.get(source_url, headers=headers, proxies={
        'http': pro,
        'https': pro
    })
    response = etree.HTML(response.content.decode())
    # 项目提交次数
    item["commit_count"] = "".join(response.xpath("//span[@class='d-none d-sm-inline']/strong/text()"))
    # 项目贡献数
    contributors_count = "".join(response.xpath("//a[contains(text(), 'Contributors')]/span/text()"))
    item["contributors_count"] = contributors_count
    # 项目url
    item["source_url"] = response.url
    # 跳转url
    ref_url = f"https://api.github.com/repositories/{project_id}"
    item["ref_url"] = ref_url
    # 用ref_url MD5
    item["uuid"] = md5(ref_url)
    # read me内容
    item["readme"] = response.xpath("//div[@data-target='readme-toc.content']").xpath('string(.)').get("")
    # item["readme_html"] = response.xpath(json_path(config, "$.item_info.readme")).get("")
    # 基本信息
    item["website_name"] = 'GitHub'
    item["website_sub_name"] = 'GitHub'
    item["host"] = 'github.com'
    netloc = urlparse(response.url).netloc.replace('www.', '')
    if netloc:
        item["sub_host"] = netloc
    else:
        item["sub_host"] = item["host"]
    item['crawler_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(item)


if __name__ == '__main__':
    hsd()
