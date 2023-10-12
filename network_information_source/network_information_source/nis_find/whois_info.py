"""
whois信息
"""
import whois
from dpcontracts import require
from loguru import logger

from network_information_source.common import verify_domain_name, verify_url


@require('域名校验', lambda args: verify_domain_name(args.host) or verify_url(args.host))
def get_whois_info(host: str):
    """whois信息查询"""
    whois_info = {}
    try:
        info = whois.whois(host)
        whois_info = info
        return whois_info
    except Exception as ex:
        logger.error(f'{ex}')
        return whois_info


if __name__ == '__main__':
    print(get_whois_info('sina.com'))
