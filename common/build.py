#!/usr/bin/env python
# -*- coding:utf-8 -*-
from common import Common
import json


class Build(Common):
    def __init__(self):
        Common.__init__(self)
        self.build_name = ''
        self.build_id = ''
        self.config_id = ''
        self.post_url = self.url_path('/private-build-configs/{namespace}', self.env['namespace'])

    @property
    def build_history_url(self):
        return self.url_path('/private-builds/{namespace}/{build_id}', (self.env['namespace'], self.build_id))

    @property
    def build_history_log_url(self):
        return self.url_path('/private-builds/{namespace}/{build_id}/logs', (self.env['namespace'], self.build_id))

    @property
    def get_endpoint_id(self):
        response, code, url = self.get(self.url_path('/regions/{namespace}/{region}', (self.env['namespace'], self.env['region_name'])))
        region_id, code = self.get_value(response, 'id')
        response, code, url = self.get(self.url_path('/private-build-endpoints/{namespace}', self.env['namespace']))
        print type(json.loads(response))
        for i in range(len(json.loads(response))):
            if json.loads(response)[i]['region_id'] == region_id:
                return json.loads(response)[i]['endpoint_id']

    @property
    def get_image_repo(self):
        if 'private_registry' in self.env.keys():
            response, code, url = self.get(self.url_path('/registries/{namespace}/{regisitry_name}/projects', (self.env['namespace'], self.env['private_registry'])))
            if code == 200:
                if not response == '[]':
                    project_name = json.loads(response)[0]['project_name']
                    response, code, url = self.get(self.url_path('/registries/{namespace}/{regisitry_name}/projects/{project_name}/repositories', (self.env['namespace'], self.env['private_registry'], project_name)))
                    if code == 200:
                        if not response == '[]':
                            name = json.loads(response)[0]['name']
                            return {'project_name': project_name, 'name': name}
                else:
                    response, code, url = self.get(self.url_path('/registries/{namespace}/{regisitry_name}/repositories', (self.env['namespace'], self.env['private_registry'])))
                    if code == 200:
                        if not response == '[]':
                            name = json.loads(response)[0]['name']
                            return {'name': name}

    def update_build_parameter(self, json_file):
        self.set_value(json_file, 'code_repo_path', self.env['code_repo_path'])
        self.set_value(json_file, 'code_repo_username', self.env['code_repo_username'])
        self.set_value(json_file, 'code_repo_password', self.env['code_repo_password'])
        self.set_value(json_file, 'endpoint_id', self.get_endpoint_id)
        image = self.get_image_repo
        if 'project_name' in image.keys():
            image_repo = {'project': {'name': image['project_name']}, 'name': image['name'], 'registry': {'name': self.env['private_registry']}}
        else:
            image_repo = {'name': image['name'], 'registry': {'name': self.env['private_registry']}}
        self.set_value(json_file, 'image_repo', image_repo)

    def create(self, json_file, **kwargs):
        if kwargs:
            response, code, url = self.post(self.post_url, json_file, **kwargs)
        else:
            response, code, url = self.post(self.post_url, json_file)
        if code == 201:
            self.build_name = json.loads(response)['name']
            self.config_id = json.loads(response)['config_id']
            return '创建构建成功。请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code
        else:
            return '创建构建失败。请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code

    def start(self, config_id):
        response, code, url = self.post(self.url_path('/private-builds/{namespace}', self.env['namespace']), {'build_config_name': config_id})
        if code == 201:
            self.build_id = json.loads(response)['build_id']
            return '启动构建成功。请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code
        else:
            return '启动构建失败。请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code

    def get_image(self):
        status, code = self.get_expected_value(self.build_history_url, 'status', 'S')
        if code:
            response, code, url = self.get(self.build_history_url)
            registry_index, code = self.get_value(response, 'registry_index')
            docker_repo_path, code = self.get_value(response, 'docker_repo_path')
            docker_repo_tag, code = self.get_value(response, 'docker_repo_tag')
            image_name = registry_index + '/' + docker_repo_path
            image_tag = docker_repo_tag
            image = dict(image_name=image_name, image_tag=image_tag)
            return image, True
        else:  # 构建失败，输出失败log
            response, code, url = self.get(self.build_history_log_url)
            try:
                log_list = json.loads(response)
                return log_list[-1]['message'], False
            except Exception as e:
                return e, False


build = Build()


