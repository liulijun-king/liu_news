"""
输入域名，需要主动检测域名是否提供Web服务，并判断Web服务响应的数据是否为html类型
需求背景：需要对每日亿级规模的域名判定是否为具有业务意义的“网站”，“网站”的特征为：
1)支持HTTP/HTTPS协议通信，
2）提供Web服务，
3）Web服务提供的数据为浏览器可解析渲染的网页，而非Web API或图床等二进制资源
"""
from typing import Union, Iterable, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from network_information_source.config import settings
from network_information_source.common import net_utils
from network_information_source.nis_verify.protocol_prob import protocol_prob
from network_information_source.nis_verify.service_prob import service_prob
from network_information_source.nis_verify.web_page_prob import web_page_prob


class WebsiteProbe(object):

    def __init__(self, host: Union[str, list], port: int = 443, thread_count=settings.WEB_SITE_PROBE_THREAD_COUNT,
                 **kwargs):
        self.host = [host] if isinstance(host, str) else host
        self.port = port
        self.thread_count = thread_count
        self.kwargs = kwargs

    def start(self) -> Iterable:
        with ThreadPoolExecutor(max_workers=self.thread_count) as t:
            all_task = [t.submit(self.__execute__, host, self.port) for host in self.host]

            for future in as_completed(all_task):
                yield future.result()

    def __execute__(self, host: str, port: int, prefix: str = 'www') -> Dict[str, Any]:
        try:

            sub_domain = net_utils.gen_sub_domain(host, prefix)

            protocol = protocol_prob(sub_domain, port) or protocol_prob(sub_domain, 80, protocol='http')
            port = self.port if 'https' in protocol else 80
            return {
                'is_html': all([
                    service_prob(sub_domain, port, protocol),
                    web_page_prob(sub_domain, port, protocol),
                ]) if protocol else False,
                'protocol': protocol if protocol else 'http',
                'sub_domain': sub_domain,
                'host': host,
                'port': port,
                **self.kwargs
            }
        except Exception as ex:
            logger.error(f'{ex}')

    def probe(self, host, port, prefix='www') -> Dict[str, Any]:
        return self.__execute__(host, port, prefix)
