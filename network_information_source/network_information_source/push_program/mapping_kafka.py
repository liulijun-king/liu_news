from typing import Dict, Any
from loguru import logger
from easy_spider_tool import jsonpath
from network_information_source.common import common
from network_information_source.config import settings


class MappingKafka:
    def __init__(self, src: Dict[str, Any] = None):
        """
        推送kafka字段映射
        @param src: 任务输出结果
        @return:
        """
        if src is None:
            src = {}
        self.src = src

        self.infos = {}

        # 排除字段
        self.exp_fields = ['whois']

    def extract_data(self) -> Dict[str, Any]:
        """通用提取"""
        self.infos.update(self.src)

        for method in [
            self.extract_completion_time,
            self.extract_recursive_server,
            self.extract_gregion,

            self.extract_is_html,

            self.extract_website_name,
            self.extract_whois,
            self.extract_access,
            self.extract_dns,
        ]:
            try:
                info = method()
            except Exception as ex:
                logger.error(f'{ex}')
                continue

            self.infos.update(info)

        [self.infos.pop(field) for field in self.exp_fields if field in self.infos]

        return self.infos

    def extract_verify_data(self) -> Dict[str, Any]:
        """提取验证需求数据"""
        self.extract_data()

        for method in [
            self.extract_is_html,
        ]:
            try:
                info = method()
            except Exception as ex:
                logger.error(f'{ex}')
                continue

            self.infos.update(info)

        return self.infos

    def extract_find_data(self) -> Dict[str, Any]:
        """提取发现需求数据"""
        self.extract_data()

        for method in [
            self.extract_website_name,
            self.extract_whois,
            self.extract_access,
            self.extract_dns,
        ]:
            try:
                info = method()
            except Exception as ex:
                logger.error(f'{ex}')
                continue

            self.infos.update(info)

        return self.infos

    @staticmethod
    def extract_gregion() -> Dict[str, Any]:
        """区分境内外"""
        return {
            'gregion': settings.REGION.name
        }

    @staticmethod
    def extract_completion_time() -> Dict[str, Any]:
        return {
            'completion_time': common.get_now()
        }

    def extract_is_html(self) -> Dict[str, Any]:
        return {
            'is_html': self.src.get('is_html', '')
        }

    def extract_recursive_server(self) -> Dict[str, Any]:
        return {
            'recursive_server': self.src.get('recursive_server', [])
        }

    def extract_whois(self) -> Dict[str, Any]:
        whois_info = self.src.get('whois', {})

        whois_emails = whois_info.get('emails', [])
        if whois_emails and isinstance(whois_emails, str):
            whois_emails = [whois_emails]
            whois_info.update({'emails': whois_emails})

        return {f'whois_{k}': v for k, v in whois_info.items()}

    def extract_website_name(self) -> Dict[str, Any]:
        return {
            'website_name': jsonpath(self.src.get('website_name', {}), '$.[?(@.label=="网站名称")].content', first=True,
                                     default='')
        }

    def extract_access(self) -> Dict[str, Any]:
        return {
            'access': self.src.get('access', [{}])[0].get('is_html', '')
        }

    def extract_dns(self) -> Dict[str, Any]:
        return {
            'dns': jsonpath(self.src.get('dns', {}), '$.*.a[*]', first=False, default=[])
        }
