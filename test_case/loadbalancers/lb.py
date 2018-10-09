import requests
import time

from common import settings
from common.base_request import Common
from common.log import logger


class LoadBalancer(Common):
    def __init__(self):
        super(LoadBalancer, self).__init__()

    def get_lb_url(self, lb_id=None):
        return lb_id and "v1/load_balancers/{}/{}".format(self.account, lb_id) or "v1/load_balancers/{}/".format(
            self.account)

    def get_lb_frontends_url(self, lb_id=None):
        return "v1/load_balancers/{}/{}/frontends?page=1&page_size=20&search=".format(self.account, lb_id)

    def get_list_lb_url(self):
        return "v1/load_balancers/{}?region_name={}&project_name={}&service_id=&frontend=false".format(settings.ACCOUNT,
                                                                                                       self.region_name,
                                                                                                       self.project_name)

    def get_lb_event_url(self):
        return "/v1/events/{}?pageno=1&size=100".format(settings.ACCOUNT)

    def get_lb_name(self):
        url = self.get_lb_url()
        params = {"region_name": self.region_name}
        response = self.send(method="get", path=url, params=params)
        if response.status_code == 200:
            contents = response.json()
            for content in contents:
                if content['type'] == "haproxy":
                    lb_name = content['name']
                    return lb_name
            return None
        return "lb_name not found"

    def create_lb(self, file, data):
        url = self.get_lb_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=url, data=data)

    def get_list_lb(self):
        url = self.get_list_lb_url()
        return self.send(method='get', path=url)

    def update_lb_dns(self, lb_id, file, data):
        logger.info("************************** update lb_dns ********************************")
        url = self.get_lb_url(lb_id)
        data = self.generate_data(file, data)
        return self.send(method="PUT", path=url, data=data)

    def get_lb_detail(self, lb_id):
        logger.info("************************** get lb_dns detail ********************************")
        url = self.get_lb_url(lb_id)
        return self.send(method="get", path=url)

    def delete_lb(self, lb_name):
        lb_id = self.get_lb_id(lb_name)
        url = self.get_lb_url(lb_id)
        return self.send(method='delete', path=url)

    def get_lb_id(self, lb_name):
        url = self.get_list_lb_url()
        response = self.send(method="GET", path=url)
        assert response.status_code == 200, "get lb_id failed"
        return self.get_uuid_accord_name(response.json(), {"name": lb_name}, "load_balancer_id")

    def get_lb_events(self, lb_id, operation):
        url = self.get_lb_event_url()
        return self.get_events(url, lb_id, operation)

    def get_app_lbdetail(self, app_id):
        logger.info("************************** get app_lb_detail ********************************")
        url = self.get_lb_url()
        params = {"region_name": self.region_name, "service_id": app_id, "frontend": True}
        params.update({"project_name": self.project_name})
        return self.send(method='get', path=url, params=params)

    def access_service(self, service_url, query):
        logger.info("************************** access service **********************************")
        try:
            cnt = 0
            while cnt < 5 and True:
                cnt = cnt + 1
                time.sleep(1)
                ret = requests.get(service_url)
                logger.info(ret.text)
                if ret.status_code == 200 and query in ret.text:
                    return True
        except ConnectionError as e:
            logger.info("access service failed:{}".format(e))
        return False
