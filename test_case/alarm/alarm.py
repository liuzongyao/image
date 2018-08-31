import json
import sys

from common.base_request import Common
from common.log import logger


class Alarm(Common):
    def get_alarm_url(self, uuid=''):
        return "v2/alarms/{}/{}".format(self.account, uuid)

    def get_ack_alarm_url(self, uuid):
        return "v2/alarms/{}/{}/action".format(self.account, uuid)

    def list_alarm(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_alarm_url()
        return self.send(method='get', path=url)

    def create_alarm(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_alarm_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_alarm(self, uuid, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_alarm_url(uuid)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def delete_alarm(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_alarm_url(uuid)
        return self.send(method='delete', path=url)

    def ack_alarm(self, uuid, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_ack_alarm_url(uuid)
        data = json.dumps(data)
        return self.send(method='post', path=url, data=data)

    def get_alarm_detail(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_alarm_url(uuid)
        return self.send(method='get', path=url)

    def get_alarm_uuid(self, name):
        response = self.list_alarm()
        assert response.status_code == 200, '获取指标警报列表失败 {}'.format(response.text)
        return self.get_uuid_accord_name(response.json(), {"name": name}, "uuid")

    def get_log_alarm_url(self, uuid=''):
        return "v2/log_alarms/{}/{}".format(self.account, uuid)

    def create_log_alarm(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_log_alarm_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def update_log_alarm(self, uuid, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_log_alarm_url(uuid)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def delete_log_alarm(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_log_alarm_url(uuid)
        return self.send(method='delete', path=url)

    def list_log_alarm(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_log_alarm_url()
        return self.send(method='get', path=url)

    def get_log_alarm_detail(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_log_alarm_url(uuid)
        return self.send(method='get', path=url)

    def get_log_alarm_uuid(self, name):
        response = self.list_log_alarm()
        assert response.status_code == 200, '获取日志警报列表失败 {}'.format(response.text)
        return self.get_uuid_accord_name(response.json().get('results'), {"name": name}, "uuid")
