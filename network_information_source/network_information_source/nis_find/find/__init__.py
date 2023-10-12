from typing import Union, Iterable
from .find import WebsiteFind


def website_find(host: Union[str, list], **kwargs) -> Iterable:
    """网站元信息 采集程序入口"""
    for info in WebsiteFind(host, **kwargs).start():
        yield info
