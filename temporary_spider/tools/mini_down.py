# -*- coding: utf-8 -*-
# @Time    : 2023/10/10 0010 18:17
# @Author  : Liu
# @Site    : 
# @File    : mini_down.py
# @Software: PyCharm
import hashlib
from io import BytesIO

from minio import Minio


class MiniDown(object):
    def __int__(self):
        self.minio_client = Minio('8.130.28.33:8091',
                                  access_key='minioadmin',
                                  secret_key='minioadmin',
                                  secure=False)

    def upload_file(self, file_name, content):
        minio_client = Minio('8.130.28.33:8091',
                             access_key='minioadmin',
                             secret_key='minioadmin',
                             secure=False)
        data = BytesIO(content)
        name = minio_client.put_object('zhongxincaiji', file_name, data=data, length=len(content))
        print(name)



def get_md5(val):
    """把目标数据进行哈希，用哈希值去重更快"""
    md5 = hashlib.md5()
    md5.update(val.encode('utf-8'))
    return md5.hexdigest()


if __name__ == '__main__':
    import requests

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    url = 'https://thumbor.ftacademy.cn/unsafe/738x415/picture/9/000177349_piclink.jpg'
    response = requests.get(url, headers=headers)
    md = MiniDown()
    md.upload_file(f"{get_md5(url)}.jpg", response.content)
