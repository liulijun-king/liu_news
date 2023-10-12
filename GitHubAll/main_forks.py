#  开发时间：2022/5/12 16:22
#  文件名称：main.py
#  备注：
# -*- coding:utf-8 -*-
import os
from scrapy import cmdline

# os.system('scrapy crawl github_forks')

cmdline.execute("scrapy crawl github_forks".split(' '))
