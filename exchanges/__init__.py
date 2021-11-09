# -*- coding: utf-8 -*-
# @Time       : 2021/11/6 1:16
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/6

import traceback
import time
import pandas as pd
from config import *
from config.global_config import *
from utils.db_module import DbModule
from utils.delivery_date import DeliveryDate
from abc import ABCMeta, abstractmethod


class ExchangeBase(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name
        self.data_type = ""
        self.last_update_time = ""
        self.max_re_pull_times = 3
        self.request_time_delt = 1  # ms
        self.time_out = 5

        self.headers = {}
        self.success_lst = []
        self.failed_lst = set()

        self.cursor = self.get_db_cursor()
        self.exchange_config = self.get_exchange_config()
        self.current_hour_timestamp = DeliveryDate.get_current_hour_start_timestamp()

    def kline_job_start(self):
        def kline_job_start(self):
            logger_info.debug("%s threading create success...." % self.name)
            try:
                start_time = time.time()
                symbols = self.exchange_config["SYMBOLS"]
                self.get_data_from_exchange(symbol_lst=symbols)
                if len(self.failed_lst) != 0 and REPULL_DATA is True:
                    self.re_pull_data_from_exchange()
                end_time = time.time()
                logger_info.info(
                    "finish %s kline data job in %s second,%s success, %s failed" % (
                        self.name, end_time - start_time, len(self.success_lst), len(self.failed_lst)))
            except Exception:
                exstr = traceback.format_exc()
                logger_error.error(exstr)

    @staticmethod
    def get_db_cursor():
        return DbModule()

    @abstractmethod
    def get_data_from_exchange(self, symbol_lst):
        return

    def get_exchange_config(self):
        exchange_config = EXCHANGE_LIST[self.name]
        return exchange_config

    @abstractmethod
    def down_loader(self, symbol):
        return {}

    def re_pull_data_from_exchange(self):
        logger_error.info("start repull %s work..............." % self.name)
        success_list = []
        for failed_itemt in self.failed_lst:
            # in case of the item failed because db reason
            if failed_itemt.find("{") != -1:
                for times in range(self.max_re_pull_times):
                    time.sleep(self.request_time_delt)
                    logger_error.info("repull %s %s time..............." % (failed_itemt, times))
                    result = self.down_loader(json.loads(failed_itemt))
                    if result["result"] is True:
                        logger_error.info("repull %s job success in %s times" % (failed_itemt, times))
                        result = self.write_data_to_db(result["data"])
                        if result:
                            success_list.append(failed_itemt)
                            logger_info.info("repull %s item success" % failed_itemt)
                        break
        for succ in success_list:
            self.failed_lst.remove(succ)

    def data_clean(self, data, last_update_time):
        """
        对每次拉取的数据进行清洗，清洗出上一次时间与本次时间相差得部分
        data["time"]部分必须是int格式得秒级别得时间戳
        """
        start_time = last_update_time
        end_time = self.current_hour_timestamp
        data["time"] = pd.to_datetime(data["time"], unit="s")
        if start_time is None or start_time is '':
            pd_data = data
        else:
            pd_data = data[data["time"] > start_time[0]]
        # pd_data = data[data["time"] > start_time[0]] if start_time is not None else data
        pd_data = pd_data[pd_data["time"] < end_time]
        pd_data = pd_data.sort_values(by=['time'], ascending=True)
        pd_data.reset_index(drop=True, inplace=True)
        # if len(pd_data) == 1:
        #     pass
        # elif len(pd_data) != 0:
        #     pd_data = pd_data.iloc[:-1, :]
        if len(pd_data) >= 1:
            pd_data = pd_data.iloc[:-1, :]
        return pd_data

    def write_data_to_db(self, data):
        flag = True
        if len(data) == 0:
            logger_error.debug("no %s data left after data clean... " % self.data_type)
            self.success_lst.append(self.data_type)
            return flag
        try:
            if WRITE_TO_DB:
                data.to_sql(self.name, self.cursor.engine, index=False, if_exists='append')
            else:
                logger_info.info(
                    "dowload %s row %s data sucess,but WRITE_TO_DB set FALSE" % (len(data), self.data_type))
        except Exception as e:
            flag = False
            logger_error.error("write %s row  %s data to database failed" % (len(data), self.data_type))
            self.failed_lst.add(self.data_type)
            exstr = traceback.format_exc()
            logger_error.error(exstr)
        else:
            self.success_lst.append(self.data_type)
            logger_info.info("write %s row %s data to database sucess" % (len(data), self.data_type))
        return flag

    @staticmethod
    def get_contract_delivery_date(contract_type):
        delivery = DeliveryDate()
        date = None
        if contract_type == QUARTER:
            date = delivery.this_quarter()
        elif contract_type == NEXT_QUARTER:
            date = delivery.next_quarter()
        elif contract_type == THIS_WEEK:
            date = delivery.this_week()
        elif contract_type == NEXT_WEEK:
            date = delivery.next_week()
        return date

    def load_last_upadte_time(self, exchange_name, data_type):
        sql = """SELECT "time" FROM "%s" WHERE info='%s' ORDER BY "time" DESC limit 10 """ % (exchange_name, data_type)
        res = self.cursor.execute(sql)
        try:
            if res["result"] is True:
                last_up_time = res["data"].fetchone()
                return last_up_time
        except Exception as e:
            exstr = traceback.format_exc()
            logger_error.error(exstr)
