"""
站点描述
"""
from loguru import logger
from lxml import etree

from network_information_source.common import net_utils


def website_desc(url: str) -> str:
    if not url:
        return ''

    headers = {
    }
    desc = ''
    try:
        r = net_utils.req('GET', url, headers=headers)
        html = etree.HTML(r)
        desc = ''.join(html.xpath("//meta[contains(@name,'description')]/@content"))

    except Exception as ex:
        logger.error(f'{url} 无站点描述信息')

    return desc


if __name__ == '__main__':
    print(website_desc('https://www.sina.com.cn'))
