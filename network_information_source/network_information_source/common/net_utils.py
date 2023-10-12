from typing import Dict, Union
import requests
import urllib3
from loguru import logger
from requests import Response
from fake_useragent import UserAgent
from tldextract import tldextract


class NetUtils:
    def __init__(self):
        pass

    @staticmethod
    def random_user_agent():
        return {'user-agent': UserAgent().random}

    def req(self, method: str = 'post', url: str = None, headers: Dict[str, any] = None, timeout: int = 5,
            res_type: str = None, retry_num: int = 2, **kwargs) -> Union[Response, str, None]:
        urllib3.disable_warnings()
        method = method.upper()

        if method in ['GET', 'POST']:
            if headers is None:
                headers = self.random_user_agent()

            # print(headers)
            for _ in range(retry_num):
                # noinspection PyBroadException
                try:
                    response = requests.request(method, url=url, headers=headers, verify=False, timeout=timeout,
                                                **kwargs)
                    response.raise_for_status()

                    if response.status_code == 200:
                        response.encoding = 'utf-8'

                        if res_type == 'json':
                            return response.json()

                        if res_type == 'content':
                            return response

                        return response.text
                except requests.HTTPError as ex:
                    logger.error(f"{ex}")
                except Exception as ex:
                    logger.error(f"{ex}")

        logger.error(f"{method.upper()}- {url}")

    @staticmethod
    def get_domain(host: str):
        """获取域名"""
        val = tldextract.extract(host)
        suffix = val.suffix

        domain_name = ''

        if val.subdomain:
            domain_name = f'{val.subdomain}.{val.domain}.{suffix}'

        if not domain_name and val.domain:
            domain_name = f'{val.domain}.{suffix}'

        return domain_name

    @staticmethod
    def get_top_domain(host: str):
        """获取顶级域名"""
        val = tldextract.extract(host)
        suffix = val.suffix

        if val.domain:
            return f'{val.domain}.{suffix}'
        return host

    @staticmethod
    def gen_sub_domain(host: str, prefix='www'):
        val = tldextract.extract(host)
        suffix = val.suffix

        if not val.subdomain:
            # print(val.domain, val.suffix, val.registered_domain, val.ipv4, val.subdomain, val.fqdn)
            return f'{prefix}.{host}'
        else:
            return f'{val.subdomain}.{val.domain}.{suffix}'


net_utils = NetUtils()
