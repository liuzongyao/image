import sys

from common.base_request import Common
from common.log import logger


class Domain(Common):
    def get_common_domain_url(self, uuid=None):
        return uuid and 'v2/domains/{}/{}'.format(self.account, uuid) or 'v2/domains/{}'.format(self.account)

    def get_search_domain_url(self, name):
        return 'v2/domains/{}?search={}'.format(self.account, name)

    def list_domain(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_domain_url()
        return self.send(method='get', path=url, params={})

    def search_domain(self, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_search_domain_url(name)
        return self.send(method='get', path=url, params={})

    def create_domain(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_domain_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data, params={})

    def update_domain(self, domain_id, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_domain_url(domain_id)
        return self.send(method='put', path=url, json=data, params={})

    def delete_domain(self, domain_id):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_domain_url(domain_id)
        return self.send(method='delete', path=url, params={})

    def get_domain_id(self, domain_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_domain_url()
        response = self.send(method='get', path=url, params={})
        return self.get_uuid_accord_name(response.json()['results'], {"domain": domain_name}, "domain_id")
