# -*- coding:utf-8 -*-
from common.rest import rest
from common.result import result
from common.exec_helper import exec_helper
from common.common import common
import pytest
import json
import sys


# def teardown_function(function):
#     print ("teardown_function--->")
#     for i in range(len(rest.resource_url)):
#         rest.delete(rest.resource_url[i])


@pytest.mark.demo
def test_6():
    case_name = sys._getframe().f_code.co_name
    rest.update_load_balance()
    #校验服务创建
    response, code = rest.post(rest.url_path('/services/{namespace}', common.env['namespace']), 'basic_service_deployment.json', 'module_load_balance.json', service_name="demo7")
    if result.is_pass(code == 201):
        result.update_check_point(case_name, True, '测试通过')
    else:
        try:
            message = json.loads(response)
            result.update_check_point(case_name, False, message)
        except ValueError:
            result.update_check_point(case_name, False, response)

    service_uuid, code = rest.get_value(response, 'unique_name')
    service_name, code = rest.get_value(response, 'service_name')

    #校验创建服务事件
    response, code = rest.get_event(rest.url_path('/events/{namespace}/{resource_type}/{resource_uuid}', (common.env['namespace'], 'service', service_uuid), params=rest.get_event_params()), 'create', 'service')
    if result.is_pass(code):
        result.update_check_point(case_name, True, '测试通过')
    else:
        try:
            message = json.loads(response)
            result.update_check_point(case_name, False, message)
        except ValueError:
            result.update_check_point(case_name, False, response)

    # 校验服务处于运行中
    response, code = rest.get_expected_value(rest.url_path('/services/{namespace}/{service_uuid}', (common.env['namespace'], service_uuid)), 'current_status', 'Running')

    if result.is_pass(code):
        result.update_check_point(case_name, True, '测试通过')
    else:
        try:
            message = json.loads(response)
            result.update_check_point(case_name, False, message)
        except ValueError:
            result.update_check_point(case_name, False, response)

    #校验服务可以访问
    response, code = rest.get(rest.get_service_url(service_name))
    position = response.find("Welcome to nginx")
    print position
    if result.is_pass(position != -1):
        result.update_check_point(case_name, True, '测试通过')
    else:
        result.update_check_point(case_name, False, response)

    #校验登陆容器
    response, code = exec_helper.get_expect_string(service_uuid, 'export', "export")

    if result.is_pass(code):
        result.update_check_point(case_name, True, '测试通过')
    else:
        try:
            message = json.loads(response)
            result.update_check_point(case_name, False, message)
        except ValueError:
            result.update_check_point(case_name, False, response)
    #校验登陆容器事件
    response, code = rest.get_event(rest.url_path('/events/{namespace}/{resource_type}/{resource_uuid}', (common.env['namespace'], 'service', service_uuid), params=rest.get_event_params()), 'login', 'service')

    if result.is_pass(code):
        result.update_check_point(case_name, True, '测试通过')
    else:
        try:
            message = json.loads(response)
            result.update_check_point(case_name, False, message)
        except ValueError:
            result.update_check_point(case_name, False, response)

    #校验服务log
    response, code = rest.get_log(rest.url_path('/services/{namespace}/{service_uuid}/logs', (common.env['namespace'], service_uuid), params=rest.get_log_parames()))
    if result.is_pass(code):
        result.update_check_point(case_name, True, '测试通过')
    else:
        result.update_check_point(case_name, False, response)

    #校验metric

    params = rest.get_metric_params('avg', 'service.mem.utilization', service_uuid)
    response, code = rest.get_metric(rest.url_path('/monitor/{namespace}/metrics/query', common.env['namespace'], params=params, version='v2'), 'dps')
    if result.is_pass(code):
        result.update_check_point(case_name, True, '测试通过')
    else:
        result.update_check_point(case_name, False, response)
























