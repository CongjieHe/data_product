# -*- coding: utf-8 -*-
# @Time       : 2021/11/24 23:05
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/24

from config import *

def down_binance(start_day, end_day, interval='1m'):
    spot_url = 'https://data.binance.vision/data/spot/monthly/klines/{}/{}/{}.zip'
    
    for item in EXCHANGE_LIST[exchange]['SYMBOLS']:
        info = "%s|%s|%s" % (item["assert"], item["to"], item["type"])
        symbol = item['symbol']
        type = item['type']

if __name__ == '__main__':
    for exchange in EXCHANGE_LIST:
        if exchange == 'binance':
            down_binance()
       
