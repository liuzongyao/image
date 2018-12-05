import sys

from common.base_request import Common
from common.log import logger


class Ingress(Common):
    def get_list_ingress_url(self, k8s_namespace):
        return 'v2/kubernetes/clusters/{}/ingresses/{}/'.format(self.region_name, k8s_namespace)

    def get_create_ingress_url(self):
        return 'v2/kubernetes/clusters/{}/ingresses/'.format(self.region_name)

    def get_common_ingress_url(self, k8s_namespace, name):
        return 'v2/kubernetes/clusters/{}/ingresses/{}/{}'.format(self.region_name, k8s_namespace, name)

    def get_search_ingress_url(self, k8s_namespace, name):
        return 'v2/kubernetes/clusters/{}/ingresses/{}/?name={}'.format(self.region_name, k8s_namespace, name)

    def list_ingress(self, k8s_namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_list_ingress_url(k8s_namespace)
        return self.send(method='get', path=url)

    def search_ingress(self, k8s_namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_search_ingress_url(k8s_namespace, name)
        return self.send(method='get', path=url)

    def create_ingress(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_create_ingress_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_ingress(self, k8s_namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_ingress_url(k8s_namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def delete_ingress(self, k8s_namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_ingress_url(k8s_namespace, name)
        return self.send(method='delete', path=url)

    def get_ingress_detail(self, k8s_namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_ingress_url(k8s_namespace, name)
        return self.send(method='get', path=url)
