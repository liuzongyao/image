#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
# import requests
# file_path = os.path.dirname(__file__)
# env_value = file_path + '/data_template/compose.yaml'
# data = {"region": "awsoldk8s", "space_name": "staging", "app_name": "sssss5s"}
# url = "http://jakiro-api-staging.nolimited.haproxy-54-223-242-27-alaudacn.myalauda.cn/v1/applications/testorg001"
# header = {'Authorization': 'Token 80ba348a7232292885aa1fb9136b22c080dcb9b2'}
# files = {'file': open(env_value, 'rb')}
# r = requests.post(url, data=data, files=files, headers=header)
# print r

import sys
def a():
    print sys._getframe().f_code.co_name

a()