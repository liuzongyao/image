import sys

from common.base_request import Common
from common.log import logger


class Configmap(Common):
    def get_common_configmap_url(self, ns_name='', configmap_name=''):
        return 'v2/kubernetes/clusters/{}/configmaps/{}/{}'.format(self.region_id, ns_name, configmap_name)

    def list_configmap(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_configmap_url()
        return self.send(method='get', path=url)

    def create_configmap(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_configmap_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_configmap(self, ns_name, configmap_name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_configmap_url(ns_name, configmap_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def get_configmap_detail(self, ns_name, configmap_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_configmap_url(ns_name, configmap_name)
        return self.send(method='get', path=url)

    def delete_configmap(self, ns_name, configmap_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_configmap_url(ns_name, configmap_name)
        return self.send(method='delete', path=url)
