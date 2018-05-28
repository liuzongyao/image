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
from bs4 import BeautifulSoup
from dateutil import tz
from datetime import datetime
import iso8601


class Alauda:

    def __init__(self, env_file):
        self.env_file = env_file
        f = open(self.env_file)
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
                print "the resource {} does not exist, should in {}".format(resource, resource_list)
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
                html = r.text
                return html
            else:
                json_response = json.loads(r.text)
                return json_response
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
            if r.status_code < 200 or r.status_code >= 300:
                print('get request url was {}'.format(r.url))
                print ('error message {}, error code {}, error type {}'.format(r.text['message'], r.text['code'], r.text['type']))
                return False
            else:
                json_response = json.loads(r.text)
                return json_response

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
            if r.status_code < 200 or r.status_code > 300:  # 说明删除出现问题
                print('delete url was {}'.format(r.url))
                print ('error reason was {}'.format(r.text['message']))
                return False
            else:
                print('delete success, url was {}'.format(r.url))
                return True

        except Exception as e:
            print('delete,出错原因:%s' %e)

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

    def set_value(self, data_template, key, value, index=1):
        """
        第二版本set value方法
        :param data_template: 原数据
        :param key: 需要更改的数据key
        :param value: 需要更改的数据value
        :param index:如果数据模版中有多个key通过index来区分，从1开始
        :return: 更改后的json文件
        """
        data_template = self.json_dir + data_template
        response = json.load(open(data_template))
        self.__set_value(response, key, value, index, {'index': 0})
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
        for k, v in response.items():
            if k == key:
                current['index'] = current['index'] + 1
                if current['index'] == index:
                    response.update({key: value})
                    is_updated = True
                    if is_updated:
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

    def get_value(self, response, key, **kwargs):
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

    def circle_get_value(self, url_path, key, **kwargs):
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
            if response:
                time.sleep(5)
                print response
                try:
                    return self.get_value(response, key, **kwargs)
                except KeyError:
                    i = i+1
                    print i
            else:
                assert False


    def get_expected_value(self, url_path, key, expected_value, **kwargs):
        """
        判断获得的值是否是期望的
        note1：忽略了当第一次就取得返回值 但是和最终结果不一致的情况，比如说期望service是running状态 但是第一次取得是starting 没有继续等待
        :param url_path:
        :param key:
        :param expected_value:
        :return:
        """
        i = 0
        while i < 10:
            if self.circle_get_value(url_path, key, **kwargs) == expected_value:
                return True
            else:
                time.sleep(5)
                i = i + 1
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

    def get_content(self, html, tag):
        soap = BeautifulSoup(html, 'html.parser')
        content = unicode(getattr(getattr(soap, tag), 'string'))
        print type(content)
        return content

    def covert_to_unix(self, create_at):
        # UTC Zone
        #from_zone = tz.gettz('UTC')
        # China Zone
        to_zone = tz.gettz(datetime.now(tz.tzlocal()).tzname())

        # utc = datetime.utcnow()

        utc = iso8601.parse_date(create_at).astimezone(to_zone)

        print type(utc)

        # Tell the datetime object that it's in UTC time zone
        #utc = utc.replace(tzinfo=from_zone)

        # Convert time zone
        # local = datetime.strftime(utc.astimezone(to_zone), "%Y-%m-%d %H:%M:%S")
        #
        t = time.mktime(time.strptime(datetime.strftime(utc, "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
        print type(t)

        return t


file_path = os.path.dirname(__file__)
env_dist = os.environ
if 'env_key' in env_dist.keys():
    env_value = os.getenv("env_key")
else:
    env_value = file_path + '/../config/env_staging.yaml'

rest = Alauda(env_value)