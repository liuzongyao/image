import sys

from common.base_request import Common
from common.log import logger


class Service(Common):
    def get_list_service_url(self, namespace):
        return 'v2/kubernetes/clusters/{}/services/{}/'.format(self.region_name, namespace)

    def get_create_service_url(self):
        return 'v2/kubernetes/clusters/{}/services/'.format(self.region_name)

    def get_common_service_url(self, namespace, name):
        return 'v2/kubernetes/clusters/{}/services/{}/{}'.format(self.region_name, namespace, name)

    def get_search_service_url(self, namespace, name):
        return 'v2/kubernetes/clusters/{}/services/{}/?name={}'.format(self.region_name, namespace, name)

    def list_service(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_list_service_url(namespace)
        return self.send(method='get', path=url)

    def search_service(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_search_service_url(namespace, name)
        return self.send(method='get', path=url)

    def create_service(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_create_service_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_service(self, namespace, name, json):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_service_url(namespace, name)
        return self.send(method='put', path=url, json=json)

    def delete_service(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_service_url(namespace, name)
        return self.send(method='delete', path=url)

    def get_service_detail(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_service_url(namespace, name)
        return self.send(method='get', path=url)
