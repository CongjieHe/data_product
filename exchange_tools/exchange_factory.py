# -*- coding: utf-8 -*-
# @Time       : 2021/11/9 2:32
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/9
import sys
import os
sys.path.append(os.getcwd())

from config import *
from config.global_config import *
from exchanges.exchange_binance import Binance


class ExchangeFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(exchange_name):
        if exchange_name is BINANCE:
            ex_instance = Binance(BINANCE)
            return ex_instance
        else:
            logger_error.error("The exchange name is illegal!")
