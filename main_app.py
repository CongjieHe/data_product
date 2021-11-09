# -*- coding: utf-8 -*-
# @Time       : 2021/11/10 1:01
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/10

from config import *
from kline_service import KlineService

if __name__ == '__main__':
    logger_info.info("System start!")
    kl_service = KlineService()
    kl_service.start()
