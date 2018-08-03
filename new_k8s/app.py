import json
import urllib3
from urllib3.exceptions import NewConnectionError, MaxRetryError
from time import time, sleep
from common.base_request import Common
from common.log import logger
from common import settings
from common.parsercase import ParserCase
from common.get_common_data import EXEC


class Application(Common):
    def __init__(self):
        super(Application, self).__init__()

    def get_create_app_url(self):
        return "/v2/apps?project_name={}".format(settings.PROJECT_NAME)

    def get_app_list_url(self):
        return "/v2/apps/?cluster={}&namespace=&name=&app_name=&label=&repository_uuid=&template_uuid=&page=1&" \
               "page_size=20&project_name={}".format(settings.REGION_NAME, settings.PROJECT_NAME)

    def app_common_url(self, uuid):
        return "/v2/apps/{}".format(uuid)

    def get_app_yam_url(self, uuid):
        return "/v2/apps/{}/yaml".format(uuid)

    def get_start_app_url(self, uuid):
        return "/v2/apps/{}/start".format(uuid)

    def get_stop_app_url(self, uuid):
        return "/v2/apps/{}/stop".format(uuid)

    def get_app_log_url(self, service_id, start_time, end_time):
        return "/v1/logs/{}/search?start_time={}&end_time={}&pageno=1&size=500" \
               "&paths=stdout&read_log_source_name=default&services={}" \
               "&allow_service_id=true&mode=polling&namespace={}&project_name={}".format(settings.ACCOUNT,
                                                                                         start_time,
                                                                                         end_time,
                                                                                         service_id,
                                                                                         settings.ACCOUNT,
                                                                                         settings.PROJECT_NAME)

    def get_app_cpu_monitor_url(self, app_id, start_time, end_time):
        return "/v2/monitor/" + settings.ACCOUNT + "/metrics/query?q=avg:service.cpu.utilization{" \
               "app_id=" + app_id + "}by{service_name}&start=" + start_time + "&end=" + end_time + "&" \
               "project_name=" + settings.PROJECT_NAME

    def get_service_loadbalance_url(self, service_id):
        return "/v1/load_balancers/{}?region_name={}&detail=false&service_id={}" \
               "&frontend=true&project_name={}".format(settings.ACCOUNT, settings.REGION_NAME, service_id,
                                                       settings.PROJECT_NAME)

    def get_service_instance_url(self, service_id):
        return "/v2/services/{}/instances?project_name={}".format(service_id, settings.PROJECT_NAME)

    def get_app_uuid(self, app_name):
        url = self.get_app_list_url()
        response = self.send(method='get', path=url)
        assert response.status_code == 200
        contents = response.json()['results']
        for content in contents:
            if 'name' in content['resource'] and app_name == content['resource']['name']:
                return content['resource']['uuid']

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
                        return "{}://{}.{}.{}".format(protocol, service_name, service_namespace, domain)
            return "{}://{}:{}".format(protocol, address, port)

    def create_app(self, file, dir_name=None, variables={}):
        logger.info("************************** create app ********************************")
        url = self.get_create_app_url()
        content = ParserCase(file, dir_name=dir_name, variables=variables).parser_case()
        return self.send(method='post', path=url, **content)

    def delete_app(self, app_name):
        logger.info("************************** delete app ********************************")
        uuid = self.get_app_uuid(app_name)
        if uuid:
            url = self.app_common_url(uuid)
            return self.send(method='delete', path=url)

    def update_app(self, uuid, file, dir_name=None):
        logger.info("************************** update app ********************************")
        url = self.app_common_url(uuid)
        content = ParserCase(file, dir_name=dir_name).parser_case()
        return self.send(method='patch', path=url, **content)

    def start_app(self, uuid):
        logger.info("************************** start app ********************************")
        url = self.get_start_app_url(uuid)
        return self.send(method='put', path=url)

    def stop_app(self, uuid):
        logger.info("************************** stop app ********************************")
        url = self.get_stop_app_url(uuid)
        return self.send(method='put', path=url)

    def get_service_log(self, service_id):
        start_time = round(time(), 6)
        end_time = start_time + 3600
        url = self.get_app_log_url(service_id, start_time, end_time)
        count = 0
        while count < 40:
            count += 1
            response = self.send(method='get', path=url)
            code = response.status_code
            if code != 200:
                logger.error("Get service log failed")
                return False
            content = response.json()
            if content['logs']:
                return True
            sleep(3)
        logger.warning("No logs were obtained within two minutes, please manually check")
        return False

    def get_app_monitor(self, app_id):
        start_time = int(time())
        end_time = start_time + 3600
        url = self.get_app_cpu_monitor_url(app_id, str(start_time), str(end_time))
        count = 0
        while count < 40:
            count += 1
            response = self.send(method='get', path=url)
            code = response.status_code
            content = response.json()
            if code != 200:
                logger.error("Get app cpu monitor failed")
                return False
            if content:
                return True
            sleep(3)
        logger.warning("No monitor were obtained within two minutes, please manually check")
        return False

    def get_service_instance(self, service_id):
        url = self.get_service_instance_url(service_id)
        response = self.send(method='get', path=url)
        if response.status_code == 200:
            content = response.json()
            return self.get_value(content, '0.metadata.name')

    def get_app_status(self, app_id, key, expect_status):
        url = self.app_common_url(app_id)
        return self.get_status(url, key, expect_status)

    def access_service(self, service_url, query):
        logger.info("************************** access service ********************************")
        http = urllib3.PoolManager()
        try:
            ret = http.request('GET', service_url)
            logger.info(ret.data)
            if ret.status == 200 and query in ret.data.decode('utf-8'):
                return True
        except (NewConnectionError, MaxRetryError) as e:
            logger.error("access service failed")
        return False

    def exec_container(self, **kwargs):
        """
        .e.g: kwargs =
                {
                    "organization": "testorg001",                                   // required
                    "username": settings.SUB_ACCOUNT,                             // optional
                    "ip": "52.80.87.235",                                           // required
                    "service_uuid": "dc07a499-ecf2-4f73-8f85-188990a8415c",         // required
                    "pod_instance": "jenkins-notdelete1-6d4df7bc77-v266t",          // required
                    "service_name": "jenkins-notdelete1",                            // required, app name
                    "password": settings.PASSWORD,                                // required
                    "command": 'ls'                                               // required
                }
        :param kwargs: dict
        :return:
        """
        logger.info("************************** exec ********************************")
        exec_instance = EXEC(**kwargs)
        ret = exec_instance.send_command()
        if ret == 0:
            return True
        return False