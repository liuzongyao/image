import sys

from common.base_request import Common
from common.log import logger


class Alb(Common):
    def get_alb_crd_url(self):
        return "v2/kubernetes/clusters/{}/customresourcedefinitions?name=alaudaloadbalancer2".format(self.region_name)

    def get_create_alb_url(self):
        return "v2/kubernetes/clusters/{}/resources".format(self.region_name)

    def get_list_alb_url(self):
        return "v2/kubernetes/clusters/{}/alaudaloadbalancer2/".format(self.region_name)

    def get_common_alb_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/alaudaloadbalancer2/{}/{}".format(self.region_name, namespace, name)

    def get_frontend_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/frontends/{}/?labelSelector=alb2.alauda.io/name={}".format(self.region_name,
                                                                                                     namespace, name)

    def create_frontend_url(self):
        return "v2/kubernetes/clusters/{}/frontends/".format(self.region_name)

    def common_frontend_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/frontends/{}/{}".format(self.region_name, namespace, name)

    def create_rule_url(self):
        return "v2/kubernetes/clusters/{}/rules/".format(self.region_name)

    def common_rule_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/rules/{}/{}".format(self.region_name, namespace, name)

    def list_rule_url(self, namespace, alb_name, frontend_name):
        return "v2/kubernetes/clusters/{}/rules/{}/?labelSelector=alb2.alauda.io/name={},alb2.alauda.io/frontend={}".format(
            self.region_name, namespace, alb_name, frontend_name)

    def get_alb_crd(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_alb_crd_url()
        return self.send(method='get', path=url, params={})

    def create_alb(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_create_alb_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data, params={})

    def list_alb(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_list_alb_url()
        return self.send(method='get', path=url, params={})

    def update_alb(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_alb_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data, params={})

    def get_alb_detail(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_alb_url(namespace, name)
        return self.send(method='get', path=url, params={})

    def delete_alb(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_alb_url(namespace, name)
        return self.send(method='delete', path=url, params={})

    def create_frontend(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.create_frontend_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data, params={})

    def list_frontend(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_frontend_url(namespace, name)
        return self.send(method='get', path=url, params={})

    def get_detail_frontend(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.common_frontend_url(namespace, name)
        return self.send(method='get', path=url, params={})

    def update_frontend(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.common_frontend_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data, params={})

    def delete_frontend(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.common_frontend_url(namespace, name)
        return self.send(method='delete', path=url, params={})

    def create_rule(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.create_rule_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data, params={})

    def list_rule(self, namespace, alb_name, frontend_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.list_rule_url(namespace, alb_name, frontend_name)
        return self.send(method='get', path=url, params={})

    def detail_rule(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.common_rule_url(namespace, name)
        return self.send(method='get', path=url, params={})

    def update_rule(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.common_rule_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data, params={})

    def delete_rule(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.common_rule_url(namespace, name)
        return self.send(method='delete', path=url, params={})
