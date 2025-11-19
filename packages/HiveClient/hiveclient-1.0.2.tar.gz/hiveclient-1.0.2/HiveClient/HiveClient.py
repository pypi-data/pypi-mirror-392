# 以下是修改后的HiveClient.py（与run_sql函数适配，并统一参数为小写）
# -*- coding:utf-8 -*-
from functools import wraps
from itertools import zip_longest
from pyhive import hive
import pandas as pd
import warnings
import logging
import re
import time
from pyhive.exc import OperationalError, NotSupportedError
from pandas.errors import DatabaseError

warnings.filterwarnings("ignore")


def extract_core_hive_error(err_msg):
    """提取Hive核心错误信息"""
    if not err_msg:
        return "未知Hive错误"

    if 'errorMessage="' in err_msg:
        match = re.search(r'errorMessage="([^"]+)"', err_msg)
        if match:
            return match.group(1)

    if 'SemanticException' in err_msg:
        match = re.search(r'SemanticException \[.*?\]: (.*?)(?=:|\n|")', err_msg)
        if match:
            return match.group(1)

    return err_msg[:500] + ("..." if len(err_msg) > 500 else "")


class Retry(object):
    """带延迟的重试装饰器"""

    def __init__(self, retry=3, delay=2):
        self.retry = retry
        self.delay = delay

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            retry_count = 0
            last_full_error = "未知错误"
            while retry_count < self.retry:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    full_err = str(e)
                    last_full_error = full_err
                    core_err = extract_core_hive_error(full_err)
                    # print(f"第 {retry_count + 1} 次执行失败：")
                    # print(f"核心错误：{core_err}")

                    if retry_count < self.retry - 1:
                        print(f"将在 {self.delay} 秒后重试...\n")
                        time.sleep(self.delay)

                    args[0].init_connection()
                    retry_count += 1

            core_err = extract_core_hive_error(last_full_error)
            raise Exception(
                f"多次重试仍然失败（共 {self.retry} 次）\n"
                f"核心错误：{core_err}\n"
                f"Hive详细错误：{last_full_error}"
            )

        return wrapped_func


class HiveClient(object):
    """Hive客户端工具类，支持查询、DML操作及pandas数据返回"""

    def __init__(self, host, port, username, password, auth='CUSTOM'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = auth
        self.conn = None
        self.init_connection()

    def init_connection(self):
        """初始化或重建Hive连接"""
        try:
            if self.conn:
                self.conn.close()
            self.conn = hive.Connection(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                auth=self.auth
            )
            print("Hive连接初始化成功")
        except Exception as e:
            full_err = str(e)
            raise Exception(f"Hive连接建立失败：{full_err}")

    @Retry()
    def dql(self, query_sql):
        """执行单条DQL查询，返回字典列表"""
        datas = []
        cursor = self.conn.cursor()
        try:
            cursor.execute(query_sql)
            columns = [col[0] for col in cursor.description]
            for result in cursor.fetchall():
                item = dict(zip_longest(columns, result))
                datas.append(item)
            return datas
        finally:
            cursor.close()

    @Retry()
    def dml(self, query_sql):
        """执行单条DML语句"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(query_sql)
            print("DML语句执行成功")
        finally:
            cursor.close()

    @Retry()
    def dmls(self, query_sql):
        """执行多条以分号分隔的DML语句"""
        sql_list = [sql.strip() for sql in re.split(r';\s*', query_sql) if sql.strip()]

        for sql in sql_list:
            cursor = self.conn.cursor()
            try:
                cursor.execute(sql)
                print(f"执行SQL成功：{sql[:50]}...")
            finally:
                cursor.close()

    @Retry()
    def pd_dql(self, query_sql):
        """执行单条DQL查询，返回pandas DataFrame"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(query_sql)
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            print(f"查询成功，返回 {len(df)} 条数据")
            return df
        finally:
            cursor.close()

    @Retry()
    def pd_dqls(self, query_sql):
        """执行多条DML+最后一条DQL，返回DataFrame"""
        sql_list = [sql.strip() for sql in query_sql.split(';') if sql.strip()]
        if len(sql_list) < 1:
            raise Exception("未找到有效SQL语句")

        # 执行前N-1条DML
        for sql in sql_list[:-1]:
            cursor = self.conn.cursor()
            try:
                cursor.execute(sql)
                print(f"执行前置SQL成功：{sql[:50]}...")
            finally:
                cursor.close()

        # 执行最后一条查询
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql_list[-1])
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            print(f"最终查询成功，返回 {len(df)} 条数据")
            return df
        finally:
            cursor.close()

    def close(self):
        """手动关闭连接"""
        if self.conn:
            self.conn.close()
            print("Hive连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()