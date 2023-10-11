# -*- coding: utf-8 -*-
# @Time    : 2023/10/10 0010 18:17
# @Author  : Liu
# @Site    : 
# @File    : mini_down.py
# @Software: PyCharm
from io import BytesIO

from minio import Minio


class MiniDown(object):
    def __int__(self):
        self.minio_client = self.get_conn()

    def get_conn(self):
        mn = Minio('8.130.28.33:8091',
                   access_key='minioadmin',
                   secret_key='6zeRzJrsfN56',
                   secure=False)
        return mn

    def upload_file(self, file_name, content):
        try:
            data = BytesIO(content)
            self.minio_client.put_object('zhongxincaiji', file_name, data=data, length=len(content))
        except Exception:
            self.minio_client = self.get_conn()
