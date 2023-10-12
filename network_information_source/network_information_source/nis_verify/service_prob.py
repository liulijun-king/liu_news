"""
服务探测
"""

from typing import Union
from network_information_source.common import net_utils


# @require('主机，端口检验', lambda args: verify_port(args.port) and verify_domain_name(args.host) or verify_ip_address(args.host))
def service_prob(host: str, port: Union[str, int] = 80, protocol='http'):
    """提供Web服务"""
    url = f'{protocol}://{host}:{port}'
    response = net_utils.req('GET', url=url)
    return True if response else False
