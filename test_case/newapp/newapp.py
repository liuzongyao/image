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

    def get_newapp_status_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/status".format(self.region_name, namespace, name)

    def get_newapp_address_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/address".format(self.region_name, namespace, name)

    def get_newapp_topology_url(self, namespace, name, kind='Deployment'):
        return "v2/kubernetes/clusters/{}/topology/{}?kind={}&name={}".format(self.region_name, namespace, kind, name)

    def get_newapp_pod_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/{}/pods".format(self.region_name, namespace, name)

    def get_scale_newapp_url(self, namespace, name, step):
        return "v2/misc/clusters/{}/scale/deployments/{}/{}?step={}".format(self.region_name, namespace, name,
                                                                            step)

    def get_exec_newapp_url(self, namespace, name, container_name):
        return "v2/misc/clusters/{}/exec/{}/{}/{}".format(self.region_name, namespace, container_name, name)

    def get_newapp_logs_url(self, namespace, name, container_name):
        return "v2/kubernetes/clusters/{}/pods/{}/{}/{}/log".format(self.region_name, namespace, container_name, name)

    def get_newapp_event_url(self, app_id):
        return "v1/events/{}/application/{}?pageno=1&size=20&query_string=".format(self.account, app_id)

    def get_newapp_kevent_url(self, namespace, name):
        return "v2/kevents/?&cluster={}&namespace={}&name={}&page=1&page_size=20&kind=Deployment,Application," \
               "Pod,EndPoint,Service,HorizontalPodAutoscaler,ReplicaSet,DaemonSet,StatefulSet".format(self.region_name,
                                                                                                      namespace, name)

    def search_newapp_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/applications/{}/?search={}".format(self.region_name, namespace, name)

    def delete_deploy_url(self, namespace, name):
        return "v2/kubernetes/clusters/{}/deployments/{}/{}".format(self.region_name, namespace, name)

    def get_all_newapp(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_url()
        return self.send(method='get', path=url)

    def create_newapp(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def create_newapp_by_yaml(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_common_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data, headers={"Content-Type": "application/yaml"})

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

    def get_newapp_status_withoutassert(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_status_url(namespace, name)
        return self.send(method='get', path=url)

    def get_newapp_pods(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_pod_url(namespace, name)
        return self.send(method='get', path=url)

    def get_newapp_topology(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_topology_url(namespace, name)
        return self.send(method='get', path=url)

    def get_newapp_address(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_address_url(namespace, name)
        return self.send(method='get', path=url)

    def get_newapp_event(self, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_event_url(name)
        params = Common.generate_time_params()
        return self.send(method='get', path=url, params=params)

    def get_newapp_kevent(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_kevent_url(namespace, name)
        params = Common.generate_time_params()
        return self.send(method='get', path=url, params=params)

    def scale_up_newapp(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_scale_newapp_url(namespace, name, 1)
        return self.send(method='post', path=url)

    def scale_down_newapp(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_scale_newapp_url(namespace, name, -1)
        return self.send(method='post', path=url)

    def exec_newapp(self, namespace, name, container_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_exec_newapp_url(namespace, name, container_name)
        return self.send(method='post', path=url)

    def get_newapp_log(self, namespace, name, container_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_newapp_logs_url(namespace, name, container_name)
        return self.send(method='get', path=url)

    def search_newapp(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.search_newapp_url(namespace, name)
        return self.send(method='get', path=url)

    def delete_deployment(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.delete_deploy_url(namespace, name)
        return self.send(method='delete', path=url)

    def get_newapp_status(self, namespace, name, expect_value):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            url = self.get_newapp_status_url(namespace, name)
            response = self.send(method="GET", path=url)
            assert response.status_code == 200, "get app status failed"
            value = self.get_value(response.json(), 'app_status')
            logger.info("应用状态：{}".format(value))
            if value == expect_value:
                flag = True
                break
            sleep(5)
        return flag
