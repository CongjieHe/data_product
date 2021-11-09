# -*- coding: utf-8 -*-
# @Time       : 2021/11/6 1:18
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/6

import traceback

import psycopg2
from sqlalchemy import create_engine
from config.db_config import db_setting
from config import *


class DbModule:
    def __init__(self):
        self.db_config = db_setting[RUN_ENV]
        self.conn, self.engine = self._connect_to_db()

    def _connect_to_db(self):
        try:
            engine = create_engine('postgresql://%s:%s@%s:%s/%s' % (
                self.db_config["user"], self.db_config["pwd"], self.db_config["ip"], self.db_config["port"],
                self.db_config["db"]))
            conn = engine.connect()
        except Exception as e:
            exstr = traceback.format_exc()
            logger_error.error(exstr)
            logger_error.error("Connect DB failed")
        else:
            logger_info.debug("Connect DB success")
            return conn, engine

    def execute(self, sql):
        result = {"result": True}
        try:
            data = self.conn.execute(sql)
        except Exception as e:
            result["result"] = False
            result["data"] = e
            logger_error.error("execute %s failed" % sql)
            exstr = traceback.format_exc()
            logger_error.error(exstr)
        else:
            logger_info.debug("execute %s success..." % sql)
            result["data"] = data
        return result

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
