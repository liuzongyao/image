#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
import time
import os
import yaml


class Common:

    start_time = time.time()
    end_time = time.time()
    env = ''
    master = ''

    def __init__(self):
        file_path = os.path.dirname(__file__)
        env_dist = os.environ
        if 'env_key' in env_dist.keys():
            env_file = os.getenv("env_key")
        else:
            env_file = file_path + '/../config/env_new_int.yaml'
        f = open(env_file)
        self.env = yaml.load(f)


    @classmethod
    def get_start_time(cls):

        return time.time()

    @classmethod
    def get_end_time(cls):
        return time.time()


common = Common()
