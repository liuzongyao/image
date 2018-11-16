import sys
from common.base_request import Common
from common.log import logger
from subprocess import getstatusoutput


class Cluster(Common):
    def get_node_url(self, region_name, node_name=''):
        return node_name and "v2/regions/{}/{}/nodes/{}".format(self.account, region_name, node_name) or \
               "v2/regions/{}/{}/nodes".format(self.account, region_name)

    def get_feature_url(self, region_name):
        return "v2/regions/{}/{}/features".format(self.account, region_name)

    def generate_install_cmd(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/generate-installation-command".format(self.account)
        data = self.generate_data(file, data)
        return self.send(method="post", path=url, data=data, params={})

    def get_region_info(self, region_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}".format(self.account, region_name)
        return self.send(method="get", path=url, params={})

    def get_region_list(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v1/regions/{}".format(self.account)
        return self.send(method="get", path=url, params={})

    def access_cluster(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}".format(self.account)
        data = self.generate_data(file, data)
        return self.send(method="post", path=url, data=data, params={})

    def check_k8s_version(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/version-check".format(self.account)
        data = self.generate_data(file, data)
        return self.send(method="post", path=url, data=data, params={})

    def get_node_list(self, region_name):
        url = self.get_node_url(region_name)
        return self.send(method="get", path=url, params={})

    def add_nodes(self, region_name, file, data):
        url = self.get_node_url(region_name)
        data = self.generate_data(file, data)
        return self.send(method="post", path=url, data=data, params={})

    def update_node_labels(self, region_name, node_name, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        data = {"labels": data}
        url = "v2/regions/{}/{}/nodes/{}/labels".format(self.account, region_name, node_name)
        return self.send(method="put", path=url, json=data, params={})

    def get_cluster_labels(self, region_name):
        url = "v2/regions/{}/{}/labels".format(self.account, region_name)
        return self.send(method="get", path=url, params={})

    def cordon_node(self, region_name, node_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/nodes/{}/cordon".format(self.account, region_name, node_name)
        return self.send(method="put", path=url, params={})

    def uncordon_node(self, region_name, node_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/nodes/{}/uncordon".format(self.account, region_name, node_name)
        return self.send(method="put", path=url, params={})

    def delete_cluster(self, region_name):
        url = "v2/regions/{}/{}".format(self.account, region_name)
        return self.send(method="delete", path=url, params={})

    def excute_script(self, cmd, ip):
        remote_cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} '{}'".format("07Apples", "root", ip, cmd)
        logger.info("deploy cluster cmd is :{}".format(remote_cmd))
        result = getstatusoutput(remote_cmd)
        logger.info("deploy result is {}".format(result))
        return result

    def cleanup_cluster(self, ips):
        for ip in ips:
            cmd = "curl http://get.alauda.cn/deploy/ake/cleanup | sudo sh"
            self.excute_script(cmd, ip)

    def check_schedulable(self, region_name, index):
        ret_node = self.get_node_list(region_name)
        assert ret_node.status_code == 200, "获取node列表失败:{}".format(ret_node.text)
        node_info = self.get_value(ret_node.json(), "items.{}".format(index))
        return self.get_value(node_info, "spec.unschedulable")

    def install_nevermore(self, region_name, file):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/features/log".format(self.account, region_name)
        data = self.generate_data(file)
        return self.send(method="post", path=url, data=data, params={})

    def uninstall_nevermore(self, region_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/features/log".format(self.account, region_name)
        return self.send(method="delete", path=url, params={})

    def install_registry(self, region_name, file):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/features/registry".format(self.account, region_name)
        data = self.generate_data(file)
        return self.send(method="post", path=url, data=data, params={})

    def uninstall_registry(self, region_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/features/registry".format(self.account, region_name)
        return self.send(method="delete", path=url, params={})

    def get_feature_status(self, region_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_feature_url(region_name)
        return self.send(method="get", path=url, params={})

    def check_feature_status(self, region_name):
        result = {"success": True}
        log_status = self.get_status(self.get_feature_url(region_name), "log.application_info.status", "Running",
                                     params={})
        result = self.update_result(result, log_status, '日志状态不是Running')
        registry_status = self.get_status(self.get_feature_url(region_name), "registry.application_info.status",
                                          "Running", params={})
        result = self.update_result(result, registry_status, 'registry状态不是Running')
        return result
