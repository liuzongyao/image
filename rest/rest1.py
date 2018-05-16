#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import yaml
import requests
import json
import time
import os
import shutil
import dpath.util

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
                if key in jsondata.keys():
                    jsondata.update({key: value})
            f1.close()
            f2 = open(fn2, 'w')
            json.dump(jsondata, f2, indent=2)  # indent 值代表格式化json文件
            f2.close()

    def url_path(self, resource, version='v1', params=None, **kwargs):
        """
        该函数用来产生request请求的url
        :param resource: 资源值来自resource_list = ['services', 'env-files', 'storage']会添加更多的资源，通常是请求的第一个
        :param version: 代表api版本，v1适用old v2适用new
        :param params: 代表请求的params参数，格式 params={'project_name': 'automation'}
        :param kwargs: 额外的url参数，格式service_name=service_name则该参数会以'/'+内容追加到url后面
        :return: 返回一个完整的url地址。
        """
        param = ''
        if version == 'v1':
            resource_list = ['services', 'env-files', 'storage']
            if resource not in resource_list:
                print("the resource {} does not exist, should in {}".format(resource, resource_list))
            address = '/' + resource + '/' + self.namespace
            if kwargs:
                for key, value in kwargs.items():
                    address = address + '/' + value
            if params:
                keys = params.keys()
                values = params.values()
                if len(keys) == 1:
                    param = '?' + keys[0] + '=' + values[0]
                else:
                    param = '?' + keys[0] + '=' + values[0]
                    for i in range(1, len(keys)):
                        param = param + '&' + keys[i] + '=' + values[i]

            print self.apiv1 + address + param
            return self.apiv1 + address + param
        if version == 'v2':
            pass



    def get(self, url_path):
        """
        request get请求
        :param url_path: url_path方法返回值，作为此处的地址
        :return: reponse对象
        """

        try:
            r = requests.get(url_path, headers=self.header)
            r.encoding = 'UTF-8'
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                print json_response
            else:
                json_response = json.loads(r.text)
                return json_response
                print r.status_code
        except Exception as e:
            print('get请求出错,出错原因:%s' % e)

    def post(self, url_path, data_template, append_template=None, primary='service_name', **kwargs):
        """
        request post请求
        :param url_path:   url_path方法返回值，作为此处的地址
        :param data_template: 基于的数据模版
        :param append_template: 以列表追加的数据
        :param primary: 该资源的主键，如果相同会导致创建失败。
        :param kwargs: 对前面产生的数据模版作数据替换
        :return:
        """
        temp_template = self.generate_data_template(data_template, append_template, primary, **kwargs)
        response = json.load(open(temp_template))
        data = json.dumps(response)
        try:
            r = requests.post(url_path, data=data, headers=self.header)
            r.encoding = 'UTF-8'
            print r.status_code
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                print json_response
            else:
                json_response = json.loads(r.text)
                return json_response
                print r.status_code

        except Exception as e:
            print('post请求出错,原因:%s' % e)

    def delete(self, url_path):
        """
        request delete 操作
        :param url_path: url_path方法返回值，作为此处的地址
        :return:
        """
        try:
            r = requests.delete(url_path, headers=self.header)
            r.encoding = 'UTF-8'
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                return json_response
            else:
                #  json_response = json.loads(r.text)
                #  删除操作成功后没有text，此处操作会失败
                return r.status_code
        except Exception as e:
            print('delete,出错原因:%s' % e)

    def generate_data_template(self, data_template, append_template=[], primary='service_name', **kwargs):
        """
        数据模版产生方法
        :param data_template: 基础数据模版
        :param append_template: 追加的数据模版，list
        :param primary: 数据模版主键
        :param kwargs: 需要替换的数据 dict
        :return: 数据模版完整的文件 json
        """
        temp_template = self.json_dir + 'data_template_generated.json'
        data_template = self.json_dir + data_template
        if append_template:
            for i in range(len(append_template)):
                append_template[i] = self.json_dir + append_template[i]

        shutil.copyfile(data_template, temp_template)
        now = 'alauda' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        if append_template:
            for i in range(len(append_template)):
                json_append = json.load(open(append_template[i]))
                self.__update_data(temp_template, json_append)
            if kwargs:
                if primary in kwargs.keys():
                    self.__update_data(temp_template, kwargs)
                else:
                    kwargs.update({primary: now})
                    self.__update_data(temp_template, kwargs)
            else:
                self.__update_data(temp_template, {primary: now})
        elif kwargs:
            if primary in kwargs.keys():
                self.__update_data(temp_template, kwargs)
            else:
                kwargs.update({primary: now})
                self.__update_data(temp_template, kwargs)
        else:
            self.__update_data(temp_template, {primary: now})
        return temp_template

    def __update_data(self, temp_template, content):
        """
        内部数据更新方法
        :param temp_template: 原数据
        :param content: 追加数据 json
        :return: 追加后完整数据 json
        """
        response = json.load(open(temp_template))
        response.update(content)
        with open(temp_template, 'w') as f:
            json.dump(response, f, indent=2)
            f.close()

    def set_value(self, data_template, paths=[], values=[]):
        """
        第一版set value方法
        :param data_template: 原数据
        :param paths: 需要更改的数据key，需要完整的dpath格式 list
        :param values: 需要更改的数据value list
        :return: 追加后完整数据 json
        """
        data_template = self.json_dir + data_template
        response = json.load(open(data_template))
        for i in range(len(paths)):
            path = paths[i]
            value = values[i]
            dpath.util.set(response, path, value)
            with open(data_template, 'w') as f:
                json.dump(response, f, indent=2)
                f.close()

        return data_template

    def set_value1(self, data_template, key, value, index=1, current={'index': 0}):
        """
        第二版本set value方法
        :param data_template: 原数据
        :param key: 需要更改的数据key
        :param value: 需要更改的数据value
        :param index:如果数据模版中有多个key通过index来区分，从1开始
        :param current: 内部参数使用，递归函数的中止条件参数
        :return: 更改后的json文件
        """
        data_template = self.json_dir + data_template
        response = json.load(open(data_template))
        self.__set_value(response, key, value, index, current={'index': 0})
        with open(data_template, 'w') as f:
            json.dump(response, f, indent=2)
            f.close()

    def __set_value(self, response, key, value, index, current={'index':0}):
        """
        内部set value方法的中间方法
        :param response: set_value1方法中的data tempalte产生的解释后的字典
        :param key: 需要更改的数据key
        :param value: 需要更改的数据value
        :param index:如果数据模版中有多个key通过index来区分，从1开始
        :param current: 内部参数使用，递归函数的中止条件参数
        :return: 更改后的json文件
        """
        for k, v in response.items():
            if k == key:
                current['index'] = current['index'] + 1
                if current['index'] == index:
                    response.update({key: value})
                    is_updated = True
                    return response
            else:
                if type(v) == dict:
                    is_updated = self.__set_value(v, key, value, index, current)
                    if is_updated:
                        return response
                elif type(v) == list:
                    for i in range(len(v)):
                        is_updated = self.__set_value(v[i], key, value, index, current)
                        if is_updated:
                            return response
                else:
                    continue

    def get_value(self, response, key):
        """
        第一版get value方法
        :param response: request请求产后的response中的text
        :param key: 满足dpath格式的key
        :return: key的value
        """

        return dpath.util.get(response, key)

    def get_value1(self, response, key, **kwargs):
        """
        第二版get value方法，get_value1(response, 'node_port', entry='results')
        :param response: request请求产后的response中的text
        :param key: 需要的key
        :param kwargs: key: entry 参数key的最开头的入口，从这个往下轮询。 index 代表多个中的某个
        :return: key的value
        """
        if not kwargs:
            return response[key]
        else:
            glob = kwargs['entry'] + '/**/' + key
            response1 = dpath.util.search(response, glob=glob)
            if 'index' in kwargs.keys():
                return self.__get_value(response1, key)[kwargs['index']]
            else:
                return self.__get_value(response1, key)[0]

    def __get_value(self, response, key):
        """
        第二版get value的中间函数
        :param response: 经过dpath寻找后的内容，缩小搜索范围
        :param key: 需要的key
        :return: 将具有相同的key的value组成列表返回
        """
        results = []
        for k, v in response.items():
            if k == key:
                results.append(v)
            else:
                if type(v) == dict:
                    results = results + self.__get_value(v, key)
                elif type(v) == list:
                    for i in range(len(v)):
                        results = results + self.__get_value(v[i], key)
                else:
                    continue
        return results

    def circle_get_value(self, resource_url, key):
        """
        经过一段时间去或许某个值，比如服务最后的状态是否是running 需要多次get，配合get value
        :param resource_url:
        :param key:
        :return:
        """
        i = 0
        while i < 10:
            response = self.get(resource_url)
            time.sleep(5)
            print response
            try:
                return self.get_value(response, key)
            except KeyError:
                i = i+1
                print i
        print "did not get the value"


    def circle_get_value1(self, url_path, key, **kwargs):
        """
        结合第二版get value
        :param url_path: 多次查找的url
        :param key: 查找的key
        :param kwargs: 参考get value
        :return:
        """
        i = 0
        while i < 10:
            response = self.get(url_path)
            time.sleep(5)
            print response
            try:
                return self.get_value1(response, key, **kwargs)
            except KeyError:
                i = i+1
                print i
        print "did not get the value"

    def get_expected_value(self, resource_url, key, expected_value):
        """
        判断获得的值是否是期望的
        :param resource_url:
        :param key:
        :param expected_value:
        :return:
        """

        if self.circle_get_value(resource_url, key) == expected_value:
            return True
        else:
            return False

    def get_multiple_values(self, response, key_list=[]):
        """
        一次获得多个值
        :param response:
        :param key_list:
        :return:
        """
        key_values = []
        for key in key_list:
            key_values.append(self.get_value(response, key))
        return key_values


env_dist = os.environ
if 'env_key' in env_dist.keys():
    env_value = os.getenv("env_key")
else:
    env_value = './config/env_staging.yaml'

alauda = Alauda(env_value)

r"""
alauda = Alauda('./config/env_new_int.yaml')
每个test case开始都需要更新alauda 但更改环境env文件时，需要更改的地方回很多，
转为在rest文件中申请一个instance

"""
