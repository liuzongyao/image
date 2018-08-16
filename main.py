#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import tarfile

import pytest

from common import settings
from common.log import logger
from common.setup_teardown import SetUp, TearDown
from common.utils import read_result, send_email


def main():
    # 获取集群的全部固定资源
    SetUp()

    # 执行case
    run_command = ['-s', settings.TESTCASES, "--html=./report/pytest.html"]
    if settings.CASE_TYPE:
        run_command.append("-m {}".format(settings.CASE_TYPE))
    logger.info('pytest command: {}'.format(run_command))
    pytest.main(run_command)

    resultflag, html = read_result()
    logger.info("********* begin to print result *********")
    logger.info(html)
    logger.info("********* print result over*********")
    with tarfile.open("./report.tar", "w:gz") as tar:
        tar.add("./report", arcname=os.path.basename("./report"))
    send_email(
        "[{}] ({}) ({}) API E2E Test".format(resultflag, settings.ENV, settings.REGION_NAME),
        html, settings.RECIPIENTS, "./report.tar")

    # 清理数据
    TearDown()


if __name__ == '__main__':
    main()
