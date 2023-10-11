# -*- coding: utf-8 -*-
# @Time    : 2023/1/16 0016 10:05
# @Author  : Liu
# @Site    : 
# @File    : new_mysql.py
# @Software: PyCharm
# -*-coding:utf-8-*-
import pymysql
from DBUtils.PooledDB import PooledDB

from settings.db_config import formal_db
from loguru import logger


class DB(object):
    """docstring for DbConnection"""
    __pool = None

    def __init__(self):
        self.pool = DB.__get_conn_pool()

    @staticmethod
    def __get_conn_pool():
        if DB.__pool is None:
            try:
                DB.__pool = PooledDB(creator=pymysql, host=formal_db.get("host", "host"),
                                     port=int(formal_db.get("port", "port")),
                                     user=formal_db.get("user", "user"), passwd=formal_db.get("password", "password"),
                                     db=formal_db.get("database", "database"), charset=formal_db.get("charset", "charset"))
            except Exception as e:
                logger.error("%s : %s" % (Exception, e))
        return DB.__pool

    def _get_connection(self):
        conn = self.pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def _close_connection(self, conn, cursor):
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    def query_sql(self, sql, params=None):
        conn, cursor = self._get_connection()
        try:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            self._close_connection(conn, cursor)
        except Exception as e:
            self._close_connection(conn, cursor)
            logger.error(str(e))
            raise Exception("database execute error")
        return result

    def execute_sql(self, sql, params=None):
        conn, cursor = self._get_connection()
        try:
            cursor.execute(sql, params)
            result = cursor.lastrowid
            conn.commit()
            self._close_connection(conn, cursor)
        except Exception as e:
            conn.rollback()
            self._close_connection(conn, cursor)
            logger.error(str(e))
            raise Exception("database commit error")
        return result

    def update_sql(self, sql, params=None):
        conn, cursor = self._get_connection()
        try:
            result = cursor.execute(sql, params)
            conn.commit()
            self._close_connection(conn, cursor)
        except Exception as e:
            conn.rollback()
            self._close_connection(conn, cursor)
            logger.error(str(e))

            raise Exception("database commit error")
        return result
