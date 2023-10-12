# -*- coding = utf-8 -*-
# @Time : 2022/3/11 10:57
# @File : create_and_update.py
# @Software : PyCharm
# @Desc : 数据创建与更新
from enum import Enum
from typing import Dict

from sqlalchemy.orm import Session, sessionmaker
from loguru import logger

from sql_alchemy.models import engine, GitHubForksRelation

SessionLocal = sessionmaker(bind=engine)


class TableEnum(Enum):
    """数据表对应映射的枚举"""
    git_hub_forks_relation = GitHubForksRelation


def get_db(func):
    def make_decorator(*args, **kwargs):
        db = SessionLocal()
        kwargs.update({'db': db})

        try:
            finally_func = func(*args, **kwargs)
            return finally_func
        except Exception as e:
            logger.error(f'{e}')
            db.rollback()
        finally:
            db.close()

    return make_decorator


@get_db
def execute_sql(sql: str, db: Session = None):
    """执行原生sql语句"""
    cursor = db.execute(sql)
    if 'select' in sql or 'SELECT' in sql:
        query_result = cursor.fetchall()
        return query_result


@get_db
def create_post_data(table_name: str, data: Dict, filters: Dict, db: Session = None, up: bool = False):
    table = TableEnum[table_name].value

    is_exist = db.query(table).filter_by(**filters)
    if is_exist.first() is None:
        post = table(**data)
        db.add(post)
        db.commit()

    elif is_exist.first() and up is True:
        is_exist.update(data)
        db.commit()
        logger.info(f'数据更新成功')
    else:
        logger.debug(f'数据已存在，不进行处理')
