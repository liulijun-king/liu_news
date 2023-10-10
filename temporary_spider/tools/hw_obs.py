# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 0016 15:20
# @Author  : Liu
# @Site    : 
# @File    : hw_obs.py
# @Software: PyCharm
from obs import ObsClient


class HwObs(object):
    def __init__(self):
        self.conn = self.get_conn()

    @staticmethod
    def get_conn():
        obs_conn = ObsClient(
            access_key_id='OOW0I3UH7ENEO2CV6GWN',
            secret_access_key='evEO6Q8nv81LTyVnLBiFCvE6ZvjQBtIfvfVxSM6a',
            server='obs.cn-southwest-2.myhuaweicloud.com'
        )
        return obs_conn

    def up_data(self, file_name, content):
        try:
            resp = self.conn.putContent('zhongxincaiji', file_name, content)
            if resp.status < 300:
                # 返回请求Id
                return resp.requestId
            else:
                return None
        except Exception as e:
            self.conn = self.get_conn()
