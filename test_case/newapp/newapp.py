import sys
from time import sleep

from common.base_request import Common
from common.log import logger


class Newapplication(Common):
    def get_newapp_url(self):
        return "v2/kubernetes/clusters/{}/applications".format(self.region_name)

    def get_newapp_common_url(self, namespace, name=''):
        return "v2/kubernetes/clusters/{}/applications/{}/{}".format(self.region_name, namespace, name)

    def get_newapp_yaml_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/yaml".format(self.region_name, namespace, name)

    def get_start_newapp_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/start".format(self.region_name, namespace, name)

    def get_stop_newapp_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/stop".format(self.region_name, namespace, name)

    def get_add_newapp_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/add".format(self.region_name, namespace, name)

    def get_remove_newapp_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/remove".format(self.region_name, namespace, name)

    def get_all_newapp(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_url()
        return self.send(method='get', path=url)

    def create_newapp(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def get_newapp_in_namespace(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_common_url(namespace)
        return self.send(method='get', path=url)

    def get_newapp_detail(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_common_url(namespace, name)
        return self.send(method='get', path=url)

    def update_newapp(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_common_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def delete_newapp(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_common_url(namespace, name)
        return self.send(method='delete', path=url)

    def get_newapp_yaml(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_yaml_url(namespace, name)
        return self.send(method='get', path=url)

    def start_newapp(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_start_newapp_url(namespace, name)
        return self.send(method='put', path=url)

    def stop_newapp(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_stop_newapp_url(namespace, name)
        return self.send(method='put', path=url)

    def add_resource_newapp(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_add_newapp_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def remove_resource_newapp(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_remove_newapp_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def get_newapp_status(self, namespace, name, expect_value):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            url = self.get_newapp_common_url(namespace, name)
            response = self.send(method="GET", path=url)
            assert response.status_code == 200, "get status failed"
            for resource in response.json():
                if self.get_value(resource, 'kubernetes.kind') == 'Application':
                    value = self.get_value(resource, 'kubernetes.spec.assemblyPhase')
                    logger.info("应用状态：{}".format(value))
                    if value == expect_value:
                        flag = True
                        break
            sleep(5)
        return flag

    def get_deployment_status(self, namespace, name, expect_value):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            url = self.get_newapp_common_url(namespace, name)
            response = self.send(method="GET", path=url)
            assert response.status_code == 200, "get status failed"
            for resource in response.json():
                if self.get_value(resource, 'kubernetes.kind') == 'Deployment':
                    logger.info("组件状态：{}".format(self.get_value(resource, 'kubernetes.status')))
                    if expect_value == "start":
                        if 'readyReplicas' in self.get_value(resource, 'kubernetes.status'):
                            flag = True
                            break
                    else:
                        if 'readyReplicas' not in self.get_value(resource, 'kubernetes.status'):
                            flag = True
                            break
            sleep(5)
        return flag
