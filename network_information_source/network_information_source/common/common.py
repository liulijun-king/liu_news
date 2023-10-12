import datetime
import hashlib
from loguru import logger


class Common:
    def __init__(self):
        pass

    @staticmethod
    def make_md5(raw_str: str):
        """
        MD5加密
        """
        try:
            md5_url = hashlib.md5(raw_str.encode(encoding='UTF-8')).hexdigest()
            return md5_url
        except Exception as e:
            logger.exception(e)
            return ''

    @staticmethod
    def get_now():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


common = Common()
