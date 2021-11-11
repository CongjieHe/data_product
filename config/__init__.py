# -*- coding: utf-8 -*-
# @Time       : 2021/11/6 0:25
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/6

import getopt
import logging.config
import os
import sys
import json

# logger config
log_file_path = os.path.join(os.getcwd(), 'config', 'logger.conf')
# print(log_file_path)
logging.config.fileConfig(log_file_path)
logger_info = logging.getLogger("infoLogger")
logger_info.setLevel(logging.DEGUG)
logger_error = logging.getLogger("errorLogger")
logger_error.setLevel(logging.ERROR)

# exchange config
symbol_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'symbol.json')
with open(symbol_path) as f:
    EXCHANGE_LIST = json.load(f)

argv = sys.argv[1:]

# 默认参数
RUN_ENV = "dev"
CURRENT_EXCHANGE = 'binance'
WRITE_TO_DB = True
REPULL_DATA = True

try:
    opts, argv = getopt.getopt(argv, "hd:e:t:w:r:", ["database=", "exchange=", "type=", "write=", "repull="])
except getopt.GetoptError:
    print("main_app.py -d <database> -e <exchange> -t <type> -w <write> -r <repull>")
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        print("main_app.py -d <database> -e <exchange> -t <type> -w <write> -r <repull>")
        exit()
    elif opt in ("-d", "--database"):  # specify which env to run
        RUN_ENV = arg
    elif opt in ("-e", "--exchagne"):  # specify one exchange to run
        CURRENT_EXCHANGE = arg
    elif opt in ("-w", "--write"):  # param -w , control data write into db
        if arg.lower() == "y":
            WRITE_TO_DB = True
        elif arg.lower() == "n":
            WRITE_TO_DB = False
        else:
            print("-w must be 'y' or 'n' ")
            exit()
    elif opt in ("-r", "--repull"):
        if arg.lower() == "y":
            REPULL_DATA = True
        elif arg.lower() == "n":
            REPULL_DATA = False
        else:
            print("-r must be 'y' or 'n' ")
            exit()
