# -*- coding:utf-8 -*-
from common.rest import rest
from common.result import result
from common.exec_helper import exec_helper
import pytest


# def teardown_function(function):
#     print ("teardown_function--->")
#     for i in range(len(rest.resource_url)):
#         rest.delete(rest.resource_url[i])

def test_1():
    response1 = rest.post(rest.url_path('services', params={'project_name': 'automation'}), 'basic_service_deployment.json',  space_name='test-automation')

    service_id = rest.get_value(response1, 'unique_name')

    response2 = rest.get(rest.url_path(['services', service_id]))

    current_status = rest.get_value(response2, 'current_status')

    print current_status

    container_port = rest.circle_get_value(rest.url_path(['services', service_id]), 'container_port', entry='raw_container_ports')

    print container_port

    response = rest.get(rest.url_path(['events', 'service', service_id], params=rest.get_event_time()))
    print response




def test_2():
    #get service with params
    response = rest.get(rest.url_path('services', params={'space_name': 'staging'}))
    count = rest.get_value(response, 'count')
    print count
    unique_name = rest.get_value(response, 'node_port', entry='results')
    print unique_name

    assert 'running' in 'running'

@pytest.mark.demo
def test_3():
    response1 = rest.post(rest.url_path('services'), 'basic_service_deployment.json')

    service_id = rest.get_value(response1, 'unique_name')

    is_event = rest.get_event(rest.url_path(['events', 'service', service_id], params=rest.get_event_time()), 'create', 'service')

    print is_event

    current_status = rest.get_expected_value(rest.url_path(['services', service_id]), 'current_status', 'Running')

    print current_status

    is_expected = exec_helper.get_expect_string(service_id, 'export', "A='1'")  # check环境变量

    print is_expected

    is_event = rest.get_event(rest.url_path(['events', 'service', service_id], params=rest.get_event_time()), 'login', 'service')

    print is_event

@pytest.mark.demo
def test_4():
    response = rest.post(rest.url_path('env-files'), 'envfiles.json', primary='name')
    if isinstance(response, dict):
        result.update_check_point('test_4', 'create env file succeed', False, True, 'success')
    else:
        content = rest.get_content(response, 'p')
        result.update_check_point('test_4', 'create env file succeed', True, False, content)
    envfile_name = rest.get_value(response, 'name')
    envfile_uuid = rest.get_value(response, 'uuid')
    rest.set_value('module_envfiles.json', 'name', envfile_name)

    response = rest.post(rest.url_path(['storage', 'volumes']), 'volume.json', primary='name')
    if isinstance(response, dict):
        result.update_check_point('test_4', 'create volume success', False, True, 'success')
    else:
        result.update_check_point('test_4', 'create volume success', True, False, response)
    volume_name = rest.get_value(response, 'name')
    volume_id = rest.get_value(response, 'id')
    rest.set_value('module_volumes.json', 'volume_name', volume_name)
    rest.set_value('module_volumes.json', 'volume_id', volume_id)
    append_json = ['module_envfiles.json', 'module_volumes.json']
    response = rest.post(rest.url_path('services'), 'basic_service_deployment.json', append_json)
    service_id = rest.get_value(response, 'unique_name')
    service_name = rest.get_value(response, 'service_name')
    if isinstance(response, dict):
        result.update_check_point('test_4', 'create service success', False, True, 'success')
    else:
        result.update_check_point('test_4', 'create service success', True, False, response)

    current_status = rest.get_expected_value(rest.url_path(['services', service_id]), 'current_status', 'Running')

    if current_status:
        result.update_check_point('test_4', 'check service is running', False, True, 'success')
    else:
        result.update_check_point('test_4', 'check service is running', True, False, 'failure')

    is_expected = exec_helper.get_expect_string(service_id, 'export', "A='1'")  # check环境变量
    if is_expected:
        result.update_check_point('test_4', 'check env success in containers', False, True, 'success')
    else:
        result.update_check_point('test_4', 'check env success in containers', False, False, 'failure')

    is_exist = exec_helper.exist_file(service_id, '/demo')
    if is_exist:
        result.update_check_point('test_4', 'check host path volume exist', False, True, 'success')
    else:
        result.update_check_point('test_4', 'check host path volume exist', False, False, 'failure')

    content = rest.get(rest.get_service_url(service_name))
    if 'nginx web server' in content:
        result.update_check_point('test_4', 'check service could access', False, True, content)
    else:
        result.update_check_point('test_4', 'check service could access', False, False, content)

    rest.resource_url.append(rest.url_path(['services', service_id]))
    rest.resource_url.append(rest.url_path(['env-files', envfile_uuid]))
    rest.resource_url.append(rest.url_path(['storage', 'volumes', volume_id]))



def test_5():
    response1 = rest.post(rest.url_path('services'), 'basic_service_deployment.json')

    service_id = rest.get_value(response1, 'unique_name')

    service_name = rest.get_value(response1, 'service_name')

    response2 = rest.get(rest.url_path(['services', service_id]))

    current_status = rest.get_value(response2, 'current_status')

    print current_status

    container_port = rest.circle_get_value(rest.url_path(['services', service_id]), 'container_port', entry='raw_container_ports')

    print container_port

    response3 = rest.get(rest.url_path(['load_balancers', rest.lb_id]))

    domain = rest.get_value(response3, 'domain', entry='domain_info', index=1)

    service_url = rest.get_service_url(service_name, domain, container_port)

    content = rest.get_content(rest.get(service_url), 'title')
    print content


def test_6():
    service_id = 'abdb817c-a95b-4850-9485-7a7ff1f95faa'
    is_expected = exec_helper.get_expect_string(service_id, 'export', "A='1'")  # check环境变量
    print is_expected
