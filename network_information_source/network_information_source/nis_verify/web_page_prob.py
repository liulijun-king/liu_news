"""
页面内容探测
"""
from typing import Union
from network_information_source.common import net_utils


# @require('主机，端口检验',
# lambda args: verify_port(args.port) and verify_domain_name(args.host) or verify_ip_address(args.host))
def web_page_prob(host: str, port: Union[str, int], protocol='http'):
    """提供的是网页（为html语言）"""
    url = f'{protocol}://{host}:{port}'
    response = net_utils.req('GET', url=url, res_type='content')

    content_type = response.headers.get('content-type', '') if response else ''

    if 'text/html' not in content_type:
        return False
    # try:
    #     etree.HTML(response)
    # except Exception as _:
    #     return False

    return True
