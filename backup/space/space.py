from time import sleep

from common.base_request import Common
from common.log import logger


class Space(Common):
    def get_space_config_url(self, space_name=None):
        return space_name and "v1/spaces/{}/space/{}".format(self.account, space_name) or \
               "v1/spaces/{}/".format(self.account)

    def create_space(self, file, data):
        path = self.get_space_config_url()
        data = self.generate_data(file, data)
        return self.send(method='POST', path=path, data=data)

    def get_space(self, space_name):
        path = self.get_space_config_url(space_name)
        return self.send(method='GET', path=path)

    def get_space_resources(self, space_name):
        path = 'v1/spaces/{}/space/{}/resources'.format(self.account, space_name)
        count = 0
        while count < 40:
            count += 1
            response = self.send(method='get', path=path)
            if response.status_code == 200 and not response.json() or response.status_code == 404:
                logger.info("resource of space : {} {}".format(response.status_code, response.text))
                return True
            sleep(3)
        return False

    def delete_space(self, space_name):
        path = self.get_space_config_url(space_name)
        return self.send(method='DELETE', path=path)
