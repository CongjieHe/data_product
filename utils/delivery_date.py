# -*- coding: utf-8 -*-
# @Time       : 2021/11/6 1:20
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/6

import calendar
import datetime
import socket
import requests
import time


class DeliveryDate:

    def __init__(self):
        self.date = datetime.datetime.now()
        self.year = self.date.year
        self.month = self.date.month
        self.day = self.date.day
        self.weekday = self.date.weekday() + 1
        self.hour = self.date.hour
        self.date_delt = 0
        self.march_fri = self.get_last_friday_by_year_and_month(self.year, 3)
        self.june_fri = self.get_last_friday_by_year_and_month(self.year, 6)
        self.sep_fri = self.get_last_friday_by_year_and_month(self.year, 9)
        self.dec_fri = self.get_last_friday_by_year_and_month(self.year, 12)
        self.delivery_date_this_year = [
            datetime.datetime.strptime("%s-%s-%s 16:00:00" % (self.march_fri[0], self.march_fri[1], self.march_fri[2]),
                                       "%Y-%m-%d %H:%M:%S"),
            datetime.datetime.strptime("%s-%s-%s 16:00:00" % (self.june_fri[0], self.june_fri[1], self.june_fri[2]),
                                       "%Y-%m-%d %H:%M:%S"),
            datetime.datetime.strptime("%s-%s-%s 16:00:00" % (self.sep_fri[0], self.sep_fri[1], self.sep_fri[2]),
                                       "%Y-%m-%d %H:%M:%S"),
            datetime.datetime.strptime("%s-%s-%s 16:00:00" % (self.dec_fri[0], self.dec_fri[1], self.dec_fri[2]),
                                       "%Y-%m-%d %H:%M:%S"), ]

    def this_week(self):
        if self.weekday < 5:
            self.date_delt = 5 - self.weekday
        elif self.weekday == 5:
            if self.hour < 16:
                self.date_delt = 0
            elif self.hour >= 16:
                self.date_delt = 7
        else:
            self.date_delt = 12 - self.weekday
        date_delt_num = datetime.timedelta(days=self.date_delt)
        delivery_date = self.date + date_delt_num
        del_year = delivery_date.year
        del_month = delivery_date.month
        del_date = delivery_date.day
        return [del_year, del_month, del_date]

    def next_week(self):
        if self.weekday < 5:
            self.date_delt = 12 - self.weekday
        elif self.weekday == 5:
            if self.hour < 16:
                self.date_delt = 7
            elif self.hour >= 16:
                self.date_delt = 14
        else:
            self.date_delt = 19 - self.weekday
        date_delt_num = datetime.timedelta(days=self.date_delt)
        delivery_date = self.date + date_delt_num
        del_year = delivery_date.year
        del_month = delivery_date.month
        del_date = delivery_date.day
        return [del_year, del_month, del_date]

    def this_quarter(self):
        if self.date < self.delivery_date_this_year[0]:
            return self.march_fri
        elif self.delivery_date_this_year[0] < self.date < self.delivery_date_this_year[1] or self.date == \
                self.delivery_date_this_year[0]:
            return self.june_fri
        elif self.delivery_date_this_year[1] < self.date < self.delivery_date_this_year[2] or self.date == \
                self.delivery_date_this_year[1]:
            return self.sep_fri
        elif self.delivery_date_this_year[2] < self.date < self.delivery_date_this_year[3] or self.date == \
                self.delivery_date_this_year[2]:
            return self.dec_fri
        elif self.date > self.delivery_date_this_year[3] or self.date == \
                self.delivery_date_this_year[3]:
            return self.get_last_friday_by_year_and_month(self.year + 1, 3)

    def next_quarter(self):
        if self.date < self.delivery_date_this_year[0]:  # 1~3 return jun
            return self.june_fri
        elif self.delivery_date_this_year[0] < self.date < self.delivery_date_this_year[1] or self.date == \
                self.delivery_date_this_year[0]:  # 3~6 return sep
            return self.sep_fri
        elif self.delivery_date_this_year[1] < self.date < self.delivery_date_this_year[2] or self.date == \
                self.delivery_date_this_year[1]:  # 6~9 return dec
            return self.dec_fri
        elif self.delivery_date_this_year[2] < self.date < self.delivery_date_this_year[3] or self.date == \
                self.delivery_date_this_year[2]:  # 9~12 return next_march
            return self.get_last_friday_by_year_and_month(self.year + 1, 3)
        elif self.date > self.delivery_date_this_year[3] or self.date == \
                self.delivery_date_this_year[3]:  # > 12 return next_june
            return self.get_last_friday_by_year_and_month(self.year + 1, 6)

    @staticmethod
    def get_last_friday_by_year_and_month(year, month):
        c = calendar.Calendar(firstweekday=calendar.MONDAY)
        monthcal = c.monthdatescalendar(year, month)
        last_fridays = [day for week in monthcal for day in week if
                        day.weekday() == calendar.FRIDAY and day.month == month]
        last_friday = last_fridays[len(last_fridays) - 1]
        return [last_friday.year, last_friday.month, last_friday.day]

    @staticmethod
    def get_current_hour_start_timestamp():
        cur_time = time.time()
        # get time list
        cur_time = list(time.localtime(cur_time))
        # cur_time = [2018, 8, 22, 8, 55, 20, 0, 295, 0]
        cur_time = "%s-%s-%s %s:%s:%s" % (cur_time[0], cur_time[1], cur_time[2], cur_time[3], cur_time[4], cur_time[5])
        # trans time to time array
        cur_time = time.strptime(cur_time, '%Y-%m-%d %H:%M:%S')
        # trans time array to timestamp
        # cur_time = time.mktime(cur_time)
        return time.strftime('%Y-%m-%d %H:%M:%S', cur_time)
