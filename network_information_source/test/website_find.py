import json

from network_information_source.common import CJsonEncoder
from network_information_source.nis_find import website_find

if __name__ == '__main__':
    for info in website_find(host='sina.com'):
        print(json.dumps(info, indent=4, ensure_ascii=False, cls=CJsonEncoder))
