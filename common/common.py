#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import time


class Common:

    start_time = 0
    end_time = 0

    def __init__(self):
        pass

    @classmethod
    def get_start_time(cls):

        return time.time()

    @classmethod
    def get_end_time(cls):
        return time.time()

