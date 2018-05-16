#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
def set_value(response, key, value, index, current={'index': 0}):
    print type(response)

    for k, v in response.items():
        if k == key:
            current['index'] = current['index'] + 1
            if current['index'] == index:
                response.update({key: value})
                is_updated = True
                return is_updated
        else:
            if type(v) == dict:
                is_updated = set_value(v, key, value, index, current)
                if is_updated:
                    return is_updated
            elif type(v) == list:
                for i in range(len(v)):
                    is_updated = set_value(v[i], key, value, index, current)
                    if is_updated:
                        return is_updated
            else:
                continue


response = json.load(open('./data_template/module_kube_config.json'))
set_value(response, 'values', '[test12,ttt]', 2)

print response
for k, v in response.items():
    print k





# resource = 'service'
# resource_list = ['services','env-files']
# if resource not in resource_list:
#     print("the resource {} does not exist in {}".format(resource,resource_list))
# for value in resource_list:
#     print value
#
# def test_args(first, *args):
#    print 'Required argument: ', first
#    if args:
#        for v in args:
#           print 'Optional argument: ', v

#
# #
# response = json.load(open('./data_template/demo.json'))
#
# print response
#
#a = {u'created_at': u'2018-05-11T03:26:56.140445', u'unique_name': u'27bfe8f6-e0ab-4d31-b67b-6ee307fdfad2', u'last_autoscale_datetime': u'None', u'app_name': None, u'mount_points': [], u'service_name': u'alauda20180511112655', u'labels': [{u'editable': False, u'propagate': False, u'key': u'space', u'value': u'staging'}], u'updated_at': u'2018-05-11T03:26:56.150079', u'update_strategy': {u'max_unavailable': 1, u'max_surge': 0}, u'target_state': u'STARTED', u'instance_envvars': {}, u'service_namespace': u'default--staging', u'space_name': u'staging', u'space_uuid': u'2b68ab46-921b-4990-a68a-493d1c7a9077', u'region_id': u'e792bca0-3aad-42f3-9c2d-7b8cace0ac09', u'resource_actions': [u'service:create', u'service:delete', u'service:start', u'service:stop', u'service:update', u'service:view'], u'uuid': u'27bfe8f6-e0ab-4d31-b67b-6ee307fdfad2', u'linked_to_apps': {}, u'custom_instance_size': {u'mem': 256, u'cpu': 0.125}, u'subnet_id': None, u'pod_controller': u'Deployment', u'namespace': u'testorg001', u'entrypoint': u'', u'node_selector': {u'ip': u'10.23.0.7'}, u'autoscaling_config': u'{}', u'run_command': u'', u'custom_domain_name': None, u'linked_to_services': [], u'project_name': u'', u'raw_container_ports': [{u'protocol': u'tcp', u'container_port': 80}], u'region_name': u'laok8sazure', u'healthy_num_instances': 0, u'scaling_mode': u'MANUAL', u'image_name': u'index-staging.alauda.cn/library/nginx', u'network_mode': u'FLANNEL', u'health_checks': [], u'linked_from_apps': {}, u'load_balancers': [], u'target_num_instances': 1, u'current_num_instances': 0, u'envfiles': [], u'region_uuid': u'e792bca0-3aad-42f3-9c2d-7b8cace0ac09', u'instances': [], u'space_id': u'2b68ab46-921b-4990-a68a-493d1c7a9077', u'kube_config': {u'services': [{u'type': u'ClusterIP', u'editable': False, u'name': u'alauda20180511112655'}], u'pod': {u'podAffinity': {}, u'labels': {}, u'podAntiAffinity': {}}}, u'container_manager': u'KUBERNETES', u'current_status': u'Starting', u'ports': [80], u'exec_endpoint': u'23.99.114.240', u'instance_size': u'XXS', u'volumes': [], u'project_uuid': u'', u'is_stateful': False, u'image_tag': u'latest', u'region': {u'display_text': u'laok8sazure', u'name': u'laok8sazure'}, u'mipn_enabled': False}
#
#
#a = dpath.util.search(response, 'kube_config/**/values')




#
# if '99a9e969-5e85-4f3c-a433-c2af4835aef3' in a:
#     print "yes"
# else:
#     print("np")
#

# def get_value(response,dest):
#
#     for key, value in response.items():
#         print key
#         print value
#         if type(value) == dict:
#             return get_value(value, dest)
#         else:
#             return value




#
# print jsondata['kube_config']['pod']['podAffinity']['requiredDuringSchedulingIgnoredDuringExecution'][0]['labelSelector']['matchExpressions'][0]['values']
#
#
#
# dict1 = {'user': 'runoob', 'num': [1, 2, 3]}
#
# dict2 = dict1  # 浅拷贝: 引用对象
# dict3 = dict1.copy()  # 浅拷贝：深拷贝父对象（一级目录），子对象（二级目录）不拷贝，还是引用
#
#
# # 输出结果
# print(dict1)
# print(dict2)
# print(dict3)
#
# print(type(dict1))
# print type(dict2)
# print type(dict3)
#
# a='test.test'
# if '.' in a:
#     print "rrr"


# a='test.1.value.2'
# keys = a.split('.')
# for key in keys:
#     if key.isdigit():
#         print key
#     if key.isalpha():
#         print "z"
#
# key = 'kube_config.pod.podAffinity.requiredDuringSchedulingIgnoredDuringExecution.0.labelSelector.matchExpressions.0.values'
# #
# #key = 'kube_config.pod'
# if '.' in key: # 此处说明，key是嵌套情况。
#     keys = key.split('.')
#     for i in range(len(keys)):
#         if keys[i].isdigit():  # 说明是key
#             temp = response[int(keys[i])]
#             response = temp
#         else:
#             temp = response[keys[i]]
#             response = temp
# print response



# (code,text) = (1,2)
# print code

# import time
# now = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
# print type(now)
# print now

# a = {'a':'1'}
# b = {'c':'2', 'b':'3'}
# a.update(b)
# print a


# content = {'a':1, 'b':2, 'c':3}
# for key, value in content.items():
#     print key
#     print value

#key = 'kube_config/pod/podAffinity/requiredDuringSchedulingIgnoredDuringExecution/0/labelSelector/matchExpressions/0/key'

# def get_value(response, key):
#     results = []
#     for k, v in response.items():
#         if k == key:
#             results.append(v)
#         else:
#             if type(v) == dict:
#                 results = results + get_value(v, key)
#             elif type(v) == list:
#                 for i in range(len(v)):
#                     results = results + get_value(v[i], key)
#             else:
#                 continue
#
#     return results
#
# print type(response)
# xxx = get_value(a,'values')
# print xxx
#
#
# print response['unique_name']

