# -*- coding: utf-8 -*-
# @Time       : 2021/11/15 22:35
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/15
import numpy as np
from numpy import abs
from numpy import log
from numpy import sign

import pandas as pd
import time


class Alphas_101:
    def __init__(self, data, save=False):
        self.high = data['high']
        self.low = data['low']
        self.close = data['close']
        self.open = data['open']
        self.volume = data['volume']
        self.returns = self.close.pct_change()
        self.vwap = (data['open'] + data['high'] + data['low'] + data['close']) / 4

    @staticmethod
    def __ts_argmax(df: pd.DataFrame, window=10):
        """
        返回滑动窗口中数据最大值的位置
        :param df: pandas.DataFrame
        :param window: 窗口大小
        :return: 滑动窗口中最大值位置
        """
        return df.rolling(window).apply(np.argmax) + 1

    @staticmethod
    def __ts_argmin(df: pd.DataFrame, window = 10):
        """
        返回滑动窗口中数据最小值的位置
        :param df: pandas.DataFrame
        :param window: 窗口大小
        :return: 滑动窗口中最小值位置
        """
        return df.rolling(window).apply(np.argmin) + 1

    def alpha001(self):
        inner = self.close.copy(deep=True)
        inner[self.returns < 0] = self.returns.rolling(window=20).std()
        inner = (inner ** 2) * np.sign(inner)
        inner = self.__ts_argmax(inner, window=5)
        return inner

if __name__ == '__main__':
    data = pd.read_csv('D:\WorkCode\BT\CoreCode\data_product\Alphas_101\\btc_usd_perp.csv')
    alphas = Alphas_101(data)
    res = alphas.alpha001()
    print("Well Done")