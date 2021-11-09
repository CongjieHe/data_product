# -*- coding: utf-8 -*-
# @Time       : 2021/11/9 20:11
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/9
"""
该脚本用于更新Kline接口的symbol列表
"""
import pandas as pd
from sqlalchemy import create_engine
import os
import sys
import json

remote_engine = create_engine('postgresql://coindata:1024@127.0.0.1:5432/exchange_data')

symbol_path = os.path.join(os.path.dirname(os.getcwd()), 'config', 'symbol.json')
with open(symbol_path) as f:
    EXCHANGE_LIST = json.load(f)


if __name__ == '__main__':
    symbol_list = []
    for exchange in EXCHANGE_LIST:
        exchange_datas = EXCHANGE_LIST[exchange]
        for exchange_data in exchange_datas["SYMBOLS"]:
            exchange_data["exchange"] = exchange
            symbol_list.append(exchange_data)
    symbol_list = pd.DataFrame(symbol_list)
    symbol_list["id"] = symbol_list.index
    symbol_list = symbol_list[["id", "exchange", "symbol", "assert", "to", "type"]]
    symbol_list.rename(columns={"symbol": "pair"}, inplace=True)
    symbol_list.to_sql("symbol", remote_engine, index=False, if_exists='replace')
    print(symbol_list)
