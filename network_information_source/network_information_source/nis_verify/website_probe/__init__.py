from typing import Union, Iterable
from .website_probe import WebsiteProbe


def website_probe(host: Union[str, list], port: int = 443, **kwargs) -> Iterable:
    """网站检测"""

    for info in WebsiteProbe(host, port, **kwargs).start():
        yield info
