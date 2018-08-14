import requests
from requests.exceptions import ConnectionError
from common.base_request import Common
from common.log import logger
from common import settings


class Application(Common):
    def __init__(self):
        super(Application, self).__init__()

    def get_create_app_url(self):
        return "/v2/apps"

    def get_app_list_url(self, app_name):
        return "/v2/apps/?cluster={}&namespace=&name=&app_name={}&label=&repository_uuid=&template_uuid=&page=1&" \
               "page_size=20".format(settings.REGION_NAME, app_name)

    def app_common_url(self, uuid):
        return "/v2/apps/{}".format(uuid)

    def get_app_yam_url(self, uuid):
        return "/v2/apps/{}/yaml".format(uuid)

    def get_start_app_url(self, uuid):
        return "/v2/apps/{}/start".format(uuid)

    def get_stop_app_url(self, uuid):
        return "/v2/apps/{}/stop".format(uuid)

    def get_app_log_url(self, service_id):
        return "/v1/logs/{}/search?&services={}&namespace={}".format(settings.ACCOUNT, service_id, settings.ACCOUNT)

    def get_app_cpu_monitor_url(self, app_id):
        return "/v2/monitor/{}/metrics/query?q=avg:service.cpu.utilization{}by{}".format(settings.ACCOUNT,
                                                                                         "{app_id=" + app_id + "}",
                                                                                         "{service_name}")

    def get_service_loadbalance_url(self, service_id):
        return "/v1/load_balancers/{}?region_name={}&detail=false&service_id={}" \
               "&frontend=true".format(settings.ACCOUNT, settings.REGION_NAME, service_id)

    def get_service_instance_url(self, service_id):
        return "/v2/services/{}/instances".format(service_id)

    def get_app_event_url(self, namespace):
        return "/v1/events/{}?namespace={}&pageno=1&size=100".format(settings.ACCOUNT, namespace)

    def get_app_uuid(self, app_name):
        url = self.get_app_list_url(app_name)
        response = self.send(method='get', path=url)
        assert response.status_code == 200
        contents = response.json()['results']
        if contents:
            return self.get_value(contents, '0.resource.uuid')
        return " "

    def get_service_uuid(self, app_uuid):
        url = self.app_common_url(app_uuid)
        response = self.send(method='get', path=url)
        assert response.status_code == 200
        return self.get_value(response.json(), 'services.0.resource.uuid')

    def get_service_url(self, service_uuid):
        url = self.get_service_loadbalance_url(service_uuid)
        response = self.send(method='get', path=url)
        if response.status_code == 200:
            content = response.json()
            address = self.get_value(content, '0.address')
            protocol = self.get_value(content, '0.listeners.0.protocol')
            port = self.get_value(content, '0.listeners.0.listener_port')
            service_name = self.get_value(content, '0.frontends.0.rules.0.services.0.service_name')
            service_namespace = self.get_value(content, '0.frontends.0.rules.0.services.0.service_namespace')
            domain_info = self.get_value(content, '0.domain_info')
            for con in domain_info:
                if con['type'] == "default-domain":
                    domain = con['domain']
                    disable = con['disabled']
                    if not disable:
                        return "{}://{}.{}.{}:{}".format(protocol, service_name, service_namespace, domain, port)
            return "{}://{}:{}".format(protocol, address, port)

    def create_app(self, file, data):
        logger.info("************************** create app ********************************")
        url = self.get_create_app_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def delete_app(self, app_name):
        logger.info("************************** delete app ********************************")
        uuid = self.get_app_uuid(app_name)
        url = self.app_common_url(uuid)
        return self.send(method='delete', path=url)

    def update_app(self, uuid, file, data):
        logger.info("************************** update app ********************************")
        url = self.app_common_url(uuid)
        data = self.generate_data(file, data)
        return self.send(method='patch', path=url, data=data)

    def start_app(self, uuid):
        logger.info("************************** start app ********************************")
        url = self.get_start_app_url(uuid)
        return self.send(method='put', path=url)

    def stop_app(self, uuid):
        logger.info("************************** stop app ********************************")
        url = self.get_stop_app_url(uuid)
        return self.send(method='put', path=url)

    def get_service_log(self, service_id, expect_value):
        url = self.get_app_log_url(service_id)
        return self.get_logs(url, expect_value)

    def get_app_monitor(self, app_id):
        url = self.get_app_cpu_monitor_url(app_id)
        return self.get_monitor(url)

    def get_service_instance(self, service_id):
        url = self.get_service_instance_url(service_id)
        response = self.send(method='get', path=url)
        if response.status_code == 200:
            content = response.json()
            return self.get_value(content, '0.metadata.name')

    def get_app_status(self, app_id, key, expect_status):
        url = self.app_common_url(app_id)
        return self.get_status(url, key, expect_status)

    def get_app_events(self, app_id, operation, namespace):
        url = self.get_app_event_url(namespace)
        return self.get_events(url, app_id, operation)

    def access_service(self, service_url, query):
        logger.info("************************** access service ********************************")
        try:
            ret = requests.get(service_url)
            logger.info(ret.text)
            if ret.status_code == 200 and query in ret.text:
                return True
        except ConnectionError as e:
            logger.error("access service failed: {}".format(e))
        return False

    def exec_container(self, ip, service_uuid, pod_instance, app_name, command):
        logger.info("************************** exec ********************************")
        ret = self.send_command(ip, service_uuid, pod_instance, app_name, command)
        if ret == 0:
            return True
        return False
