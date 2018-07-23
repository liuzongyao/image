#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import pytest
from common.result import result

if __name__ == '__main__':
    run_command = ['-s', '-m demo', './test_case/newk8s_service/deployment_service.py', "--html=./report/pytest.html"]
    pytest.main(run_command)
    body = result.update_results()
    result.send_email('hello world', body)
