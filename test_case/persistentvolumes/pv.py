import sys

from common.base_request import Common
from common.log import logger


class Pv(Common):
    def get_common_pv_url(self, pv_name=''):
        return 'v2/kubernetes/clusters/{}/persistentvolumes/{}'.format(self.region_id, pv_name)

    def list_pv(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pv_url()
        return self.send(method='get', path=url)

    def create_pv(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pv_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_pv(self, pv_name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pv_url(pv_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def get_pv_detail(self, pv_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pv_url(pv_name)
        return self.send(method='get', path=url)

    def delete_pv(self, pv_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_pv_url(pv_name)
        return self.send(method='delete', path=url)
