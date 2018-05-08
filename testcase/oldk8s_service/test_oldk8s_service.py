from rest.rest import alauda
import pytest


def setup_function(function):
    print ("setup_function------>")


def teardown_function(function):
    print ("teardown_function--->")
    for i in range(len(alauda.resource_url)):
        alauda.delete(alauda.resource_url[i])
    alauda.resource_url = []



def test_create_basic_service_deployment():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/basic_service_deployment.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port = alauda.get_value(response2, 'container_port')

    print container_port

    assert 'running' in 'running'



def test_create_basic_service_dameonset():

    resource1_url = '/services/' + alauda.namespace

    response1 = alauda.post(resource1_url, './data_template/basic_service_dameonset.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port = alauda.get_value(response2, 'container_port')

    print container_port
    #
    # response3 = alauda.delete(resource2_url)
    #
    # print response3

    assert 'running' in 'running'


def test_create_basic_service_statefulset():
    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/basic_service_statefulset.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port = alauda.get_value(response2, 'container_port')

    print container_port

    assert 'running' in 'running'



def test_get_basic_service_deployment_status():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/basic_service_deployment.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    current_status = alauda.circle_get_value(resource2_url, 'current_status', circle=10)

    print current_status

    assert 'running' in 'running'



def test_create_basic_service_deployment_update_service_name():
    resource1_url = '/services/' + alauda.namespace
    filename = alauda.generate_data_template('./data_template/basic_service_deployment.json', service_name="demo123")
    response1 = alauda.post(resource1_url, filename)
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)
    print type(response1)
    assert 'running' in 'running'



def test_create_basic_service_deployment_append_envvar():

    resource1_url = '/services/' + alauda.namespace
    filename = alauda.generate_data_template('./data_template/basic_service_deployment.json', ['./data_template/module_instance_envvars.json'])
    response1 = alauda.post(resource1_url, filename)
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    assert 'running' in 'running'



def test_create_basic_service_deployment_with_expected_status():

    resource1_url = '/services/' + alauda.namespace

    response1 = alauda.post(resource1_url, './data_template/basic_service_deployment.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    current_status = alauda.get_expected_value(resource2_url, 'current_status', 'Running', circle=10)

    print current_status

    assert current_status



def test_create_basic_service_deployment_append_lb():

    resource1_url = '/services/' + alauda.namespace
    filename = alauda.generate_data_template('./data_template/basic_service_deployment.json', ['./data_template/module_load_balancers.json'], service_name="demo123")
    response1 = alauda.post(resource1_url, filename)
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    assert 'running' in 'running'



def test_create_basic_service_deployment_appendm():

    resource1_url = '/services/' + alauda.namespace
    append_json = ['./data_template/module_labels.json','./data_template/module_instance_envvars.json']
    filename = alauda.generate_data_template('./data_template/basic_service_deployment.json', append_json)
    response1 = alauda.post(resource1_url, filename)
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    assert 'running' in 'running'

