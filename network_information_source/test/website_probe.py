from easy_spider_tool import format_json

from network_information_source.nis_verify import WebsiteProbe

# for task in verify_test_tasks[0]:
#     for info in website_probe(**extract_task(task)):
#         print(info)

if __name__ == '__main__':
    for info in WebsiteProbe(host=['console-prod-images.playbattlegrounds.com']).start():
        print(format_json(info))