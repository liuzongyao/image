# coding=utf-8
from common.base_request import Common
from common.log import logger
import sys


class Dashboard(Common):
    def get_dashboard_url(self, dashboard_id=''):
        return "v2/monitor/{}/dashboards/{}".format(self.account, dashboard_id)

    def get_chart_url(self, dashboard_id, chart_id=''):
        return "{}/charts/{}".format(self.get_dashboard_url(dashboard_id), chart_id)

    def get_chart_monitor_url(self):
        return "v2/monitor/{}/metrics/query".format(self.account)

    def create_dashboard(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_dashboard_url()
        data = self.generate_data(file, data)
        return self.send("POST", path, data=data)

    def get_dashboard(self, dashboard_id):
        path = self.get_dashboard_url(dashboard_id)
        return self.send("GET", path)

    def update_dashboard(self, dashboard_id, file, data):
        path = self.get_dashboard_url(dashboard_id)
        data = self.generate_data(file, data)
        return self.send("PUT", path, data=data)

    def delete_dashboard(self, dashboard_id):
        path = self.get_dashboard_url(dashboard_id)
        return self.send("DELETE", path)

    def get_dashboard_list(self):
        params = {"page": 1, "page_size": 100}
        path = self.get_dashboard_url()
        return self.send("GET", path, params=params)

    def create_chart(self, dashboard_id, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_chart_url(dashboard_id)
        data = self.generate_data(file, data)
        return self.send("POST", path, data=data)

    def update_chart(self, dashboard_id, chart_id, file, data):
        path = self.get_chart_url(dashboard_id, chart_id)
        data = self.generate_data(file, data)
        return self.send("PUT", path, data=data)

    def delete_chart(self, dashboard_id, chart_id):
        path = self.get_chart_url(dashboard_id, chart_id)
        return self.send("DELETE", path)

    def get_chart(self, params):
        time = self.generate_time_params()
        params.update(time)
        path = self.get_chart_monitor_url()
        return self.send("GET", path, params=params)

    def get_dashboard_id(self, dashboard_name):
        response = self.get_dashboard_list()
        if response.status_code == 200:
            contents = response.json().get("data")
            return self.get_uuid_accord_name(contents, {"dashboard_name": dashboard_name}, "uuid")
        return ''
