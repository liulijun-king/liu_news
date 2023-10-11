# -*- coding: utf-8 -*-
# @Time    : 2023/3/3 0003 16:32
# @Author  : Liu
# @Site    : 
# @File    : news_main.py
# @Software: PyCharm
from spider.executive_yuan import ExecutiveYuan
from spider.mm import MonitorMer
from spider.morning_paper import MorningPaper
from spider.president_office import PresidentOffice

if __name__ == '__main__':
    ExecutiveYuan().id_split()
    PresidentOffice().id_split()
    MorningPaper().id_split()
    MonitorMer().id_split()
