#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pytest
from common.utils import send_email, read_result
from common import settings
from common.log import Logging
import tarfile
import os

logger = Logging.get_logger()

if __name__ == '__main__':
    run_command = ['-s', settings.TESTCASES, "--html=./report/pytest.html"]
    if settings.CASE_TYPE:
        run_command.append("-m {}".format(settings.CASE_TYPE))
    print(run_command)
    pytest.main(run_command)
    resultflag, html = read_result()
    with tarfile.open("./report.tar", "w:gz") as tar:
        tar.add("./report", arcname=os.path.basename("./report"))
    send_email(
        "[{}] ({}) ({}) API E2E Test".format(resultflag, settings.ENV, settings.REGION_NAME),
        html, settings.RECIPIENTS, "./report.tar")
    logger.info("********* begin to print result *********")
    logger.info(html)
    logger.info("********* begin to print result *********")
