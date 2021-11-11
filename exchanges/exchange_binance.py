# -*- coding: utf-8 -*-
# @Time       : 2021/11/8 21:10
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/8

import time
import requests
from exchanges import ExchangeBase
import pandas as pd
from config import *
from config.global_config import *


class Binance(ExchangeBase):
    def __init__(self, exchange_name='binance'):
        super().__init__(exchange_name)

    def get_data_from_exchange(self, symbol_lst):
        """
        MAX_LIMIT: FUTURE:1500, SPOT:1000
        Spot接口文档：https://binance-docs.github.io/apidocs/spot/cn/#k
        Feature接口文档：https://binance-docs.github.io/apidocs/futures/cn/#k-market_data
        :return:
        """
        symbols = symbol_lst
        for symbol in symbols:
            data = self.down_loader(symbol)
            if data["result"] is True:
                result = self.write_data_to_db(data["data"])
            time.sleep(self.request_time_delt)

    def down_loader(self, symbol):
        if symbol["type"] == SPOT:
            url = self.exchange_config["SPOT_URL"]
            url = url.format(symbol["symbol"])
        else:
            url = self.exchange_config["FUTURE_URL"]
            url = url.format(symbol["symbol"])
        logger_info.debug(url)
        self.data_type = "%s|%s|%s" % (symbol["assert"], symbol["to"], symbol["type"])

        try:
            res = requests.get(url, headers=self.headers, timeout=self.time_out)
            ex_data = res.json()
            self.last_update_time = self.load_last_upadte_time(self.name, self.data_type)
        except Exception as e:
            logger_error.error(e)
            self.failed_lst.add(json.dumps(symbol))
            logger_error.error("add [%s] to failed_list" % json.dumps(symbol))
            return {"result": False}
        else:
            ex_data = pd.DataFrame(ex_data, columns=["id", "open", "high", "low", "close", "volume", "closeTime",
                                                     "quoteAssetVolume", "trades", "takerBuyBaseVolume",
                                                     "takerBuyQuoteVolume", "Ignore"])
            if len(ex_data) == 0:
                logger_error.error("%s data length is 0,please check what happend" % self.data_type)
                return {"result": False}
            ex_data = ex_data[["id", "high", "low", "open", "close", "volume"]]
            ex_data.rename(columns={"id": "time", "volume": "volume"}, inplace=True)
            ex_data['time'] = ex_data["time"] / 1000 + 8 * 60 * 60
            ex_data = self.data_clean(ex_data, self.last_update_time)
            ex_data["info"] = self.data_type
            ex_data.drop_duplicates(subset=['time', 'info'], keep="last", inplace=True)
            return {"result": True, "data": ex_data}
