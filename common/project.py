from common import settings
from common.base_request import Common
from common.log import logger
from common.parsercase import ParserCase, data_value, add_file


class Project(Common):
    def __init__(self):
        super(Project, self).__init__()

    def get_project(self):
        path = '/v1/projects/{}/{}'.format(settings.ACCOUNT, settings.PROJECT_NAME)
        response = self.send(method='get', path=path)
        if response.status_code == 200:
            logger.info('The {} is exist, no need to create'.format(settings.PROJECT_NAME))
            return True
        if response.status_code == 404:
            return False

    def create_project(self):
        ret = self.get_project()
        if ret is False:
            data = ParserCase('project.yml', variables={"project": settings.PROJECT_NAME}).parser_case()
            response = self.send(method='POST', path='/v1/projects/{}/'.format(self.account), **data)
            assert response.status_code == 201, response.text
            string = 'CREATE_PROJECT = True\n'
            add_file(string)

    def delete_role(self, role_name):
        response = Common().send(method='DELETE', path='/v1/roles/{}/{}/'.format(settings.ACCOUNT, role_name))
        try:
            assert response.status_code == 204
            logger.info('Delete role {} success'.format(role_name))
        except AssertionError:
            logger.error('Delete role: {} failed, Response code: {}, message: {}'.format(
                role_name, response.status_code, response.text))

    def delete_project(self):
        if 'CREATE_PROJECT' in data_value():
            for suffix in ('-project_admin', '-project_auditor'):
                role_name = settings.PROJECT_NAME + suffix
                # delete project role first
                self.delete_role(role_name)
            response = Common().send(method='Delete', path='/v1/projects/{}/{}'.format(settings.ACCOUNT,
                                                                                       settings.PROJECT_NAME))
            try:
                assert response.status_code == 204
                logger.info('Delete project {} success'.format(settings.PROJECT_NAME))
                return True
            except AssertionError:
                logger.error('Delete project {} failed, Response code: {}, message: {}'.format(
                    settings.PROJECT_NAME, response.status_code, response.text))
                return False
        else:
            logger.info("The project no need to delete")
            return True
