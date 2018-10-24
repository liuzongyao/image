import sys

from common.base_request import Common
from common.log import logger


class Namespace(Common):
    def get_namespace_url(self, namespace=None):
        return namespace and "v2/kubernetes/clusters/{}/namespaces/{}".format(self.region_id, namespace) or \
               "v2/kubernetes/clusters/{}/namespaces".format(self.region_id)

    def get_general_namespaces_url(self, namespace=None):
        return namespace and "v2/kubernetes/clusters/{}/general-namespaces/{}".format(self.region_name, namespace) or \
               "v2/kubernetes/clusters/{}/general-namespaces".format(self.region_name)

    def get_resourcequota_url(self, namespace='', quotaname=''):
        return "v2/kubernetes/clusters/{}/resourcequotas/{}/{}".format(self.region_id, namespace, quotaname)

    def get_limitrange_url(self, namespace='', limitname=''):
        return "v2/kubernetes/clusters/{}/limitranges/{}/{}".format(self.region_id, namespace, limitname)

    def get_resource_url(self, namespace):
        return namespace and "v2/kubernetes/clusters/{}/namespaces/{}/resources".format(self.region_id, namespace)

    def create_namespaces(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_namespace_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=path, data=data)

    def create_general_namespaces(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_general_namespaces_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=path, data=data)

    def get_namespaces(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_namespace_url(namespace)
        return self.send(method="GET", path=path)

    def delete_namespaces(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_namespace_url(namespace)
        return self.send(method="DELETE", path=path)

    def delete_general_namespaces(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_general_namespaces_url(namespace)
        return self.send(method="DELETE", path=path)

    def list_namespaces(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_namespace_url()
        return self.send(method="GET", path=path)

    def create_resourcequota(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_resourcequota_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=path, data=data)

    def update_resourcequota(self, namespace, name, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_resourcequota_url(namespace, name)
        data = self.generate_data(file, data)
        return self.send(method="PUT", path=path, data=data)

    def delete_resourcequota(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_resourcequota_url(namespace, name)
        return self.send(method="DELETE", path=path)

    def list_resourcequota(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_resourcequota_url(namespace)
        return self.send(method="GET", path=path)

    def detail_resourcequota(self, namespace, name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_resourcequota_url(namespace, name)
        return self.send(method="GET", path=path)

    def get_resource(self, namespace):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        path = self.get_resource_url(namespace)
        return self.send(method="GET", path=path)
