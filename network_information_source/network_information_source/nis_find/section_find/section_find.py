"""
发现域名的板块信息
"""
from typing import Union, Iterable, Dict, Any
from loguru import logger
from network_information_source.config import settings
from network_information_source.common import net_utils
from network_information_source.nis_utils.net import get_page_source, extract_url


class SectionFind(object):
    def __init__(self, host: Union[str, list], port: int = 443, thread_count=settings.WEBSITE_THREAD_COUNT, **kwargs):
        self.host = [host] if isinstance(host, str) else host
        self.port = port
        self.thread_count = thread_count
        self.kwargs = kwargs

    def start(self) -> Iterable:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=self.thread_count) as t:
            all_task = [t.submit(self.__execute__, host)
                        for host in self.host]

            for future in as_completed(all_task):
                yield future.result()

    def __execute__(self, host, prefix='www') -> Dict[str, Any]:
        domain_name = net_utils.get_domain(host)

        # protocol = protocol_prob(sub_domain, 443) or protocol_prob(sub_domain, 80, protocol='http')

        # 获取源码
        url = host

        urls = []
        try:
            response_text = get_page_source(url)
            urls = extract_url(response_text)
        except Exception as ex:
            logger.error(f'{ex}')

        return {
            'host': host,
            'urls': urls,
            **self.kwargs
        }
