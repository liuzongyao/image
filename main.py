#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import pytest
from common.result import result

if __name__ == '__main__':
    run_command = ['--capture=no', '-m demo', './test_case/oldk8s_service/test_oldk8s_service.py', "--html=./report/pytest.html"]
    pytest.main(run_command)
    body = result.update_results()
    result.send_email('hello world', body)