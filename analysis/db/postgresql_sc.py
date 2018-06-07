# coding=utf-8
# author="Jianghua Zhao"
import sys
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor, RealDictCursor
from singleton import Singleton
from config import config

from db_sc import DBInterface

reload(sys)
sys.setdefaultencoding('utf-8')


def generate_sql_string(sql_type, table_name, dict_data=None, dict_condition=None):
    """
    generate sql string for postgresql operation
    :param sql_type: INSERT, SELECT, UPDATE, DELETE
    :param table_name:
    :param dict_data:
    :param dict_condition:
    :return:
    """
    data_keys, data_values = [], []
    if isinstance(dict_data, dict):
        for key, value in dict_data.items():
            data_keys.append(key)
            if isinstance(value, (str, unicode)):
                value = value.replace("'", '"')
                value = "'{0}'".format(value.encode("utf-8"))
            elif isinstance(value, (int, long, float)):
                value = str(value)
            else:
                raise ValueError("value type error: %s" % (str(type(value))))
            data_values.append(value)

    condition_keys, condition_values = [], []
    if isinstance(dict_condition, dict):
        for key, value in dict_condition.items():
            condition_keys.append(key)
            if isinstance(value, (str, unicode)):
                value = value.replace("'", '"')
                value = "'{0}'".format(value.encode("utf-8"))
            elif isinstance(value, (int, long, float)):
                value = str(value)
            else:
                raise ValueError("value type error: %s" % (str(type(value))))
            condition_values.append(value)

    sql = ""
    if sql_type == "INSERT":
        data_keys = ",".join(data_keys)
        data_values = "(" + ",".join(data_values) + ")"
        if len(data_keys) == 0:
            raise Exception("insert nothing")
        else:
            sql = "INSERT INTO {0}({1}) VALUES {2}".format(table_name, data_keys, data_values)
    elif sql_type == "SELECT":
        conditions = zip(condition_keys, condition_values)
        conditions = " and ".join(["=".join(x) for x in conditions])
        if len(conditions) == 0:
            sql = "SELECT * FROM {0};".format(table_name)
        else:
            sql = "SELECT * FROM {0} WHERE {1};".format(table_name, conditions)
    elif sql_type == "UPDATE":
        set_values = zip(data_keys, data_values)
        set_values = ",".join(["=".join(x) for x in set_values])
        conditions = zip(condition_keys, condition_values)
        conditions = " and ".join(["=".join(x) for x in conditions])
        if len(set_values) == 0 or len(conditions) == 0:
            raise Exception("there is not update value or condition")
        else:
            sql = "UPDATE {0} SET {1} WHERE {2};".format(table_name, set_values, conditions)
    elif sql_type == "DELETE":
        conditions = zip(condition_keys, condition_values)
        conditions = " and ".join(["=".join(x) for x in conditions])
        if len(conditions) == 0:
            raise Exception("no delete condition")
        else:
            sql = "DELETE FROM {0} WHERE {1}; ".format(table_name, conditions)
    # print sql
    return sql


class PostgresqlUtil(DBInterface):
    def __init__(self):
        super(PostgresqlUtil, self).__init__()
        self.conn_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=32,
            database=config.POSTGRESQL_DATABASE,
            user=config.POSTGRESQL_USER_NAME,
            password=config.POSTGRESQL_PASSWORD,
            host=config.POSTGRESQL_HOST,
            port=config.POSTGRESQL_PORT
        )

    def get_conn(self):
        conn = self.conn_pool.getconn()
        return conn

    def put_conn(self, conn):
        self.conn_pool.putconn(conn)

    def close(self):
        self.conn_pool.closeall()

    # 插入
    def insert(self, table, data, **kwargs):
        insert_sql = generate_sql_string("INSERT", table, data)
        conn = self.get_conn()
        cur = conn.cursor()

        try:
            cur.execute(insert_sql)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.commit()
            self.put_conn(conn)

    # 查找
    def select(self, table, condition, **kwargs):
        select_sql = generate_sql_string("SELECT", table, dict_condition=condition)
        conn = self.get_conn()
        cur = conn.cursor()

        res = []
        try:
            cur.execute(select_sql)
            res = cur.fetchall()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.commit()
            self.put_conn(conn)
        return res

    # 删除
    def delete(self, table, condition, **kwargs):
        delete_sql = generate_sql_string("DELETE", table, dict_condition=condition)
        conn = self.get_conn()
        cur = conn.cursor()

        try:
            cur.execute(delete_sql)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.commit()
            self.put_conn(conn)

    # 修改
    def update(self, table, condition, data, upsert=False, **kwargs):
        item = self.select(table, condition)
        if len(item) == 0 and upsert is False:
            raise ValueError()
        elif len(item) == 0 and upsert is True:
            self.insert(table, data)
        else:  # len(item) > 0
            update_sql = generate_sql_string("UPDATE", table, data, condition)
            conn = self.get_conn()
            cur = conn.cursor()

            try:
                cur.execute(update_sql)
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cur.close()
                conn.commit()
                self.put_conn(conn)

