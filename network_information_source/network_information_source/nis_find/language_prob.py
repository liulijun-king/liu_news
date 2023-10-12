"""
网站内容语言探测
"""
# encoding:utf-8
import langid
from lxml import etree
from loguru import logger


def language_prob_element(text_string) -> str:
    """提取网页源码内语言标识"""
    lang = ''
    try:
        html = etree.HTML(text_string)
        lang = ''.join(html.xpath('//html/@lang'))
    except Exception as ex:
        logger.error(f'获取语言标识失败')

    return lang


def language_prob(text_string: str) -> str:
    """获取语种"""
    lang = langid.classify(text_string)
    return lang[0] if lang else ''


if __name__ == '__main__':
    print(language_prob(
        '本篇博客主要介绍两款语言探测工具，用于区分文本到底是什么语言，We are pleased to introduce today a new technology'))
