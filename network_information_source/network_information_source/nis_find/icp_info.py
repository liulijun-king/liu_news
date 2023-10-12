"""
域名注册信息
"""
from loguru import logger
from lxml import etree

from network_information_source.common import net_utils


def icp_prob(host: str):
    url = f'https://icp.chinaz.com/{host}'
    headers = {
    }
    icp_info = []
    try:
        r = net_utils.req('GET', url, headers=headers)
        html = etree.HTML(r)
        ul_block_element = html.xpath("//ul[contains(@id,'first')]")

        li_s = [_.xpath('.//li') for _ in ul_block_element][0]

        for li in li_s:
            label = ''.join(li.xpath('./span//text()')).strip()
            content = ''.join(li.xpath('./p//text()')).strip()
            icp_info.append({
                'label': ' '.join(label.split()),
                'content': ' '.join(content.split())
            })

    except Exception as ex:
        logger.error(f'{host} 无ICP信息')

    return icp_info


if __name__ == '__main__':
    print(icp_prob('sina.com'))
