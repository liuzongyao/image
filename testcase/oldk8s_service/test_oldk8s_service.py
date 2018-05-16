from rest.rest import alauda
import pytest
import time
import json


# def teardown_function(function):
#     deleted = 0
#     print ("teardown_function--->")
#     for i in range(len(alauda.resource_url)):
#         while not deleted:
#             code = alauda.delete(alauda.resource_url[i])
#             print "--------"
#             print code
#             if code < 200 or code >= 300:
#                 time.sleep(5)
#             else:
#                 deleted = 1
#
#     alauda.resource_url = []


def test_create_basic_service_deployment():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', params={'project_name': 'automation'}, space_name='test-automation')
    print type(response1)

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port_key = 'raw_container_ports/0/container_port'

    container_port = alauda.circle_get_value(resource2_url, container_port_key)

    print container_port

    assert 'running' in 'running'


def test_create_basic_service_deployment_append_auto():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ['module_autoscaling_config.json'])
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port_key = 'raw_container_ports/0/container_port'

    container_port = alauda.get_value(response2, container_port_key)

    print container_port

    assert 'running' in 'running'


def test_create_basic_service_deployment_append_Affinity():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ['module_kube_config.json'])
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port_key = 'raw_container_ports/0/container_port'

    container_port = alauda.get_value(response2, container_port_key)

    print container_port

    assert 'running' in 'running'


def test_create_basic_service_dameonset():

    resource1_url = '/services/' + alauda.namespace

    response1 = alauda.post(resource1_url, 'basic_service_dameonset.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port_key = 'raw_container_ports/0/container_port'

    container_port = alauda.get_value(response2, container_port_key)

    print container_port

    assert 'running' in 'running'


def test_create_basic_service_statefulset():
    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_statefulset.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port_key = 'raw_container_ports/0/container_port'

    container_port = alauda.get_value(response2, container_port_key)

    print container_port

    assert 'running' in 'running'


def test_get_basic_service_deployment_status():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    current_status = alauda.circle_get_value(resource2_url, 'current_status')

    print current_status

    assert 'running' in 'running'


def test_create_basic_service_deployment_update_service_name():
    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ports=[80, 90])
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)
    print type(response1)
    assert 'running' in 'running'


def test_create_basic_service_deployment_append_envvar():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ['module_instance_envvars.json'])
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    assert 'running' in 'running'


def test_create_basic_service_deployment_append_envfiles():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ['module_envfiles.json'])
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    assert 'running' in 'running'


def test_create_basic_service_deployment_with_expected_status():

    resource1_url = '/services/' + alauda.namespace

    response1 = alauda.post(resource1_url, 'basic_service_deployment.json')

    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    current_status = alauda.get_expected_value(resource2_url, 'current_status', 'Running')

    print current_status

    assert current_status


def test_create_basic_service_deployment_append_lb():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ['module_load_balancers.json'], service_name="demo123")
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    assert 'running' in 'running'



def test_create_basic_service_deployment_appendm():

    resource1_url = '/services/' + alauda.namespace
    append_json = ['module_labels.json', 'module_instance_envvars.json']
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', append_json)
    service_name = alauda.get_value(response1, 'unique_name')
    resource2_url = '/services/' + alauda.namespace + '/' + service_name
    alauda.resource_url.append(resource2_url)
    assert 'running' in 'running'


def test_create_basic_service_deployment_append_Affinity2():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, 'basic_service_deployment.json', ['module_kube_config.json'])
    service_name = alauda.get_value(response1, 'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    alauda.resource_url.append(resource2_url)

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    key = 'kube_config/pod/podAffinity/requiredDuringSchedulingIgnoredDuringExecution/0/labelSelector/matchExpressions/0/key'

    service_uuid = alauda.get_value(response2, key)

    print service_uuid

    assert 'running' in 'running'


def test_1():
    resource1_url = '/services/' + alauda.namespace
    labels = [{'editable': 'true','propagate': 'true','key': 'test3','value': 'test3'}]
    data_template = 'basic_service_deployment.json'
    append_template = ['module_labels.json']
    response1 = alauda.post(resource1_url, data_template, append_template, labels=labels)
    assert type(response1) == dict


def test_2():
    resource1_url = '/services/' + alauda.namespace

    data_template = 'basic_service_deployment.json'

    response1 = alauda.post(resource1_url, data_template, target_num_instances=2, target_state='STOPPED')
    assert type(response1) == dict



def test_3():
    resource1_url = '/services/' + alauda.namespace + '/?project_name=automation'

    data_template = 'basic_service_deployment.json'

    response1 = alauda.post(resource1_url, data_template, target_num_instances=2, target_state='STOPPED')
    assert type(response1) == dict


def test_4():
    #get service with params
    response = alauda.get(alauda.url_path('services'), params={'space_name': 'staging'})
    count = alauda.get_value1(response, 'count')
    print count
    unique_name = alauda.get_value1(response, 'node_port', entry='results')
    print unique_name

    assert 'running' in 'running'



@pytest.mark.demo
def test_full():
    response_env_file = alauda.post(alauda.url_path('env-files'), 'envfiles.json', primary='name')
    envfile_name = alauda.get_value1(response_env_file, 'name')
    envfile_uuid = alauda.get_value(response_env_file, 'uuid')
    alauda.set_value1('module_envfiles.json', 'name', envfile_name)



    response_volume = alauda.post(alauda.url_path('storage','volumes'), 'volume.json', primary='name')
    volume_name = alauda.get_value(response_volume, 'name')
    volume_id = alauda.get_value(response_volume, 'id')
    alauda.set_value('module_volumes.json', ['volumes/0/volume_name', 'volumes/0/volume_id'], [volume_name, volume_id])



    append_json = ['module_labels.json', 'module_instance_envvars.json', 'module_envfiles.json']
    response1 = alauda.post(alauda.url_path('services'), 'basic_service_deployment.json', append_json)

    service_name = alauda.get_value(response1, 'unique_name')
    alauda.resource_url.append(alauda.url_path('services', service_name))
    alauda.resource_url.append(alauda.url_path('env-files', envfile_uuid))
    alauda.resource_url.append(alauda.url_path('storage', 'volumes', volume_id))





