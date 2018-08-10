from time import sleep
from common.base_request import Common
from common.log import logger


class Namespace(Common):
    def get_namespace_url(self, namespace=None):
        return namespace and "v2/kubernetes/clusters/{}/namespaces/{}".format(self.region_id, namespace) or \
               "v2/kubernetes/clusters/{}/namespaces".format(self.region_id)

    def get_namespace_resource(self, namespace):
        path = "/v2/kubernetes/clusters/{}/namespaces/" \
               "{}/resources".format(self.region_id)
        count = 0
        while count < 40:
            count += 1
            response = self.send(method='get', path=path)
            if response.status_code == 200 and not response.json() or response.status_code == 404:
                return True
            sleep(3)
        logger.warning("Resources under the namespace that are not cleared")
        return False

    def create_namespaces(self, file, data):
        path = self.get_namespace_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=path, data=data)

    def get_namespaces(self, namespace):
        path = self.get_namespace_url(namespace)
        return self.send(method="GET", path=path)

    def delete_namespaces(self, namespace):
        path = self.get_namespace_url(namespace)
        return self.send(method="DELETE", path=path)
