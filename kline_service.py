# -*- coding: utf-8 -*-
# @Time       : 2021/11/10 0:17
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/10

import threading
import time
import datetime
import schedule
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

from config import *
from exchange_manager import ExchangeManager
from utils.db_module import DbModule
from utils.mail_center import EmailCenter

matplotlib.use("Agg")


class KlineService:
    def __init__(self):
        pass

    def start(self):
        logger_info.info("Create kline service instance success and Start Kline Service...")
        self._schedule_manager_start()
        self._heart_beat_send()

    def _schedule_manager_start(self):
        logger_info.info("Schedule manager start success...")
        schedule.every(60).seconds.do(self._heart_beat_send)

        schedule.every().day.at("10:30").do(self.calculate_every_symbol_amount_per_day)
        # TODO:need to improve use trade data to trans kline design
        # 不同数据源，采集频率不一样
        schedule.every().hour.do(self.kline_data_start_from_api)
        self.kline_data_start_from_api()

        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def _heart_beat_send():
        logger_info.info("Heart beat working ,Current Threading Num: " + threading.active_count().__str__())

    @staticmethod
    def kline_data_start_from_api():
        logger_info.info("Kline data job start from api-----------------------------------")
        exchange_manager_instance = ExchangeManager()
        exchange_manager_instance.start_from_api()

    def calculate_every_symbol_amount_per_day(self):
        data = []
        client = DbModule()
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        for exchange in EXCHANGE_LIST:
            for item in EXCHANGE_LIST[exchange]["SYMBOLS"]:
                single = {}
                symbol = item["assert"] + item["to"]
                contract_type = item["type"]
                info = exchange + "_" + symbol + "_" + contract_type.replace("_", "")
                sql = """SELECT count(*) FROM %s WHERE info = '%s' AND "time" BETWEEN '%s 00:00:00' AND '%s 23:59:59'""" % (
                    exchange, info, yesterday, yesterday)
                result = client.execute(sql)
                if result["result"]:
                    result = result["data"].fetchone()
                    amount = result[0]
                else:
                    amount = 0
                single["exchange"] = exchange
                single["symbol"] = symbol
                single["contract_type"] = contract_type
                single["date"] = yesterday
                single["amount"] = amount
                data.append(single)
        data = pd.DataFrame(data)
        data = data[["date", "exchange", "symbol", "contract_type", "amount"]]
        # data.to_sql(KLINE_DAILY_CHECK, client.engine, index=False, if_exists='append')
        client.close()
        data = data[data["amount"] == 0]
        data.reset_index(drop=True, inplace=True)
        logger_info.info("calculate success")
        self.create_kline_amount_table_png(data, yesterday)

    @staticmethod
    def create_kline_amount_table_png(data, date):
        if not isinstance(data, pd.DataFrame):
            logger_error.error("data not DataFrame")
            return False
        if len(data) == 0:
            logger_error.error("data length is zero")
            return False
        data = data[data["amount"] == 0]
        length = len(data)
        height = length * 0.2 + 2 if length > 10 else 5
        fig, ax = plt.subplots(1, 1, figsize=(8, height))
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')
        ax.set_title("%s : total amount is %s" % (date, length))
        ax.table(cellText=data.values, colLabels=data.columns, loc='center')
        fig.tight_layout()
        title = str(date) + ".png"
        path = "static/img/"
        title = path + title
        plt.savefig(title)
        try:
            fp = open(title, 'rb')
            imgs = [fp]
            mail_service = EmailCenter("%s:kline daily amount" % date, "Kline Amount")
            mail_service.send_img(title, imgs)
        except Exception as e:
            logger_error.error("something wrong happened")
            logger_error.error(e)
        return True
