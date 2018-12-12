import sys

from common.base_request import Common
from common.log import logger


class Pvc(Common):
    def get_common_pvc_url(self, ns_name='', pvc_name=''):
        return 'v2/kubernetes/clusters/{}/persistentvolumeclaims/{}/{}'.format(self.region_id, ns_name, pvc_name)

    def list_pvc(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pvc_url()
        return self.send(method='get', path=url)

    def create_pvc(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pvc_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def get_pvc_detail(self, ns_name, pvc_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pvc_url(ns_name, pvc_name)
        return self.send(method='get', path=url)

    def delete_pvc(self, ns_name, pvc_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pvc_url(ns_name, pvc_name)
        return self.send(method='delete', path=url)

    def update_pvc(self, ns_name, pvc_name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pvc_url(ns_name, pvc_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)
