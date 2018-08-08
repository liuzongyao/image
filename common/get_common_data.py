import os
import re
from pathlib import Path
from common.base_request import Common
from common import settings
from common.log import logger
from common.utils import retry
from common.parsercase import ParserCase


def target_file():
    path_list = [os.path.dirname(os.getcwd()), os.getcwd()]
    for path in path_list:
        target_file = os.path.join(path, 'common', 'settings.py')
        path = Path(target_file)
        if path.exists() and path.is_file():
            return target_file


def input_file(content):
    """
    :param content: str
    :return:
    """
    substring = re.compile(r'[A-Z_]+')
    file = target_file()
    file_path = os.path.join(os.path.dirname(file), '../temp_data')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    new_file = os.path.join(file_path, 'temporary.py')

    text = re.findall(substring, content)

    # De-weighting
    with open(file, 'r') as read:
        with open(new_file, 'w+') as write:
            for line in read:
                line_sub = re.match(substring, line)
                if line_sub:
                    line_start = line_sub.group()
                    if line_start in text:
                        continue
                write.writelines(line)

    with open(new_file, 'a+') as add:
        add.writelines(content)


def delete_role(role_name):
    response = Common().send(method='DELETE', path='/v1/roles/{}/{}/'.format(settings.ACCOUNT, role_name))
    try:
        assert response.status_code == 204
        logger.info('Delete role {} success'.format(role_name))
    except AssertionError:
        logger.error('Delete role: {} failed, Response code: {}, message: {}'.format(
            role_name, response.status_code, response.text))


def delete_project(project_name):
    if project_name.startswith('e2e'):
        for suffix in ('-project_admin', '-project_auditor'):
            role_name = project_name + suffix
            # delete project role first
            delete_role(role_name)
        response = Common().send(method='Delete', path='/v1/projects/{}/{}'.format(settings.ACCOUNT, project_name))
        try:
            assert response.status_code == 204
            logger.info('Delete project {} success'.format(project_name))
            return True
        except AssertionError:
            logger.error('Delete project {} failed, Response code: {}, message: {}'.format(
                project_name, response.status_code, response.text))
            return False
    else:
        logger.info("The name of project is not start with 'e2e', no need to delete")
        return True


class CommonData(Common):
    def __init__(self):
        super(CommonData, self).__init__()
        self.common = ''
        self.project_name = 'e2e-project'
        self.get_region_data()
        self.get_build_endpontid()
        self.get_load_balance_info()
        self.create_project()
        input_file(self.common)

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        response = self.send(method="GET", path="/v1/regions/{}/{}/".format(self.account, self.region_name))
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        self.region_id = self.get_value(self.region_data, "id")
        self.common = self.common + 'REGION_ID = "{}"\n'.format(self.region_id)

    @retry()
    def get_build_endpontid(self):
        """
        :return: 给self.build_endpoint赋值构建的集群ID
        """
        response = self.send(method="GET", path="/v1/private-build-endpoints/{}".format(self.account))
        assert response.status_code == 200, response.text
        for content in response.json():
            if content['region_id'] == self.region_id:
                self.build_endpointid = content['endpoint_id']
                self.common = self.common + 'BUILD_ENDPOINTID = "{}"\n'.format(self.build_endpointid)
                break

    @retry()
    def get_load_balance_info(self):
        response = self.send(method='GET', path='/v1/load_balancers/{}?region_name={}'
                                                '&detail=false&service_id=&frontend=false'.format(
                                                    self.account, self.region_name))
        assert response.status_code == 200, response.text
        contents = response.json()
        for content in contents:
            if "name" in content:
                self.common = self.common + 'HAPROXY_NAME = "{}"\n'.format(content['name'])
                self.common = self.common + 'HAPROXY_IP = "{}"\n'.format(content['address'])
                break

    def create_project(self):
        if not settings.PROJECT_NAME:
            delete_project(self.project_name)
            data = ParserCase('project.yml', variables={"project": self.project_name}).parser_case()
            content = {}
            content['data'] = data
            response = self.send(method='POST', path='/v1/projects/{}/'.format(self.account), **content)
            assert response.status_code == 201, response.text
            self.common = self.common + 'PROJECT_NAME = "{}"\n'.format(self.project_name)
