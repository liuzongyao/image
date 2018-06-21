# -*- coding:utf-8 -*-
import pytest
from common.result import result
from common.service import service
from common.build import build
import logging

logger = logging.getLogger()


def setup_function():
    result.test_flag = True


def teardown_function():
    result.results = {}


def setup_module():
    if 'image_name' in service.env.keys() and 'image_tag' in service.env.keys():
        logger.debug("镜像信息，配置文件已提供，不需要手工构建镜像")
    else:
        logger.debug("镜像信息，配置文件没有提供，需要手工构建镜像")
        build.update_build_parameter('build/svn.json')
        build.create('build/svn.json', name='demo1')
        build.start(build.config_id)
        image, code = build.get_image()
        assert code
        service.update_all_template(image)


def test_build2():
    # 校验服务创建
    response, code = service.create('basic_service_deployment.json', 'module_load_balance.json', service_name="demo28")
    assert code == 201, response
    # 校验服务创建事件
    response, code = service.get_event('create', 'service')
    result.assert_check_point(code, {"获取服务事件": response})
    # 校验服务运行中
    response, code = service.get_expected_value('current_status', 'Running')
    assert code, response
    # 校验服务可以访问
    response, code = service.is_available(service.service_name)
    result.assert_check_point(code == 200, {"校验服务访问": response})
    # 校验服务容器exec
    response, code = service.get_expect_string('export', "export")
    result.assert_check_point(code, {"登陆容器": response})
    # 校验服务容器登陆事件
    response, code = service.get_event('login', 'service')
    assert code, response
