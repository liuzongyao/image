#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24

import yaml
import requests
import json

class Alauda:

    def __init__(self, configfile='./config/env.yaml'):
        self.configfile = configfile
        f = open(self.configfile)
        env = yaml.load(f)
        self.header = {'Content-Type':'application/json','Authorization': 'Token ' + env['token']}
        self.apiv1 = env['apiv1']

    def complete_path(self,resource_url):
        return self.apiv1 + resource_url

    def get(self,resource_url, params=None, **kwargs):
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
            json_response = json.loads(r.text)
            return json_response
        except Exception as e:
            print('get请求出错,出错原因:%s' % e)
            return {}

    def post(self,resource_url, data_template,**kwargs):

        r"""Sends a POST request.
           :param resource_url : 资源的url不必带前面的host信息.
           :param data_template: 数据模版，是data_template文件下的某一个文件
           :param \*\*kwargs: Optional arguments that ``request`` takes. 可以是key value格式用来替换模版中的值
           :return: :class:`Response <Response>` object
           :rtype: requests.Response
           """

        print self.complete_path(resource_url)
        jsondata = json.load(open(data_template))  # dic
        data = json.dumps(jsondata)  # dic to strstr
        print data
        try:
            r = requests.post(self.complete_path(resource_url), data=data, headers=self.header,**kwargs)
            r.encoding = 'UTF-8'
            json_response = json.loads(r.text)
            return json_response
        except Exception as e:
            print('post请求出错,原因:%s' % e)










# def post(self, resource_url, data, **kwargs):
#     headers = self._headers.copy()
#     headers.update(kwargs)
#     if type(data) is dict:
#         data = json.dumps(data)
#     return rest.post(self.complete_path(resource_url), data, **headers)
#
#
# def get(self, resource_url, **kwargs):
#     headers = self._headers.copy()
#     headers.update(kwargs)
#     return rest.get(self.complete_path(resource_url), **headers)
#
#
#
# def post(url, data, **kwargs):
#     __logger.debug("Post %s" % url)
#     if data:
#         __logger.debug(str(data))
#     req = urllib2.Request(url, data, kwargs)
#     req.get_method = lambda: "POST"
#     try:
#         resp = openurl(req)
#         return resp
#     except urllib2.HTTPError, e:
#         return e
#
# def get(url, **kwargs):
#     __logger.debug("Get %s" % url)
#     req = urllib2.Request(url, None, kwargs)
#     req.get_method = lambda: "GET"
#     try:
#         resp = openurl(req)
#         return resp
#     except urllib2.HTTPError, e:
#         return e