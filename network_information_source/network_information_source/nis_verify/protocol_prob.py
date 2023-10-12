"""
协议探测
"""
from typing import Union
from easy_spider_tool import regx_match
from network_information_source.common import net_utils


# @require('主机，端口检验', lambda args: verify_port(args.port) and verify_domain_name(args.host) or verify_ip_address(args.host))
def protocol_prob(host: str, port: Union[str, int], protocol='https') -> str:
    """支持HTTP/HTTPS协议通信"""
    url = f'{protocol}://{host}:{port}'
    response = net_utils.req('GET', url=url, res_type='content')
    if response:
        return regx_match(r'^(https?):', response.url, first=True, default=False)
    return ''
