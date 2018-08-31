import sys

from common.base_request import Common
from common.log import logger


class Log(Common):
    def get_logsource_url(self):
        return "v1/integrations/{}/?families=LogSource&namespace={}".format(self.account, self.account)

    def get_type_url(self):
        return "v2/logs/{}/types?read_log_source_uuid=default&namespace={}".format(self.account, self.account)

    def get_aggregations_url(self):
        return "v2/logs/{}/aggregations?read_log_source_uuid=default&paths=&namespace={}".format(self.account,
                                                                                                 self.account)

    def get_search_url(self, service_id):
        return "v2/logs/{}/search?services={}&read_log_source_uuid=default&paths=&namespace={}".format(self.account,
                                                                                                       service_id,
                                                                                                       self.account)

    def get_saved_search_url(self, display_name=''):
        return "v2/logs/{}/saved_search?all=true&display_name={}&namespace={}".format(self.account, display_name,
                                                                                      self.account)

    def get_common_saved_search_url(self, uuid=''):
        return "v2/logs/{}/saved_search/{}?&namespace={}".format(self.account, uuid, self.account)

    def list_saved_search(self, display_name=''):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_saved_search_url(display_name)
        return self.send(method='get', path=url)

    def create_saved_search(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_saved_search_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def delete_saved_search(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_saved_search_url(uuid)
        return self.send(method='delete', path=url)

    def get_saved_search_detail(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_saved_search_url(uuid)
        return self.send(method='get', path=url)

    def get_type(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_type_url()
        return self.send(method='get', path=url)

    def get_logsource(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_logsource_url()
        params = {"project_name": self.project_name, "page_size": 200, "page": 1}
        return self.send(method='get', path=url, params=params)

    def get_aggregations(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_aggregations_url()
        params = Common.generate_time_params()
        return self.send(method='get', path=url, params=params)

    def search_log(self, service_id):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_search_url(service_id)
        params = Common.generate_time_params()
        params.update({"project_name": self.project_name, "size": 50, "pageno": 1})
        return self.send(method='get', path=url, params=params)

    def get_saved_search_uuid(self, name):
        response = self.list_saved_search()
        assert response.status_code == 200, '获取保存日志条件列表失败 {}'.format(response.text)
        return self.get_uuid_accord_name(response.json(), {"name": name}, "uuid")
