#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
import yaml
import sys
import requests
import json
import time
import os
import shutil
import re
import logging

logger = logging.getLogger()


class Common:
    start_time = ''
    end_time = ''

    def __init__(self):
        file_path = os.path.dirname(__file__)
        env_dist = os.environ
        if 'env_key' in env_dist.keys():
            env_file = os.getenv("env_key")
        else:
            env_file = file_path + '/../config/env_new_int.yaml'
        f = open(env_file)
        self.env = yaml.load(f)
        self.api = self.env['api']
        self.header = {'Authorization': 'Token ' + self._get_token()}
        self.region = self.env['region_name']
        self.namespace = self.env['namespace']
        self.space = self.env['space_name']
        self.json_dir = self.env['json_dir']
        self.resource_url = []
        self.update_all_template(self.env)

    @classmethod
    def get_start_time(cls):
        return time.time()

    @classmethod
    def get_end_time(cls):
        return time.time()

    def update_all_template(self, environment):
        json_file = []
        for root, dirs, files in os.walk(self.json_dir):
            for fn1 in files:
                if os.path.splitext(fn1)[1] == 'deploy.json':
                    json_file.append(os.path.join(root, fn1))
        for fn2 in json_file:
            f1 = open(fn2)
            json_data = json.load(f1)
            for key, value in environment.items():
                if key in json_data.keys():
                    json_data.update({key: value})
            f1.close()
            f2 = open(fn2, 'w')
            json.dump(json_data, f2, indent=2)  # indent 值代表格式化json文件
            f2.close()

    def _get_token(self):
        url = self.api + 'v1' + '/generate-api-token'
        if 'username' in self.env.keys():
            payload = {"organization": self.env['namespace'], "username": self.env['username'], "password": self.env['password']}
        elif 'namespace' in self.env.keys():
            payload = {"username": self.env['namespace'], "password": self.env['password']}
        else:
            sys.exit("sorry, goodbye! could not get token, please check the username/passord right")

        data = json.dumps(payload)
        header = {'Content-Type': 'application/json'}
        try:
            r = requests.post(url, data=data, headers=header)
            if r.status_code == 200:
                token = json.loads(r.text)['token']
                return token
            else:
                sys.exit(r.text + r.url)
        except Exception as e:
            logger.debug('post请求出错,原因:%s' % e)

    def get_master(self):
        response, code, url = self.get(self.url_path('/load_balancers/{namespace}', self.namespace, params={'region_name': self.region}))
        try:
            response = json.loads(response)
            return response[0]['address']
        except ValueError as e:
            logger.debug('post请求出错,原因:%s' % e)

    def url_path(self, url, args='', version='v1', params=None):
        url = re.sub(r'{.*?}', '{}', url).format(*args if isinstance(args, tuple) else (args,))
        if params:
            keys = params.keys()
            values = params.values()
            param = '?' + keys[0] + '=' + values[0]
            for i in range(1, len(keys)):
                param = param + '&' + keys[i] + '=' + values[i]
            return self.api + version + url + param
        else:
            return self.api + version + url

    def get(self, url_path):
        """
        request get请求
        :param url_path: url_path方法返回值，作为此处的地址
        :return: reponse对象
        """
        try:
            r = requests.get(url_path, headers=self.header)
            r.encoding = 'UTF-8'
            return r.text, r.status_code, r.url
        except Exception as e:
            logger.debug('get请求出错,出错原因:%s' % e)

    def post(self, url_path, data_template, append_template=None, **kwargs):
        """
        request post请求
        :param url_path:   url_path方法返回值，作为此处的地址
        :param data_template: 基于的数据模版
        :param append_template: 以列表追加的数据
        :param primary: 该资源的主键，如果相同会导致创建失败。
        :param kwargs: 对前面产生的数据模版作数据替换
        :return:
        """
        if isinstance(data_template, dict):  # 处理只是dict的情况, 此时不需要content-type为json，因为传入的数据是dict
            try:
                Common.start_time = self.get_start_time()
                self.header = {'Authorization': 'Token ' + self._get_token()}
                r = requests.post(url_path, data=data_template, headers=self.header)
                r.encoding = 'UTF-8'
                return r.text, r.status_code, r.url
            except Exception as e:
                logger.debug('post请求出错,原因:%s' % e)
            finally:
                Common.end_time = self.get_end_time()
        else:
            temp_template = self.generate_data_template(data_template, append_template, **kwargs)
            response = json.load(open(temp_template))
            if "files" in response.keys():
                files = {'file': open(response["files"], 'rb')}
                response.pop("files")
                data = json.dumps(response)
                try:
                    Common.start_time = self.get_start_time()
                    self.header.update({'Content-Type': 'multipart/form-data'})
                    r = requests.post(url_path, data=data, files=files, headers=self.header)
                    r.encoding = 'UTF-8'
                    return r.text, r.status_code, r.url
                except Exception as e:
                    logger.debug('post请求出错,原因:%s' % e)
                finally:
                    Common.end_time = self.get_end_time()
            else:
                data = json.dumps(response)
                try:
                    Common.start_time = self.get_start_time()
                    self.header.update({'Content-Type': 'application/json'})
                    r = requests.post(url_path, data=data, headers=self.header)
                    r.encoding = 'UTF-8'
                    return r.text, r.status_code, r.url
                except Exception as e:
                    logger.debug('post请求出错,原因:%s' % e)
                finally:
                    Common.end_time = self.get_end_time()

    def delete(self, url_path):
        """
        request delete 操作
        :param url_path: url_path方法返回值，作为此处的地址
        :return:
        """
        try:
            r = requests.delete(url_path, headers=self.header)
            r.encoding = 'UTF-8'
            return r.text, r.status_code, r.url

        except Exception as e:
            logger.debug('delete,出错原因:%s' % e)

    def generate_data_template(self, data_template, append_template=[], **kwargs):
        """
        数据模版产生方法
        :param data_template: 基础数据模版
        :param append_template: 追加的数据模版，list
        :param kwargs: 需要替换的数据 dict, 必须是完整的数据，比如"node_selector": {"ip": "172.31.19.230"}
        :return: 数据模版完整的文件 json
        """
        temp_template = self.json_dir + 'data_template_generated.json'
        data_template = self.json_dir + data_template
        shutil.copyfile(data_template, temp_template)
        if append_template:
            if isinstance(append_template, list):  # 处理多个json文件，list情形
                for i in range(len(append_template)):
                    append_template[i] = self.json_dir + append_template[i]
                    json_append = json.load(open(append_template[i]))
                    self.__update_data(temp_template, json_append)
                if kwargs:
                    self.__update_data(temp_template, kwargs)
            else:  # 一个json文件，直接给出文件名字
                append_template = self.json_dir + append_template
                json_append = json.load(open(append_template))
                self.__update_data(temp_template, json_append)
                if kwargs:
                    self.__update_data(temp_template, kwargs)
        elif kwargs:
            self.__update_data(temp_template, kwargs)
        return temp_template

    @staticmethod
    def __update_data(temp_template, content):
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

    def set_value(self, data_template, key, value, index=1):
        """
        :param data_template: 原数据
        :param key: 需要更改的数据key
        :param value: 需要更改的数据value
        :param index:如果数据模版中有多个key通过index来区分，从1开始
        :return: 更改后的json文件
        """
        data_template = self.json_dir + data_template
        response = json.load(open(data_template))
        self.__set_value(response, key, value, index, {'index': 1})
        with open(data_template, 'w') as f:
            json.dump(response, f, indent=2)
            f.close()

    def __set_value(self, response, key, value, index, current):
        """
        内部set value方法的中间方法
        :param response: set_value1方法中的data tempalte产生的解释后的字典
        :param key: 需要更改的数据key
        :param value: 需要更改的数据value
        :param index:如果数据模版中有多个key通过index来区分，从1开始，代表希望替换的key的序号
        :param current: 内部参数使用，递归函数的中止条件参数.代表当前key的序号
        :return: 更改后的json文件
        """
        global is_update
        is_update = False
        for k, v in response.items():
            if k == key:
                if current['index'] == index:
                    response.update({key: value})
                    current['index'] += 1
                    return response
                else:
                    current['index'] += 1
            else:
                if type(v) == dict:
                    self.__set_value(v, key, value, index, current)
                elif type(v) == list:
                    for i in range(len(v)):
                        self.__set_value(v[i], key, value, index, current)
                else:
                    continue

    def get_value(self, response, key, substring=''):
        try:
            response = json.loads(response)
        except ValueError as msg:
            return msg, False
        if not substring:
            if key in response.keys():
                return response[key], True
            else:
                results = self.__get_value(response, key)
                return results[0], True  # new k8s app uuid
        else:
            results = self.__get_value(response, key)
            if results:
                for i in range(len(results)):
                    if substring in results[i]:
                        return results[i], True
            else:
                return "could not find the value for key {}".format(key), False

    def __get_value(self, response, key, result=None):
        if result is None:
            result = []
        if isinstance(response, dict):
            for k, v in response.items():
                if k == key:
                    result.append(v)
                else:
                    if type(v) == dict:
                        self.__get_value(v, key, result)
                    elif type(v) == list:
                        for i in range(len(v)):
                            self.__get_value(v[i], key, result)
                    else:
                        continue
        elif isinstance(response, list):
            for i in range(len(response)):
                self.__get_value(response[i], key, result)
        return result

    def get_expected_value(self, url_path, key, expected_value, substring=''):
        i = 0
        while i < 10:
            response, code, url = self.get(url_path)
            founder = self.get_value(response, key, substring)[0]
            if founder == expected_value:
                return "find the expected value {}".format(expected_value), True
            else:
                time.sleep(10)
                i = i + 1
        return "get value {}, but the expected value {}".format(founder, expected_value), False
