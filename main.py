#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tarfile
import os
import pytest
from common.utils import send_email, read_result
from common import settings
from common.log import logger
from common.get_common_data import CommonData, delete_project
from common.parsercase import data_value


def setup():
    CommonData()


def teardown():
    delete_project(data_value().get('PROJECT_NAME'))


def main():
    # 获取集群的全部固定资源
    setup()

    # 执行case
    run_command = ['-s', settings.TESTCASES, "--html=./report/pytest.html"]
    if settings.CASE_TYPE:
        run_command.append("-m {}".format(settings.CASE_TYPE))
    logger.info('pytest command: {}'.format(run_command))
    pytest.main(run_command)

    try:
        resultflag, html = read_result()
        with tarfile.open("./report.tar", "w:gz") as tar:
            tar.add("./report", arcname=os.path.basename("./report"))
        send_email(
            "[{}] ({}) ({}) API E2E Test".format(resultflag, settings.ENV, settings.REGION_NAME),
            html, settings.RECIPIENTS, "./report.tar")
        logger.info("********* begin to print result *********")
        logger.info(html)
        logger.info("********* begin to print result *********")

        teardown()
    except KeyboardInterrupt:
        teardown()


if __name__ == '__main__':
    main()

