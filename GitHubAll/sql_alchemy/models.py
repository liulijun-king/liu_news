# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, Index, String, TIMESTAMP, Text, text, create_engine
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, MEDIUMTEXT, TINYINT
from sqlalchemy.ext.declarative import declarative_base

DB_URI = 'mysql+pymysql://wg_dba:wgdb%252022@140.210.219.168:3306/CenterProject'

engine = create_engine(DB_URI, pool_size=5, pool_recycle=1, pool_timeout=30)
Base = declarative_base()
metadata = Base.metadata


class GitHubForksRelation(Base):
    __tablename__ = 'git_hub_forks_relation'
    __table_args__ = {'comment': 'GitHub：forks用户信息表'}

    id = Column(BIGINT(20), primary_key=True, comment='数据自增主键ID')
    project_id = Column(String(255), nullable=False, comment='项目id')
    user_name = Column(String(255), nullable=False, comment='姓名')
    head_img = Column(Text, comment='头像')
    sub_project_name = Column(String(255), comment='子项目名')
    sub_project_url = Column(Text, comment='子项目链接')
    user_url = Column(Text, comment='个人主页url')
    user_id = Column(String(255), comment='用户链接的md5')
    source_url = Column(Text, comment='文章URL')
    uuid = Column(String(255), nullable=False, unique=True, comment='个人主页和子项目名的MD5')
    crawler_time = Column(TIMESTAMP, comment='采集该文章的时间点；格式为 yyyy-MM-dd HH:mm:ss')
    insert_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment='入库时间')
    update_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
