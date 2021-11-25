# -*- coding: utf-8 -*-
# @Time       : 2021/11/24 23:05
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/24
import datetime as dt
import time as t
import pandas as pd
import requests
from config import *
from utils.db_module import DbModule


class DownOldData:
    def __init__(self, start_time) -> None:
        self.start_time = start_time
        self.next_start_time = start_time
        self.client = DbModule()
        self.headers = {}
        self.request_time_delt = 1  # s
        self.time_out = 5
        self.dir_path = './static/output_csv'
        self.early_data = ['btc|usdt|perp', 'eth|usdt|perp']

    def to_db(self, db_name, ex_data, info):
        ex_data = pd.DataFrame(ex_data, columns=["id", "open", "high", "low", "close", "volume", "closeTime",
                                                     "quoteAssetVolume", "trades", "takerBuyBaseVolume",
                                                     "takerBuyQuoteVolume", "Ignore"])
        ex_data = ex_data[["id", "high", "low", "open", "close", "volume"]]
        ex_data.rename(columns={"id": "time"}, inplace=True)
        ex_data['time'] = ex_data["time"] / 1000 + 8 * 60 * 60
        ex_data["time"] = pd.to_datetime(ex_data["time"], unit="s")
        ex_data = ex_data.sort_values(by=['time'], ascending=True)
        ex_data.reset_index(drop=True, inplace=True)
        ex_data = ex_data.iloc[:-1, :]
        ex_data["info"] = info
        ex_data.drop_duplicates(subset=['time', 'info'], keep="last", inplace=True)
        ex_data.to_sql(db_name, self.client.engine, index=False, if_exists='append')

    def down_binance_toDB(self, interval='1m'):
        exchange = 'binance'
        spot_url = "https://api.binance.com/api/v3/klines?interval=1m&startTime={}&endTime={}&symbol={}"
        future_url = "https://fapi.binance.com/fapi/v1/klines?interval=1m&startTime={}&endTime={}&symbol={}"
        
        for item in EXCHANGE_LIST[exchange]['SYMBOLS']:
            flag = True
            info = "%s|%s|%s" % (item["assert"], item["to"], item["type"])
            symbol = item['symbol']
            type = item['type']
            self.next_start_time = self.start_time
            if type == 'perp':
                url = future_url
                self.next_start_time = max(self.next_start_time.replace(year=2020), self.next_start_time)
            else:
                url = spot_url

            sql = f"SELECT time FROM binance WHERE info=\'{info}\' ORDER BY time LIMIT 5;"
            time = pd.read_sql(sql, self.client.conn)
            time = time.sort_values(['time']).reset_index(drop=True).iloc[0][0] #TimeStamp
            time = time.to_pydatetime()
            if time <= self.next_start_time:
                flag = False
            else:
                flag = True

            while flag:
                start_time = self.next_start_time
                end_time = start_time + dt.timedelta(hours=8)

                if end_time >= time:
                    end_time = time
                    flag = False

                start_timestamp = int(start_time.timestamp() * 1000)
                end_timestamp = int(end_time.timestamp() * 1000)
                tmp_url = url.format(start_timestamp, end_timestamp, symbol)
                try:
                    res = requests.get(tmp_url, headers=self.headers, timeout=self.time_out)
                    ex_data = res.json()
                except Exception as e:
                    print('Failed to get {} {} data!'.format(start_time.strftime("%Y-%m-%d %H:%M:%S"), symbol))
                else:
                    print('Get {} {} data successfully {}'.format(start_time.strftime("%Y-%m-%d %H:%M:%S"), symbol, len(ex_data)))
                    self.next_start_time = start_time + dt.timedelta(hours=8)
                    if len(ex_data) > 0:
                        self.to_db(exchange, ex_data, info)
                t.sleep(self.request_time_delt)
        self.close_connect()

    def from_DB_to_csv(self, exchange):
        for item in EXCHANGE_LIST[exchange]['SYMBOLS']:
            info = "%s|%s|%s" % (item["assert"], item["to"], item["type"])
            file_name = "%s_%s_%s.csv" % (item["assert"], item["to"], item["type"])
            symbol = item['symbol']
            type = item['type']
            if info in self.early_data:
                stop_data = '2021-11-12 00:00:00'
            else:
                stop_data = '2021-11-15 00:00:00'
            stop_data = dt.datetime.strptime(stop_data, "%Y-%m-%d %H:%M:%S")
            sql = "SELECT * FROM {} WHERE info=\'{}\' AND time BETWEEN \'{}\' AND \'{}\' ORDER BY time;"

            if type == 'perp':
                start_data = dt.datetime(year=2020, month=1, day=1, hour=0, minute=0)
            else:
                start_data = dt.datetime(year=2018, month=1, day=1, hour=0, minute=0)

            if start_data < stop_data:
                flag = True
            else:
                flag = False
            
            while flag:
                start_str = start_data.strftime("%Y-%m-%d %H:%M:%S")
                end_str = (start_data + dt.timedelta(hours=23, minutes=59)).strftime("%Y-%m-%d %H:%M:%S")
                tmp_sql = sql.format(exchange, info, start_str, end_str)
                res = pd.read_sql(tmp_sql, self.client.conn)
                if res.shape[0] > 0:
                    res.drop(['id'], axis=1, inplace=True)
                    outfile_path = os.path.join(self.dir_path, start_data.strftime("%Y-%m-%d"), exchange)
                    if not os.path.exists(outfile_path):
                        os.makedirs(outfile_path)
                    res.to_csv(os.path.join(outfile_path, file_name), index=False)
                    print(f"Day {start_str[:11]} {info} write to csv {res.shape[0]}")
                else:
                    print(f"Day {start_str[:11]} {info} write to csv 0")
                start_data = start_data + dt.timedelta(days=1)
                if start_data >= stop_data:
                    flag = False
        self.close_connect()

    def close_connect(self):
        self.client.close()


if __name__ == '__main__':
    down_old_data = DownOldData(start_time = dt.datetime(year=2018, month=1, day=1, hour=0, minute=0))
    for exchange in EXCHANGE_LIST:
        if exchange == 'binance':
            down_old_data.down_binance_toDB()
            # down_old_data.from_DB_to_csv('binance')
       
