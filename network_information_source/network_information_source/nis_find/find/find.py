"""
输入域名，需要采集并推送以下信息：
1.域名（domain，类型string，与输入相同）
2.域名对应网站名称（name，类型string）
3.网站名称中文翻译（nameCh，类型string）
4.网站简介（desc，类型string）
5.首页URL（url，类型string）
6.采集时间（gt，类型long，10位时间戳）
7.网站语种（lang，类型string）
8.Whois信息（registrant,registrant_contact_email, sponsoring_register, domain_status, DNSSEC，类型string）----这个数据和前期做的网络资源发现属于哪个？
9.Alexa排名（alexaRank,类型string）
10.Web服务可访问标记（access，类型bool）
11.Dns解析记录（ip，类型array[string]） ----是否可以通过域名解析接口调用

"""
from typing import Union, Iterable, Dict, Any

from lxml import etree
from easy_spider_tool import jsonpath

from network_information_source.config import settings
from network_information_source.nis_verify import WebsiteProbe, protocol_prob
from network_information_source.nis_find.website_desc import website_desc
from network_information_source.nis_find.alex_rank import extract_alex_ranking
from network_information_source.nis_find.dns_info import DnsResolver
from network_information_source.nis_find.icp_info import icp_prob
from network_information_source.nis_find.language_prob import language_prob, language_prob_element
from network_information_source.nis_find.whois_info import get_whois_info
from network_information_source.common import net_utils


class WebsiteFind(object):
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
        sub_domain = net_utils.gen_sub_domain(host, prefix)

        icp_out = icp_prob(sub_domain)

        index_url = jsonpath(icp_out, '$.[?(@.label=="网站首页网址")].content', first=True, default='')

        if not index_url:
            index_url = host

        sub_domain = net_utils.gen_sub_domain(index_url, prefix)

        protocol = protocol_prob(sub_domain, 443) or protocol_prob(sub_domain, 80, protocol='http')

        port = 443 if protocol in 'https' else 80

        language_prob_out = ''
        if protocol:
            index_url = f'{protocol}://{sub_domain}'

            response_text = net_utils.req('GET', index_url)

            text = ''.join(etree.HTML(response_text).xpath('//p//text()')) if response_text else ''

            language_prob_out = language_prob_element(response_text) if response_text else ''
            language_prob_out = language_prob(text or response_text) if not language_prob_out and response_text else ''
        else:
            index_url = ''

        return {
            'website_name': icp_out,
            'index_url': index_url,
            'website_desc': website_desc(index_url) if index_url else '',
            'lang': language_prob_out,
            'whois': get_whois_info(domain_name),
            'alexa_rank': extract_alex_ranking(domain_name),
            'access': list(WebsiteProbe(domain_name).start()) if protocol else {},
            'dns': list(DnsResolver(domain_name).start()),
            'host': host,
            **self.kwargs
        }
