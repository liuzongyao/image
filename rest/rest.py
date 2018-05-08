#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import yaml
import requests
import json
import time
import os

class Alauda:

    def __init__(self, envfile):
        self.envfile = envfile
        f = open(self.envfile)
        env = yaml.load(f)
        self.header = {'Content-Type': 'application/json', 'Authorization': 'Token ' + env['token']}
        self.apiv1 = env['apiv1']
        self.region = env['region_name']
        self.namespace = env['namespace']
        self.env_file = env['env_file']
        self.json_dir = env['json_dir']
        self.resource_url = []
        jsonfile = []
        for root, dirs, files in os.walk(self.json_dir):
            for fn1 in files:
                if os.path.splitext(fn1)[1] == '.json':
                    jsonfile.append(os.path.join(root, fn1))
        print jsonfile

        for fn2 in jsonfile:
            f1 = open(fn2)
            jsondata = json.load(f1)
            for key, value in env.items():
                # if jsondata.has_key(key):
                if key in jsondata.keys():
                    jsondata.update({key: value})
            f1.close()
            f2 = open(fn2, 'w')
            json.dump(jsondata, f2, indent=2)  # indent 值代表格式化json文件
            f2.close()


    def replace_env(self, envfile, jsondir):
        f = open(envfile)
        env = yaml.load(f)
        jsonfile = []
        for root, dirs, files in os.walk(jsondir):
            for fn1 in files:
                if os.path.splitext(fn1)[1] == '.json':
                    jsonfile.append(os.path.join(root, fn1))

        for fn2 in jsonfile:
            f1 = open(fn2)
            jsondata = json.load(f1)
            for key, value in env.items():
                if jsondata.has_key(key):
                    jsondata.update({key: value})
            f1.close()
            f2 = open(fn2, 'w')
            json.dump(jsondata, f2, indent=2)  # indent 值代表格式化json文件
            f2.close()

    def complete_path(self, resource_url):
        return self.apiv1 + resource_url

    def get(self, resource_url, params=None, **kwargs):
        r"""Sends a GET request.

            :param url: URL for the new :class:`Request` object.
            :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
            :param \*\*kwargs: Optional arguments that ``request`` takes.
            :return: :class:`Response <Response>` object
            :rtype: requests.Response
            """
        print self.complete_path(resource_url)
        try:
            r = requests.get(self.complete_path(resource_url), headers=self.header, **kwargs)
            r.encoding = 'UTF-8'
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                print json_response
                exit()
            else:
                json_response = json.loads(r.text)
                return json_response
                print r.status_code
        except Exception as e:
            print('get请求出错,出错原因:%s' % e)
            exit()

    def post(self, resource_url, data_template, **kwargs):

        r"""Sends a POST request.
           :param resource_url : 资源的url不必带前面的host信息.
           :param data_template: 数据模版，是data_template文件下的某一个文件
           :param \*\*kwargs: Optional arguments that ``request`` takes. 可以是key value格式用来替换模版中的值
           :return: :class:`Response <Response>` object
           :rtype: requests.Response
        """
        jsondata = json.load(open(data_template))
        data = json.dumps(jsondata)
        print self.complete_path(resource_url)
        print data
        try:
            r = requests.post(self.complete_path(resource_url), data=data, headers=self.header)
            r.encoding = 'UTF-8'
            print r.status_code
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                print json_response
                exit()
            else:
                json_response = json.loads(r.text)
                return json_response
                print r.status_code

        except Exception as e:
            print('post请求出错,原因:%s' % e)
            exit()


    def delete(self,resource_url):
        r"""Sends a DELETE request.
            :param url: URL for the new :class:`Request` object.
            :param \*\*kwargs: Optional arguments that ``request`` takes.
            :return: :class:`Response <Response>` object
            :rtype: requests.Response
            """
        print self.complete_path(resource_url)
        try:
            r = requests.delete(self.complete_path(resource_url), headers=self.header)
            r.encoding = 'UTF-8'
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                print json_response
                exit()
            else:
                json_response = json.loads(r.text)
                return json_response
                print r.status_code
        except Exception as e:
            print('delete,出错原因:%s' % e)
            exit()

    def generate_data_template(self, data_template, append_json=[], **kwargs):
        # 根据后超的提示，dict update存在key就是更新，不存在就是追加，因此没必要写method

        # filename = './generated_json/data_template_generated.json'
        # jsondata = json.load(open(data_template))
        # if append_json:
        #     for i in range(len(append_json)):
        #         jsondata_append = json.load(open(append_json[i]))
        #         jsondata.update(jsondata_append)
        #         jsonfile = open(filename, 'w')
        #         json.dump(jsondata, jsonfile,indent=2)
        #         jsonfile.close()
        # return filename

        #filename = './generated_json/data_template_generated.json'

        jsondata = json.load(open(data_template))
        if append_json:
            for i in range(len(append_json)):
                jsondata_append = json.load(open(append_json[i]))
                jsondata.update(jsondata_append)
                with open('./data_template/data_template_generated.json', 'w') as f:
                    json.dump(jsondata, f, indent=2)
                    f.close()
        if kwargs:
            for i in range(len(kwargs.keys())):
                jsondata[kwargs.keys()[i]] = kwargs.values()[i]
                with open('./data_template/data_template_generated.json', 'w') as f:
                    json.dump(jsondata, f, indent=2)
                    f.close()

        return './data_template/data_template_generated.json'




    def get_value(self, response, key, resource_type=None):

        r"""
        经常有这样的需要，我希望从前一个post/get请求中拿出一个值，作为下一个请求中的一个参数
        比如希望查看build状态 就需要拿到build id
        :param response: the response from the request
        :param key: the key of what you want to get
        :param resource_type: 不同的资源具有相同的key，比如project name或者region name 分别用project和region作为resource type
        :return: the value of the key

        """
        if resource_type is None: # 处理没有type的常规情况

            keys = response.keys()
            values = response.values() # list
            if key not in keys:
                # 处理字典嵌套情况
                for value in values:
                    if type(value) == list and value and type(value[0]) == dict:  # 判断是不是list 不需要加引号,value 列表不为空
                        # print "value0 is :", value[0]
                        # print "value0 type is :", type(value[0])
                        for key2, value2 in value[0].items():
                            if key2 != key:
                                print "not found this key"
                            else:
                                return value2
            else:
                return response[key]
        else:
            return response[resource_type][key]

            # 此处没有再次考虑不同resource之后的嵌套情况
            # 返回这样的case很少。如果需要从这里添加。

    def circle_get_value(self, resource_url, key, circle=1, resource_type=None):
        r"""
        默认等待5s，等待时间通过circle设置

        此处有问题，因为已经拿到了response 所有无论等待多久，值都不会变化
        """
        for i in range(circle):
            time.sleep(5)  # meeting 决定change 粒度为5

        response = self.get(resource_url)

        return self.get_value(response, key, resource_type)

    def get_expected_value(self, resource_url, key, expected_value, circle=1, resource_type=None):

        if self.circle_get_value(resource_url, key, circle, resource_type) == expected_value:
            return True
        else:
            return False

    def get_multiple_values(self, response, key_list=[], resource_type=None):
        key_values = []
        for key in key_list:
            key_values.append(self.get_value(response, key, resource_type))
        return key_values


env_dist = os.environ
if env_dist.has_key("env_key"):
    env_value = os.getenv("env_key")
else:
    env_value = './config/env_staging.yaml'

alauda = Alauda(env_value)

r"""
alauda = Alauda('./config/env_new_int.yaml')
每个test case开始都需要更新alauda 但更改环境env文件时，需要更改的地方回很多，
转为在rest文件中申请一个instance

"""
