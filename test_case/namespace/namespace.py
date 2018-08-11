from common.base_request import Common


class Namespace(Common):
    def get_namespace_url(self, namespace=None):
        return namespace and "v2/kubernetes/clusters/{}/namespaces/{}".format(self.region_id, namespace) or \
               "v2/kubernetes/clusters/{}/namespaces".format(self.region_id)

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
