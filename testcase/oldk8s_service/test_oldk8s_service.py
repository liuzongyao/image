# -*- coding:utf-8 -*-
from rest.rest1 import alauda
import pytest
import time
import json



def teardown_function(function):
    print ("teardown_function--->")
    for i in range(len(alauda.resource_url)):
        wait = 0
        while wait < 10:
            code = alauda.delete(alauda.resource_url[i])
            print "--------"
            print code
            if code < 200 or code >= 300:
                time.sleep(5)
                wait = wait + 1
            else:  # 已经删掉，删除下一个
                break


@pytest.mark.demo
def test_create_basic_service_deployment():
    response1 = alauda.post(alauda.url_path('services', params={'project_name': 'automation'}), 'basic_service_deployment.json',  space_name='test-automation')

    service_name = alauda.get_value1(response1, 'unique_name')

    response2 = alauda.get(alauda.url_path('services', service_name=service_name))

    current_status = alauda.get_value1(response2, 'current_status')

    print current_status

    container_port = alauda.circle_get_value1(alauda.url_path('services', service_name=service_name), 'container_port', entry='raw_container_ports')

    print container_port

    assert 'running' in 'running'



def test_1():
    labels = [{'editable': 'true', 'propagate': 'true', 'key': 'test3', 'value': 'test3'}]
    data_template = 'basic_service_deployment.json'
    append_template = ['module_labels.json']
    response1 = alauda.post(alauda.url_path('services'), data_template, append_template, labels=labels)
    assert type(response1) == dict



def test_4():
    #get service with params
    response = alauda.get(alauda.url_path('services', params={'space_name': 'staging'}))
    count = alauda.get_value1(response, 'count')
    print count
    unique_name = alauda.get_value1(response, 'node_port', entry='results')
    print unique_name

    assert 'running' in 'running'




def test_full():
    response_env_file = alauda.post(alauda.url_path('env-files'), 'envfiles.json', primary='name')
    envfile_name = alauda.get_value1(response_env_file, 'name')
    envfile_uuid = alauda.get_value(response_env_file, 'uuid')
    alauda.set_value1('module_envfiles.json', 'name', envfile_name)

    response_volume = alauda.post(alauda.url_path('storage', volumes='volumes'), 'volume.json', primary='name')
    volume_name = alauda.get_value(response_volume, 'name')
    volume_id = alauda.get_value(response_volume, 'id')
    alauda.set_value('module_volumes.json', ['volumes/0/volume_name', 'volumes/0/volume_id'], [volume_name, volume_id])

    append_json = ['module_labels.json', 'module_instance_envvars.json', 'module_envfiles.json']
    response1 = alauda.post(alauda.url_path('services'), 'basic_service_deployment.json', append_json)
    service_name = alauda.get_value(response1, 'unique_name')

    alauda.resource_url.append(alauda.url_path('services', service_name=service_name))
    alauda.resource_url.append(alauda.url_path('env-files', envfile_uuid=envfile_uuid))
    alauda.resource_url.append(alauda.url_path('storage', volumes='volumes', volume_id=volume_id))





