# -*- coding:utf-8 -*-
from .common import Common
import json
import time
from .exec_container import exec_container
import logging

logger = logging.getLogger()


class Service(Common):
    def __init__(self):
        Common.__init__(self)
        self.service_uuid = ''
        self.service_name = ''
        self.apps_uuid = ''
        self.apps_name = ''
        self.metric_params = ''
        self.service_url = ''
        self.post_url_v1 = self.url_path('/services/{namespace}', self.env['namespace'])
        self.post_url_v2 = self.url_path('/apps', version='v2')

    @property
    def service_event_url(self):
        return self.url_path('/events/{namespace}/{resource_type}/{resource_uuid}', (self.env['namespace'], 'service', self.service_uuid),
                             params=self.get_event_params())

    @property
    def apps_event_url(self):
        return self.url_path('/events/{namespace}/{resource_type}/{resource_uuid}', (self.env['namespace'], 'application', self.apps_uuid),
                             params=self.get_event_params())

    @property
    def get_log_url(self):
        return self.url_path('/services/{namespace}/{service_uuid}/logs', (self.env['namespace'], self.service_uuid), params=self.get_log_params())

    @property
    def get_metric_url(self):
        return self.url_path('/monitor/{namespace}/metrics/query', self.env['namespace'], params=self.metric_params, version='v2')

    @property
    def service_get_url(self):
        return self.url_path('/services/{namespace}/{service_uuid}', (self.env['namespace'], self.service_uuid))

    @property
    def apps_get_url(self):
        return self.url_path('/apps/{uuid}', self.apps_uuid, version='v2')

    def create(self, json_file, append_template=None, version='v1', **kwargs):
        if version == 'v1':
            response, code, url = self.post(self.post_url_v1, json_file, append_template, **kwargs)
            if code == 201:
                self.service_uuid = self.get_value(response, 'unique_name')[0]
                self.service_name = self.get_value(response, 'service_name')[0]
                return '创建服务成功。 请求url {}'.format(url), code
            else:
                return '创建服务失败。 请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code
        else:
            response, code, url = self.post(self.post_url_v2, json_file, append_template, **kwargs)
            if code == 201:
                self.apps_uuid = self.get_value(response, 'app.alauda.io/uuid')[0]
                self.apps_name = self.get_value(response, 'app.alauda.io/name')[0]
                return '创建服务成功。 请求url {}'.format(url), code
            else:
                return '创建服务失败。 请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code

    def get_resource_url(self, resource_name, port=80, http='http'):
        response, code, url = self.get(
            self.url_path('/load_balancers/{namespace}', self.env['namespace'], params={'region_name': self.env['region_name'], 'frontend': 'true'}))
        domain, code = self.get_value(response, 'domain', resource_name)
        service_url = http + '://' + domain + ':' + port.__str__()
        logger.debug('服务地址{}'.format(service_url))
        self.service_url = service_url
        return service_url

    def get_expected_value(self, key, expected_value, substring='', resource_type='service'):
        if resource_type == 'service':
            return Common.get_expected_value(self, self.service_get_url, key, expected_value, substring)
        elif resource_type == 'apps':
            return Common.get_expected_value(self, self.apps_get_url, key, expected_value, substring)

    def get_expect_string(self, cmd, expect, index=0, version='v1'):
        return exec_container.get_expect_string(self.service_uuid, cmd, expect, index, version)

    def update_load_balance(self):
        response, code, url = self.get(
            self.url_path('/load_balancers/{namespace}', self.env['namespace'], params={'region_name': self.env['region_name'], 'frontend': 'true'}))
        load_balance_name, code = self.get_value(response, 'name')
        load_balance_id, code = self.get_value(response, 'load_balancer_id')
        load_balance_type, code = self.get_value(response, 'type')
        self.set_value('module_load_balance.json', 'load_balancer_id', load_balance_id)
        self.set_value('module_load_balance.json', 'name', load_balance_name)
        self.set_value('module_load_balance.json', 'type', load_balance_type)

    def get_event_params(self, size='20', **kwargs):
        if kwargs:
            pass
        params = {'start_time': '{}'.format(Common.get_start_time()), 'end_time': '{}'.format(Common.get_end_time()), 'size': size}
        return params

    def get_event(self, operation, resource_type):
        time.sleep(5)
        if resource_type == 'service':
            response, code, url = self.get(self.service_event_url)
        elif resource_type == 'application':
            response, code, url = self.get(self.apps_event_url)
        if self.get_value(response, 'operation', operation)[0] == operation and self.get_value(response, 'resource_type', resource_type)[0] == resource_type:
            return "测试通过", True
        else:
            return response, False

    @staticmethod
    def get_log_params(**kwargs):
        if kwargs:
            pass
        end_time = time.time()
        start_time = end_time - 1800
        params = {'start_time': '{}'.format(start_time), 'end_time': '{}'.format(end_time)}
        return params

    def get_log(self):
        time.sleep(5)
        response, code, url = self.get(self.get_log_url)
        response = json.loads(response)
        if len(response) > 0 and code == 200:
            return "测试通过", True
        else:
            return "no logs for this service", False

    @staticmethod
    def get_metric_params(agg, metric_name, where, **kwargs):
        if kwargs:
            pass
        params = {'q': '{}:{}{{service_id={}}}'.format(agg, metric_name, where)}
        return params

    def get_metric(self, dps):
        time.sleep(5)
        self.metric_params = self.get_metric_params('avg', 'service.mem.utilization', self.service_uuid)
        response, code, url = self.get(self.get_metric_url)
        response = json.loads(response)
        if isinstance(response, list):
            for i in range(len(response)):
                data = response[i][dps]
                if data:
                    metrics_values = list(data.values())
                    for index in range(len(metrics_values)):
                        if len(metrics_values) > 20 and metrics_values[index]:
                            return "测试通过", True
        else:
            return "no metric for this service", False

    def is_available(self, resource_name):
        response, code, url = self.get(self.get_resource_url(resource_name))
        if code == 200:
            return '服务可以访问， 请求url {}'.format(url), code
        else:
            return '服务可以访问失败， 请求url {}, 返回code {}, 错误原因 {}'.format(url, code, response), code


service = Service()
