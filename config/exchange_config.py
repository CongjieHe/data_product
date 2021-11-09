# -*- coding: utf-8 -*-
# @Time       : 2021/11/9 12:58
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/9

# 通过获取orderbook或者trades数据来生成kline. 每3分钟执行一次数据收集
ORDER_BOOK_DATASOURCE = []
LATEST_INFO = []

exchanges = {
    'binance': True
}
