#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import pytest

if __name__ == '__main__':

    run_command = ["--capture=fd", './testcase/buildconfig/test_build_config.py', "--result-log=./report/log.txt","--html=./report/pytest.html"]

    pytest.main(run_command)
