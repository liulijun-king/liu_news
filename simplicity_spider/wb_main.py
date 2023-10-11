# -*- coding: utf-8 -*-
# @Time    : 2023/2/19 0019 10:32
# @Author  : Liu
# @Site    : 
# @File    : wb_main.py
# @Software: PyCharm
from spider.weibo import Wb
from tools.new_mysql import DB

if __name__ == '__main__':
    db = DB()
    gf = Wb(mysql_conn=db)
    gf.id_split()
    # list_rw = ['https://weibo.com/ttarticle/p/show?id=2309404869050093142371']
    # for li_ in list_rw:
    #     gf.entity_spider(li_)
    #     break
