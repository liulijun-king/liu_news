"""
DNS探测
"""
from typing import Any, Dict, Union, Iterable

import dns.resolver
from loguru import logger

from network_information_source.config import settings


class DnsResolver(object):
    """dns解析"""
    RECORD_TYPE = ['a', 'aaaa', 'cname', 'mx', 'ns', 'srv', 'txt', 'soa']

    def __init__(self, host: Union[str, list], thread_count=settings.DNS_THREAD_COUNT, **kwargs):
        self.host = [host] if isinstance(host, str) else host
        self.recursive_server = kwargs.pop('recursive_server', None)
        self.default_recursive_server = kwargs.pop('default_recursive_server', ['114.114.114.114', '8.8.8.8'])
        self.thread_count = thread_count
        self.resolver = dns.resolver.Resolver()

        if self.recursive_server and (not isinstance(self.recursive_server, list)):
            self.recursive_server = [self.recursive_server]
        else:
            self.recursive_server = self.default_recursive_server

    def get_record(self, host: str, record_type: str, lifetime: int = 10, timeout: int = 10) -> Any:
        """获取dns记录"""
        try:
            self.resolver.nameservers = list(set(self.recursive_server))

            # self.resolver.timeout = timeout
            self.resolver.lifetime = lifetime

            result = self.resolver.resolve(host, record_type, raise_on_no_answer=False)

            return result

        except Exception as ex:
            logger.error(f'{ex}')
        return []

    def start(self) -> Iterable:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=self.thread_count) as t:
            all_task = [t.submit(self.__execute__, host)
                        for host in self.host]

            for future in as_completed(all_task):
                yield future.result()

    def __execute__(self, host: str) -> Dict[str, Any]:
        """分别解析多种类型dns记录"""
        infos = {}

        for record_type in self.RECORD_TYPE:
            try:
                result = self.get_record(host, record_type=record_type.upper())
            except Exception as ex:
                logger.error(f'{ex}')
                continue

            infos.update({
                record_type: [val.to_text() for val in result]
            })

        return infos


if __name__ == '__main__':
    dns_resolver = DnsResolver(host=['baidu.com'])
    # dns_resolver.extract_a_record('sina.com')
    for info in dns_resolver.start():
        print(info)
