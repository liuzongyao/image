from time import sleep
from common.base_request import Common
from common.log import logger
from common.parsercase import data_value, ParserCase


class Namespace(Common):
    def __init__(self):
        super(Namespace, self).__init__()

    def get_namespace_resource(self, namespace):
        path = "/v2/kubernetes/clusters/{}/namespaces/" \
               "{}/resources?project_name={}".format(data_value().get('REGION_ID'), namespace,
                                                     data_value().get('PROJECT_NAME'))
        count = 0
        while count < 40:
            count += 1
            response = self.send(method='get', path=path)
            if response.status_code == 200 and not response.json() or response.status_code == 404:
                return True
            sleep(3)
        logger.warning("Resources under the namespace that are not cleared")
        return False

    def create_namespaces(self, namespace, file):
        path = '/v2/kubernetes/clusters/{}/namespaces?project_name={}'.format(data_value().get('REGION_ID'),
                                                                              data_value().get('PROJECT_NAME'))
        data = ParserCase(file, variables={"NAMESPACE": namespace}).parser_case()
        response = self.send(method="post", path=path, **data)
        assert response.status_code == 201, response.text
        uuid = self.get_value(response.json(), '0.kubernetes.metadata.uid')
        return uuid

    def delete_namespaces(self, namespace):
        ret = self.get_namespace_resource(namespace)
        if ret:
            url = '/v2/kubernetes/clusters/{}/namespaces/{}'.format(data_value().get('REGION_ID'), namespace)
            response = self.send(method='DELETE', path=url)
            if response.status_code == 204 or response.status_code == 500:
                logger.info("delete namespace {} {}".format(response.status_code, response.text))
                return True
            else:
                logger.warning("delete namespace {} {}".format(response.status_code, response.text))
                return False
        return False