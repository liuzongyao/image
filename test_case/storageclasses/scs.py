import sys

from common.base_request import Common
from common.exceptions import ParseResponseError
from common.log import logger


class Scs(Common):
    def get_common_scs_url(self, scs_name=''):
        return 'v2/kubernetes/clusters/{}/storageclasses/{}'.format(self.region_id, scs_name)

    def list_scs(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_scs_url()
        return self.send(method='get', path=url, params={})

    def create_scs(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_scs_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data, params={})

    def update_scs(self, scs_name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_scs_url(scs_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data, params={})

    def get_scs_detail(self, scs_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_scs_url(scs_name)
        return self.send(method='get', path=url, params={})

    def delete_scs(self, scs_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_scs_url(scs_name)
        return self.send(method='delete', path=url, params={})

    def get_default_size(self):
        default_size = 0
        list_result = self.list_scs()
        if list_result.status_code != 200:
            return default_size
        for detail in list_result.json():
            try:
                default = self.get_value(detail,
                                         "kubernetes#metadata#annotations#storageclass.kubernetes.io/is-default-class",
                                         "#")
                if default == "true":
                    default_size += 1
            except (KeyError, ValueError, IndexError, ParseResponseError):
                continue
        return default_size
