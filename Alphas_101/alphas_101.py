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
    def __init__(self, data, factor_id, save=False):
        self.high = data['high']
        self.low = data['low']
        self.close = data['close']
        self.open = data['open']
        self.volume = data['volume']
        self.returns = self.close.pct_change()
        self.vwap = (data['open'] + data['high'] + data['low'] + data['close']) / 4

    def alpha001(self):
        inner = self.close.copy(deep=True)
