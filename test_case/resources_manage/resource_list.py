import sys
from common.base_request import Common
from common.log import logger


class ResourceList(Common):
    def get_resources_list(self):
        return 'v2/misc/clusters/{}/resourcetypes'.format(self.region_name)

    def list_resources(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_resources_list()
        return self.send(method='get', path=url)

    def get_resource_type_list(self, contents):
        resource_list = []
        for content in contents:
            resource_list.append(content['kind'])
            for con in content['resources']:
                resource_list.append(con['kind'])

        resource_list = list(set(resource_list))
        resource_list.sort()
        return resource_list
