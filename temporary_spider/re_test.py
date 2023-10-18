# -*- coding: UTF-8 -*-


import requests

proxies = {
    'http': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333',
    'https': 'http://liulijun584268-zone-custom:9TL39WvUnboIdOI@proxy.ipidea.io:2333'
}

response = requests.get('http://ipinfo.ipidea.io', proxies=proxies)
print(response.content.decode())

# curl -x proxy.ipidea.io:2333 -U "liulijun584268-zone-custom:9TL39WvUnboIdOI" ipinfo.ipidea.io
