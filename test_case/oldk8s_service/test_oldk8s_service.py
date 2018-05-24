# -*- coding:utf-8 -*-
from common.rest import rest
from common.result import result
from common.exec_helper import exec_helper
import pytest
import time
import json
import sys
import inspect
from dateutil import tz
from datetime import datetime
import iso8601


# def teardown_function(function):
#     print ("teardown_function--->")
#     for i in range(len(rest.resource_url)):
#         rest.delete(rest.resource_url[i])


def test_1():
    response1 = rest.post(rest.url_path('services', params={'project_name': 'automation'}), 'basic_service_deployment.json',  space_name='test-automation')

    service_name = rest.get_value(response1, 'unique_name')

    response2 = rest.get(rest.url_path('services', service_name=service_name))

    current_status = rest.get_value(response2, 'current_status')

    print current_status

    container_port = rest.circle_get_value(rest.url_path('services', service_name=service_name), 'container_port', entry='raw_container_ports')

    print container_port




def test_2():
    #get service with params
    response = rest.get(rest.url_path('services', params={'space_name': 'staging'}))
    count = rest.get_value(response, 'count')
    print count
    unique_name = rest.get_value(response, 'node_port', entry='results')
    print unique_name

    assert 'running' in 'running'



def test_3():
    response = rest.delete('http://jakiro-api-staging.nolimited.haproxy-54-223-242-27-alaudacn.myalauda.cn/v1/env-files/testorg001/aa347e90-1e70-493c-88bb-f8a665e93c9a')
    print response


@pytest.mark.demo
def test_4():
    # response = rest.post(rest.url_path('env-files'), 'envfiles.json', primary='name')
    # if isinstance(response, dict):
    #     result.update_check_point('test_4', 'create volume success', False, True, 'success')
    # else:
    #     content = rest.get_content(response, 'p')
    #     result.update_check_point('test_4', 'create env file succeed', True, False, content)
    #
    # envfile_name = rest.get_value(response, 'name')
    # envfile_uuid = rest.get_value(response, 'uuid')
    # rest.set_value('module_envfiles.json', 'name', envfile_name)

    response = rest.post(rest.url_path('storage', volumes='volumes'), 'volume.json', primary='name')
    if isinstance(response, dict):
        result.update_check_point('test_4', 'create volume success', False, True, 'success')
    else:
        content = rest.get_content(response, 'p')
        result.update_check_point('test_4', 'create volume success', True, False, content)
    volume_name = rest.get_value(response, 'name')
    volume_id = rest.get_value(response, 'id')
    rest.set_value('module_volumes.json', 'volume_name', volume_name, 2)
    rest.set_value('module_volumes.json', 'volume_id', volume_id, 2)


    # append_json = ['module_envfiles.json', 'module_volumes.json']
    # response = rest.post(rest.url_path('services'), 'basic_service_deployment.json', append_json)
    # if isinstance(response, dict):
    #     result.update_check_point('test_4', 'create service success', False, True, 'success')
    # else:
    #     content = rest.get_content(response, 'p')
    #     result.update_check_point('test_4', 'create service success', True, False, content)
    #
    # service_name = rest.get_value(response, 'unique_name')
    # current_status = rest.get_expected_value(rest.url_path('services', service_name=service_name), 'current_status', 'Running')
    # print "-------------------------------------"
    # print current_status
    #
    # if current_status:
    #     result.update_check_point('test_4', 'check service is running', False, True, 'success')
    # else:
    #     result.update_check_point('test_4', 'check service is running', True, False, 'failure')
    #
    # is_expected = exec_helper.get_expect_string(service_name, 'export', "A='1'")  # check环境变量
    # if is_expected:
    #     result.update_check_point('test_4', 'check env success in containers', False, True, 'success')
    # else:
    #     result.update_check_point('test_4', 'check env success in containers', False, False, 'failure')
    #
    # is_exist = exec_helper.exist_file(service_name, '/demo')
    # if is_exist:
    #     result.update_check_point('test_4', 'check host path volume exist', False, True, 'success')
    # else:
    #     result.update_check_point('test_4', 'check host path volume exist', False, False, 'failure')
    #
    # created_at = rest.covert_to_unix(rest.get_value(response, 'created_at'))
    #
    # print type(created_at)
    #
    # print created_at.__int__() + 1
    #
    # rest.resource_url.append(rest.url_path('services', service_name=service_name))
    # rest.resource_url.append(rest.url_path('env-files', envfile_uuid=envfile_uuid))
    # rest.resource_url.append(rest.url_path('storage', volumes='volumes', volume_id=volume_id))






