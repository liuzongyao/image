import sys

from common.base_request import Common
from common.log import logger


class Networkpolicy(Common):
    def get_list_networkpolicy_url(self):
        return 'v2/kubernetes/clusters/{}/networkpolicies'.format(self.region_name)

    def get_common_networkpolicy_url(self, k8s_namespace, name):
        return 'v2/kubernetes/clusters/{}/networkpolicies/{}/{}'.format(self.region_name, k8s_namespace, name)

    def list_networkpolicy(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_list_networkpolicy_url()
        return self.send(method='get', path=url)

    def create_networkpolicy(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_list_networkpolicy_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_networkpolicy(self, k8s_namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_networkpolicy_url(k8s_namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def delete_networkpolicy(self, k8s_namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_networkpolicy_url(k8s_namespace, name)
        return self.send(method='delete', path=url)

    def get_networkpolicy_detail(self, k8s_namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_networkpolicy_url(k8s_namespace, name)
        return self.send(method='get', path=url)

    def get_networkpolicy_id(self, k8s_namespace, name):
        response = self.get_networkpolicy_detail(k8s_namespace, name)
        return self.get_value(response.json(), 'kubernetes.metadata.uid')
