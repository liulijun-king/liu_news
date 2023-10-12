from typing import Union, Iterable
from .section_find import SectionFind


def website_section_find(host: Union[str, list], **kwargs) -> Iterable:
    """网站版块信源发现"""
    for info in SectionFind(host, **kwargs).start():
        yield info
