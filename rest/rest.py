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

    def _complete_path(self, resource_url, params=None):
        param = ''
        if params:
            keys = params.keys()
            values = params.values()
            if len(keys) == 1:
                param = '?' + keys[0] + '=' + values[0]
            else:
                param = '?' + keys[0] + '=' + values[0]
                for i in range(1,len(keys)):
                    param = param + '&' + keys[i] + '=' + values[i]

        return self.apiv1 + resource_url + param

    def url_path(self, resource, *args):
        resource_list = ['services', 'env-files', 'storage']
        if resource not in resource_list:
            print("the resource {} does not exist, should in {}".format(resource, resource_list))
        address = '/' + resource + '/' + self.namespace
        if args:
            for value in args:
                address = address + '/' + value
        return address



    def get(self, resource_url, params=None, **kwargs):
        """
        :param resource_url:
        :param params:
        :param kwargs:
        :return:
        """

        print self._complete_path(resource_url, params=params)
        try:
            r = requests.get(self._complete_path(resource_url, params), headers=self.header, **kwargs)
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

    def post(self, resource_url, data_template, append_template=None, primary='service_name', params=None, **kwargs):
        r"""
         :param resource_url:
         :param data_template:
         :param append_template:
         :param primary:
         :param params:
         :param kwargs:
         :return:
         """

        temp_template = self.generate_data_template(data_template, append_template, primary, **kwargs)
        jsondata = json.load(open(temp_template))
        data = json.dumps(jsondata)
        print self._complete_path(resource_url, params=params)
        print data
        try:
            r = requests.post(self._complete_path(resource_url, params), data=data, headers=self.header)
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



    def delete(self,resource_url, params=None):
        print self._complete_path(resource_url, params)
        try:
            r = requests.delete(self._complete_path(resource_url, params), headers=self.header)
            r.encoding = 'UTF-8'
            if r.status_code < 200 or r.status_code >= 300:
                json_response = json.loads(r.text)
                return json_response
            else:
                #json_response = json.loads(r.text)  # 删除操作成功后没有text，此处操作会失败
                return r.status_code
        except Exception as e:
            print('delete,出错原因:%s' % e)


    def generate_data_template(self, data_template, append_template=[], primary='service_name', **kwargs):
        # 根据后超的提示，dict update存在key就是更新，不存在就是追加，因此没必要写method
        """
        :param self:
        :param data_template:
        :param append_template:
        :param primary:
        :param kwargs:
        :return:
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
                jsondata_append = json.load(open(append_template[i]))
                self.__update_data(temp_template, jsondata_append)
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

        jsondata = json.load(open(temp_template))
        jsondata.update(content)
        with open(temp_template, 'w') as f:
            json.dump(jsondata, f, indent=2)
            f.close()

    def set_value(self, data_template, paths=[], values=[]):
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
        print type(self.json_dir)
        print type(data_template)
        data_template = self.json_dir + data_template
        response = json.load(open(data_template))
        self.__set_value(response, key, value, index, current={'index': 0})
        with open(data_template, 'w') as f:
            json.dump(response, f, indent=2)
            f.close()


    def __set_value(self, response, key, value, index, current={'index':0}):
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

        return dpath.util.get(response, key)

    def get_value1(self, response, key, **kwargs):

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
        r"""
        此处有问题，因为已经拿到了response 所有无论等待多久，值都不会变化
        """
        i = 0
        while i < 10:
            time.sleep(5)
            response = self.get(resource_url)
            print response
            try:
                return self.get_value(response, key)
            except KeyError:
                i = i+1
                print i
        print "did not get the value"

    def get_expected_value(self, resource_url, key, expected_value):

        if self.circle_get_value(resource_url, key) == expected_value:
            return True
        else:
            return False

    def get_multiple_values(self, response, key_list=[]):
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
