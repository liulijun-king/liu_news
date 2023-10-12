"""
网站排名
"""
from lxml import etree
from loguru import logger
from network_information_source.common import net_utils


def extract_alex_ranking(host):
    today_rank = ''
    try:
        url = f'https://alexa.chinaz.com/{host}'
        headers = {
            # 'user-agent': get_user_agent(),
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'referer': 'https://alexa.chinaz.com/',
        }
        r = net_utils.req('GET', url, headers=headers)
        html = etree.HTML(r)
        today_rank = ''.join(html.xpath("//div[@class='rank']/div[@class='item'][1]/p//text()"))
    except(Exception,) as e:
        logger.error(f'alex请求错误：{e}')
    finally:
        return today_rank


if __name__ == '__main__':
    print(extract_alex_ranking('sina.com'))
