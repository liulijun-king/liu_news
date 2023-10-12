import re
from typing import List, Iterable

from dpcontracts import require
from loguru import logger
from requests import Response
from network_information_source.common import net_utils, verify_url, verify_domain_name, common

url_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', re.I)


@require('验证url', lambda args: verify_url(args.url) or verify_domain_name(args.url))
def get_page_source(url: str, **kwargs) -> str:
    return net_utils.req(method='get', url=url, res_type=None, **kwargs)


@require('验证url', lambda args: verify_url(args.url))
def get_page_response(url: str, **kwargs) -> Response:
    return net_utils.req(method='get', url=url, res_type='response', **kwargs)


def extract_url(string: str) -> List[str]:
    """提取页面内所有url"""
    urls = []
    if string:
        try:
            urls = url_regex.findall(string)
        except Exception as ex:
            logger.error(f'{ex}')

    return list(set(urls))


# @require('验证域名', lambda args: verify_domain_name(args.host))
def enumerate_domain_name(host: str, file_path: str = None, src_type: str = 'from_file') -> Iterable:
    """枚举二级域名"""
    # top_domain = net_utils.get_domain(host)
    host = host.replace('*', '')
    try:
        if src_type == 'from_file':
            if file_path is None or common.exits_file(file_path) is False:
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    sub = line.strip()
                    yield f'{sub}{host}'
        elif src_type == 'from_redis':
            pass
    except Exception as ex:
        logger.error(f'{ex}')
