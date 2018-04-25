#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import pytest

if __name__ == '__main__':

    run_command = ["--capture=fd", './testcase/buildconfig/test_build_config.py', "--result-log=./report/log.txt","--html=./report/pytest.html"]

    pytest.main(run_command)

    var = 1
    while var == 1:  # 该条件永远为true，循环将无限执行下
        print "hello world"
