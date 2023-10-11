# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 0016 15:20
# @Author  : Liu
# @Site    : 
# @File    : hw_obs.py
# @Software: PyCharm
from io import BytesIO

from minio import Minio


class HwObs(object):
    def __int__(self):
        self.minio_client = self.get_conn()

    @staticmethod
    def get_conn():
        mn = Minio('8.130.28.33:8091',
                   access_key='minioadmin',
                   secret_key='6zeRzJrsfN56',
                   secure=False)
        return mn

    def up_data(self, file_name, content):
        try:
            data = BytesIO(content)
            self.minio_client.put_object('zhongxincaiji', file_name, data=data, length=len(content))
        except Exception:
            self.minio_client = self.get_conn()
