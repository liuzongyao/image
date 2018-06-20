# -*- coding:utf-8 -*-
import pytest
from common.result import result
from common.service import service
from common.build import build


def setup_function():
    result.test_flag = True


def teardown_function():
    result.results = {}


def setup_module():
    if 'image_name' in service.env.keys() and 'image_tag' in service.env.keys():
        print "镜像信息，配置文件已提供，不需要手工构建镜像"
    else:
        print "镜像信息，配置文件没有提供，需要手工构建镜像"
        build.update_build_parameter('build/svn.json')
        build.create('build/svn.json', name='demo1')
        build.start(build.config_id)
        image, code = build.get_image()
        print image
        assert code
        service.update_all_template(image)


def test_service():
    # 校验服务创建
    response, code = service.create('new_k8s/deploy.json', version='v2')
    assert code == 201, response
    # 校验服务创建事件
    response, code = service.get_event('create', 'application')
    result.assert_check_point(code, {"获取服务事件": response})
    # 校验服务运行中
    response, code = service.get_expected_value('status', 'Running', resource_type='apps')
    assert code, response
    #校验服务可以访问
    response, code = service.is_available(service.service_name)
    result.assert_check_point(code == 200, {"校验服务访问": response})