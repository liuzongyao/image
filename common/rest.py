#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
import requests
import json
import time
import os
import shutil
import dpath.util
import re
from common import common


class Rest:

    def __init__(self):

        self.api = common.env['api']
        self.header = {'Authorization': 'Token ' + self._get_token()}
        self.region = common.env['region_name']
        self.namespace = common.env['namespace']
        self.space = common.env['space_name']
        self.json_dir = common.env['json_dir']
        self.resource_url = []
        self._update_all_template(common.env)
        common.master = self._get_master()

    def _update_all_template(self, environment):
        json_file = []
        for root, dirs, files in os.walk(self.json_dir):
            for fn1 in files:
                if os.path.splitext(fn1)[1] == '.json':
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
        print self.api

        url = self.api + 'v1' + '/generate-api-token'
        payload = {"organization": common.env['namespace'], "username": common.env['username'], "password": common.env['password']}
        data = json.dumps(payload)
        header = {'Content-Type': 'application/json'}
        try:
            r = requests.post(url, data=data, headers=header)
            token = json.loads(r.text)['token']
            return token
        except Exception as e:
            print('post请求出错,原因:%s' % e)

    def _get_master(self):

        response, code = self.get(self.url_path('/load_balancers/{namespace}', self.namespace, params={'region_name': self.region}))

        response = json.loads(response)

        return response[0]['address']

    def url_path(self, url, args='', version='v1', params=None):
        url = re.sub(r'{.*?}', '{}', url).format(*args if isinstance(args, tuple) else (args,))
        if params:
            keys = params.keys()
            values = params.values()
            param = '?' + keys[0] + '=' + values[0]
            for i in range(1, len(keys)):
                param = param + '&' + keys[i] + '=' + values[i]
            print self.api + version + url + param
            return self.api + version + url + param
        else:
            print self.api + version + url
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
            return r.text, r.status_code
        except Exception as e:
            print('get请求出错,出错原因:%s' % e)

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
        temp_template = self.generate_data_template(data_template, append_template, **kwargs)
        response = json.load(open(temp_template))
        if "files" in response.keys():
            files = {'file': open(response["files"], 'rb')}
            response.pop("files")
            data = json.dumps(response)
            try:
                common.start_time = common.get_start_time()
                self.header.update({'Content-Type': 'multipart/form-data'})
                r = requests.post(url_path, data=data, files=files, headers=self.header)
                r.encoding = 'UTF-8'
                return r.text, r.status_code
            except Exception as e:
                print('post请求出错,原因:%s' % e)
            finally:
                common.end_time = common.get_end_time()
        else:
            data = json.dumps(response)
            try:
                common.start_time = common.get_start_time()
                self.header.update({'Content-Type': 'application/json'})
                r = requests.post(url_path, data=data, headers=self.header)
                r.encoding = 'UTF-8'
                return r.text, r.status_code
            except Exception as e:
                print('post请求出错,原因:%s' % e)
            finally:
                common.end_time = common.get_end_time()

    def delete(self, url_path):
        """
        request delete 操作
        :param url_path: url_path方法返回值，作为此处的地址
        :return:
        """
        try:
            r = requests.delete(url_path, headers=self.header)
            r.encoding = 'UTF-8'
            return r.text, r.status_code

        except Exception as e:
            print('delete,出错原因:%s' %e)

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
        第二版本set value方法
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
                    current['index'] = current['index'] + 1
                    return response
                else:
                    current['index'] = current['index'] + 1
            else:
                if type(v) == dict:
                    self.__set_value(v, key, value, index, current)
                elif type(v) == list:
                    for i in range(len(v)):
                        self.__set_value(v[i], key, value, index, current)
                else:
                    continue

    def get_value(self, response, key, **kwargs):
        """
        第二版get value方法，get_value(response, 'node_port', entry='results', index=2)
        :param response: request请求产后的response中的text
        :param key: 需要的key
        :param kwargs: key: entry 参数key的最开头的入口，从这个往下轮询。 index 代表多个中的某个,从1开始
        :return: key的value
        """
        try:
            response = json.loads(response)
            #当取load balance的时候 此处的结果是list
            if isinstance(response, dict):
                if not kwargs:
                    return response[key], True
                else:
                    if 'entry' in kwargs.keys():
                        glob = kwargs['entry'] + '/**/' + key
                        response1 = dpath.util.search(response, glob=glob)
                        if 'index' in kwargs.keys():
                            return self.__get_value(response1, key, {'index': 1}, kwargs['index']), True
                        else:
                            return self.__get_value(response1, key, {'index': 1}, 1), True
                    else:
                        if 'index' in kwargs.keys():
                            return self.__get_value(response, key, {'index': 1}, kwargs['index']), True
                        else:
                            return self.__get_value(response, key, {'index': 1}, 1), True
            elif isinstance(response, list):
                for i in range(len(response)):
                    response = response[i]
                    if not kwargs:
                        return response[key], True
                    else:
                        if 'entry' in kwargs.keys():
                            glob = kwargs['entry'] + '/**/' + key
                            response1 = dpath.util.search(response, glob=glob)
                            if 'index' in kwargs.keys():
                                return self.__get_value(response1, key, {'index': 1}, kwargs['index']), True
                            else:
                                return self.__get_value(response1, key, {'index': 1}, 1), True
                        else:
                            if 'index' in kwargs.keys():
                                return self.__get_value(response, key, {'index': 1}, kwargs['index']), True
                            else:
                                return self.__get_value(response, key, {'index': 1}, 1), True
                else:
                    return "返回信息错误，既不是字典格式，也不是列表格式", False

        except ValueError:
            return response, False

    def __get_value(self, response, key, current, index):
        """
        第二版get value的中间函数
        :param response: 经过dpath寻找后的内容，缩小搜索范围
        :param key: 需要的key
        :return: 将具有相同的key的value组成列表返回
        """

        for k, v in response.items():
            if k == key:
                if current['index'] == index:
                    return v
                else:
                    current['index'] = current['index'] + 1
            else:
                if type(v) == dict:
                    a = self.__get_value(v, key, current, index)
                    if a:
                        return a
                elif type(v) == list:
                    for i in range(len(v)):
                        b = self.__get_value(v[i], key, current, index)
                        if b:
                            return b
                else:
                    continue

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
            response, code = self.get(url_path)
            founder = self.get_value(response, key, **kwargs)[0]
            if founder == expected_value:
                return "find the expected value {}".format(expected_value), True
            else:
                time.sleep(5)
                i = i + 1
        return "get value {}, but the expected value {}".format(founder, expected_value), False

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

    def get_service_url(self, service_name, port=80, http='http'):
        """
        获得服务地址方法
        :param service_name:
        :param domain:
        :param container_port: 不提供时和容器暴露端口相同，提供时是load balance上的监听端口60000-65555
        :param http:
        :return:
        """

        response, code = rest.get(rest.url_path('/load_balancers/{namespace}', common.env['namespace'], params={'region_name': common.env['region_name'], 'frontend': 'true'}))
        response = json.loads(response)
        for i in range(len(response)):
            for j in range(len(response[i]['domain_info'])):

                if response[i]['domain_info'][j]['type'] == 'default-domain':
                    domain = response[i]['domain_info'][j]['domain']
                    break
            break
        service_url = http + '://' + service_name + '.' + self.space + '.' + domain + ':' + port.__str__()
        print service_url
        return service_url

    @staticmethod
    def get_event_params(size='20', **kwargs):
        if kwargs:
            pass
        params = {'start_time': '{}'.format(common.start_time), 'end_time': '{}'.format(common.end_time), 'size': size}
        return params

    @staticmethod
    def get_log_parames(**kwargs):
        if kwargs:
            pass
        end_time = time.time()
        start_time = end_time - 604800
        params = {'start_time': '{}'.format(start_time), 'end_time': '{}'.format(end_time)}
        return params

    @staticmethod
    def get_metric_params(agg, metric_name, where, **kwargs):
        if kwargs:
            pass
        params = {'q': '{}:{}{{service_id={}}}'.format(agg, metric_name, where)}
        return params

    def get_event(self, url_path, operation, resource_type):
        time.sleep(5)
        response, code = self.get(url_path)
        if self.get_value(response, 'operation', entry='results')[0] == operation and self.get_value(response, 'resource_type', entry='results')[0] == resource_type:
            return "测试通过", True
        elif self.get_value(response, 'total_items')[0] > 1:
            for index in range(1, self.get_value(response, 'total_items')[0] + 1):
                if self.get_value(response, 'operation', entry='results', index=index)[0] == operation and self.get_value(response, 'resource_type', entry='results', index=index)[0] == resource_type:
                    return "测试通过", True
        else:
            return response, False

    def get_log(self, url_path):
        time.sleep(5)
        response, code = self.get(url_path)
        response = json.loads(response)
        if len(response) > 0 and code == 200:
            return "测试通过", True
        else:
            return "no logs for this service", False

    def get_metric(self, url_path, dps):
        time.sleep(5)
        response, code = self.get(url_path)
        response = json.loads(response)
        if isinstance(response, list):
            for i in range(len(response)):
                data = response[i][dps]
                if data:
                    for index in range(len(data.values())):
                        if len(data.values()) > 20 and data.values()[index]:
                            return "测试通过", True
        else:
            return "no metric for this service", False

    def update_load_balance(self):
        response, code = self.get(self.url_path('/load_balancers/{namespace}', common.env['namespace'], params={'region_name': common.env['region_name'], 'frontend': 'true'}))
        load_balance_name, code = self.get_value(response, 'name')
        load_balance_id, code = self.get_value(response, 'load_balancer_id')
        load_balance_type, code = self.get_value(response, 'type')
        self.set_value('module_load_balance.json', 'load_balancer_id', load_balance_id)
        self.set_value('module_load_balance.json', 'name', load_balance_name)
        self.set_value('module_load_balance.json', 'type', load_balance_type)


rest = Rest()
