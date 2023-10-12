#  开发时间：2022/6/27 14:06
#  文件名称：item_config.py
#  备注：字段设置
def item_main():
    """
    项目字段设置
    :return:
    """
    item = {
        # 采集关键字
        "module_name": "",
        # fork的原项目ID
        "fork_original_project": "",
        # fork的根项目ID
        "fork_root_project": "",
        # 项目名
        "project_name": "",
        # 用户id
        "user_id": "",
        # 项目作者
        "author": "",
        # 创建时间
        "create_time": "",
        # 项目提交次数
        "commit_count": "",
        # 项目标签
        "tags": "",
        # 项目星数
        "stars_count": "",
        # 项目浏览数
        "watch_count": "",
        # 项目fork数
        "forks_count": "",
        # 项目贡献数
        "contributors_count": "",
        # 项目简介
        "abstract": "",
        # read me内容
        "readme": "",
        # 基本信息
        "source_url": "",
        # 接口url
        "ref_url": "",
        # github二月新增需求
        "host_ip": "140.82.121.4",
        "AlexaInfo": 36,
        "host": "",
        "sub_host": "",
        "website_name": "",
        "website_sub_name": "",
        "uuid": "",
        "crawler_time": "",
        "insert_time": "",
        "update_time": "",
    }
    return item


def user_info():
    """
    用户信息字段
    :return:
    """
    item = {
        # 用户id
        "user_id": "",
        # 昵称
        "user_name": "",
        # 头像
        "head_img": "",
        # 粉丝数
        "fans_count": "",
        # 关注量
        "follow_count": "",
        # 简介
        "abstract": "",
        # 所在机构
        "organization": "",
        # 所在地址
        "address": "",
        # 邮箱
        "email": "",
        # 个人主页url
        "user_url": "",
        # twitter url
        "twitter_url": "",
        # 星数
        "stars_count": "",
        # 基本信息
        "source_url": "",
        "uuid": "",
        "crawler_time": "",
        "insert_time": "",
        "update_time": "",
    }
    return item


def forks_relation():
    """
    forks关系表字段
    :return:
    """
    item = {
        # 项目id
        "project_id": "",
        # 姓名
        "user_name": "",
        # 头像
        "head_img": "",
        # 个人主页url
        "user_url": "",
        # 用户id
        "user_id": "",
        # 子项目名
        "sub_project_name": "",
        # 子项目链接
        "sub_project_url": "",
        # 基本信息
        "source_url": "",
        "uuid": "",
        "crawler_time": "",
        "insert_time": "",
        "update_time": "",
    }
    return item


def redis_info():
    """
    存入redis的字段
    :return:
    """
    item = {
        # 入库表名
        "table_name": "",
        # 项目id
        "project_id": "",
        # github用户主页
        "user_url": "",
    }
    return item
