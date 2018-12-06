import sys

from time import sleep
from common.base_request import Common
from common.log import logger


class Middleware(Common):

    # 使用中间件模板创建应用
    def get_application_url(self, uuid=''):
        return "v2/catalog/applications/{}".format(uuid)

    def get_public_templates(self):
        return "v2/catalog/template_public_repositories?name=alauda_public_rp&template_type=2"

    # 根据模板id，获取创建应用时所用的version的id
    def get_template_info_url(self, uuid):
        return "v2/catalog/templates/{}".format(uuid)

    def get_pods_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/pods".format(self.region_name, namespace, name)

    def get_status_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/status".format(self.region_name, namespace, name)

    def get_application_list_url(self, namespace):
        return "v2/kubernetes/clusters/{}/applications/{}/".format(self.region_name, namespace)

    '''
    使用模板创建应用，如中间件等
    '''

    def get_template_list(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_public_templates()
        return self.send(method='get', path=url)

    def create_application(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_application_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def get_pods(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_pods_url(namespace, name)
        return self.send('get', path=url)

    def update_application(self, uuid, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_application_url(uuid)
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def get_application_list(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_application_list_url(namespace)
        return self.send(method='post', path=url)

    def get_template_info(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_template_info_url(uuid)
        return self.send(method='get', path=url)

    def get_template_id(self, template_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        template_list = self.get_template_list().json()[0]["templates"]
        template_id = self.get_uuid_accord_name(template_list, {"name": template_name}, "uuid")
        return template_id

    '''
    根据模板id获取version id
    '''

    def get_version_id(self, template_id):
        template_info = self.get_template_info(template_id)
        versions = template_info.json()["versions"]
        version_id = ""
        for version in versions:
            if version["is_active"]:
                version_id = version["uuid"]
                break
        logger.info("version id : {}".format(version_id))
        return version_id

    '''
    创建应用后，等待状态为running
    '''

    def get_application_status(self, namespace, name, expectstatus):

        cnt = 0
        flag = False
        while cnt < 80 and not flag:
            cnt += 1
            url = self.get_status_url(namespace, name)
            responce = self.send(method='get', path=url)
            status = self.get_value(responce.json(), 'app_status')
            logger.info("应用状态为：{}".format(status))
            if status == expectstatus:
                flag = True
                break
            sleep(5)
        return flag
