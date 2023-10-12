import json
import datetime
from typing import Dict, Any

from .common import common
from .net_utils import net_utils
from .legal_verify import *


def format_json(src_json: Dict[str, Any]) -> str:
    return json.dumps(src_json, ensure_ascii=False, indent=4, cls=CJsonEncoder)


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
