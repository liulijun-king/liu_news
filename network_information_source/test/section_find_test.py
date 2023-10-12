from easy_spider_tool import format_json, current_date

from network_information_source.nis_find import website_section_find
from network_information_source.nis_utils import kafka_utils

topic = 'topic_c1_original_websiteSection_dis'

if __name__ == '__main__':
    for info in website_section_find(host='https://www.qq.com'):
        info.update({
            'insert_time': current_date()
        })
        print(format_json(info))
        kafka_utils.push_new_server([info], topic)
