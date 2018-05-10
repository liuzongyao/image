#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import pytest

if __name__ == '__main__':

    #run_command = ["--capture=no", "-m demo",'./testcase/oldk8s_service/test_oldk8s_service.py', "--result-log=./report/log.txt", "--html=./report/pytest.html"]

    run_command = ["--capture=no",'./testcase/oldk8s_service/test_oldk8s_service.py', "--html=./report/pytest.html"]

    pytest.main(run_command)

    # var = 1
    # while var == 1:  # 该条件永远为true，循环将无限执行下
    #      print "hello world"
