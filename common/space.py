from time import sleep
from common.base_request import Common
from common.parsercase import ParserCase, data_value, add_file
from common.log import logger


class Space(Common):
    def __init__(self):
        super(Space, self).__init__()

    def create_space(self, file):
        ret = self.get_space()
        if ret is False:
            path = 'v1/spaces/{}/?project_name={}'.format(data_value().get("ACCOUNT"), data_value().get('PROJECT_NAME'))
            data = ParserCase(file, variables={"ACCOUNT": data_value().get("SPACE_NAME")}).parser_case()
            response = self.send(method='post', path=path, **data)
            assert response.status_code == 201, response.text
            uuid = self.get_value(response.json(), 'uuid')
            string = 'CREATE_SPACE = True\n'
            add_file(string)
            return uuid

    def get_space(self):
        path = 'v1/spaces/{}/space/{}?project_name={}'.format(data_value().get("ACCOUNT"),
                                                               data_value().get("SPACE_NAME"),
                                                               data_value().get('PROJECT_NAME'))
        response = self.send(method='get', path=path)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False

    def get_space_resources(self):
        path = 'v1/spaces/{}/space/{}/resources?project_name={}'.format(data_value().get("ACCOUNT"),
                                                                         data_value().get("SPACE_NAME"),
                                                                         data_value().get('PROJECT_NAME'))
        count = 0
        while count < 40:
            count += 1
            response = self.send(method='get', path=path)
            if response.status_code == 200 and not response.json() or response.status_code == 404:
                logger.info("resource of space : {} {}".format(response.status_code, response.text))
                return True
            sleep(3)
        logger.warning("Resources under the space: {} that are not cleared".format(data_value().get("SPACE_NAME")))
        return False

    def delete_space(self):
        ret = self.get_space_resources()
        if ret and 'CREATE_SPACE' in data_value():
            path = 'v1/spaces/{}/space/{}?project_name={}'.format(data_value().get("ACCOUNT"),
                                                                   data_value().get("SPACE_NAME"),
                                                                   data_value().get('PROJECT_NAME'))
            response = self.send(method='delete', path=path)
            if response.status_code == 204 or response.status_code == 404:
                logger.info('Delete resource space response: {} {}'.format(response.status_code, response.text))
                return True
            else:
                logger.error('Delete resource space failed response: {} {}'.format(response.status_code, response.text))
                return False
        return False