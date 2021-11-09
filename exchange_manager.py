# -*- coding: utf-8 -*-
# @Time       : 2021/11/9 12:45
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/9
import threading

from exchange_factory import ExchangeFactory
from config import *
from utils.db_module import DbModule
from config.exchange_config import exchanges


class ExchangeManager:
    def __init__(self):
        self.exchange_dict_of_api = {}
        self.cursor = DbModule()
        self.table_name_list = self.get_databse_table_list()
        for [exchange_name, enablement] in exchanges.items():
            if enablement is True:
                self.exchange_dict_of_api[exchange_name] = ExchangeFactory.create(
                    exchange_name=exchange_name)
                if not (exchange_name in self.table_name_list):
                    self.create_table_in_database(exchange_name)

    def start_from_api(self):
        logger_info.info("Create Exchagne Manager instance success And start kline Job from api datasource...")
        self.exchanges_pre_handle()

    @staticmethod
    def exchanges_pre_handle():
        # 此处可以根据指定的交易所获取数据
        if CURRENT_EXCHANGE != "ALL":
            for ex in exchanges.keys():
                exchanges[ex] = True if ex in CURRENT_EXCHANGE.split(',') else False

    def create_table_in_database(self, exchange_name):
        with open(r"scripts/create_table.sql", "r") as f:
            sql = f.read()
            sql_list = sql.split(';')[:-1]
            sql_list = [x.replace('\n', ' ').replace("@exchangeName", exchange_name) if '\n' in x else x.replace(
                "@exchangeName", exchange_name) for x in sql_list]
        for sql_item in sql_list:
            self.cursor.execute(sql_item)

    def get_databse_table_list(self):
        sql = "SELECT relname FROM pg_stat_user_tables;"
        res = self.cursor.execute(sql)
        tables = res["data"].fetchall()
        names = [item[0] for item in tables]
        return names
