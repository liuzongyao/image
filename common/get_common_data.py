import json
import os
import re
import time
import pexpect
from pathlib import Path
from common.base_request import Common
from common.utils import retry
from common import settings
from common.log import logger


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
    file_new = file + '-new'
    text = re.findall(substring, content)

    with open(file, 'r') as read:
        with open(file_new, 'w+') as write:
            for line in read:
                line_sub = re.match(substring, line)
                if line_sub:
                    line_start = line_sub.group()
                    if line_start in text:
                        continue
                write.writelines(line)

    os.remove(file)
    os.rename(file_new, file)

    with open(file, 'a+') as add:
        add.writelines(content)


def put_dict_to_file(content):
    """
    :param content: dict
    :return:
    """
    string = ''
    if isinstance(content, dict):
        for key, value in content.items():
            string += '{} = "{}"\n'.format(key, value)
        if string:
            input_file(string)


def clear_file():
    """
    Clean up dynamically generated data in files
    :return:
    """
    file = target_file()
    file_new = file + '-new'

    with open(file, 'r') as read:
        with open(file_new, 'w+') as write:
            while True:
                line = read.readline()
                write.writelines(line)
                if line.startswith('# Dynamic generate'):
                    break
    os.remove(file)
    os.rename(file_new, file)


def get_namespace_resource(region_id, namespace):
    path = "/v2/kubernetes/clusters/{}/namespaces/" \
           "{}/resources?project_name={}".format(region_id, namespace, settings.PROJECT_NAME)
    count = 0
    while count < 40:
        count += 1
        response = Common().send(method='get', path=path)
        if response.status_code == 200 and not response.json():
            return True
        time.sleep(3)

    return False


def delete_namespace(region_id, namespace):
    resource = get_namespace_resource(region_id, namespace)
    if namespace.startswith('e2e') and resource:
        response = Common().send(method='DELETE', path='/v2/kubernetes/clusters/{}/namespaces/{}'.format(
                region_id, namespace))
        try:
            assert response.status_code == 204
            logger.info('Delete namespace {} success'.format(namespace))
        except AssertionError:
            logger.error('Delete namespace: {} failed, Response code: {}, message: {}'.format(
                namespace, response.status_code, response.text))


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
        except AssertionError:
            logger.error('Delete project {} failed, Response code: {}, message: {}'.format(
                project_name, response.status_code, response.text))


class CommonData(Common):
    def __init__(self):
        super(CommonData, self).__init__()
        self.project_name = "e2e-project"
        self.namespace = 'e2e-namespace'
        self.common_data = {}
        self.get_region_data()
        self.get_build_endpontid()
        self.get_load_balance_info()
        self.create_project(self.project_name)
        self.create_namespace(self.namespace)
        put_dict_to_file(self.common_data)

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        response = self.send(method="GET", path="/v1/regions/{}/{}/".format(self.account, self.region_name))
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        self.region_id = self.get_value(self.region_data, "id")
        self.common_data['REGION_ID'] = self.region_id

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
                self.common_data['BUILD_ENDPOINTID'] = self.build_endpointid
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
                self.common_data['HAPROXY_NAME'] = content['name']
                self.common_data['HAPROXY_IP'] = content['address']
                break

    def create_project(self, project):
        try:
            project_name = settings.PROJECT_NAME
            return project_name
        except AttributeError:
            delete_project(project)
            data = { "name": project,
                     "display_name": "",
                     "description": "",
                     "clusters":
                         [{
                             "name": self.region_name,
                             "uuid": self.region_id,
                             "service_type": "kubernetes",
                             "quota":
                                 {
                                     "cpu": 0,
                                     "memory": 0,
                                     "pvc_num": 0,
                                     "pods": 0,
                                     "storage": 0
                                 }
                         }],
                     "template": "empty-template"
                     }
            content = {}
            content['data'] = json.dumps(data)
            response = self.send(method='POST', path='/v1/projects/{}/'.format(self.account), **content)
            assert response.status_code == 201, response.text
            self.common_data['PROJECT_NAME'] = project

    def create_namespace(self, namespace):
        try:
            name_space = settings.NAMESPACE
            return name_space
        except AttributeError:
            delete_namespace(self.region_id, namespace)
            if settings.PROJECT_NAME:
                project = settings.PROJECT_NAME
            else:
                project = self.common_data['PROJECT_NAME']
            data = {
                    "apiVersion": "v1",
                    "kind":"Namespace",
                    "metadata": {
                        "name": namespace
                    }
            }
            content = {}
            content['data'] = data
            response = self.send(method='POST', path='/v2/kubernetes/clusters/{}/namespaces?project_name={}'.format(
                self.region_id, project), **content)
            assert response.status_code == 201, response.text
            self.common_data['NAMESPACE'] = namespace
            self.common_data['NAMESPACE_UUID'] = response.json()[0]['kubernetes']['metadata']['uid']


class EXEC(object):
    def __init__(self, **kwargs):
        self.parameters = kwargs

    def commands(self):
        if 'username' in self.parameters:
            cmd = 'ssh -p 4022 -t {}/{}@{} {}/{}/{}/{} /bin/sh'.format(self.parameters['organization'],
                    self.parameters['username'], self.parameters['ip'], self.parameters['organization'],
                    self.parameters['service_uuid'], self.parameters['pod_instance'], self.parameters['service_name'])
        else:
            cmd = 'ssh -p 4022 -t {}@{} {}/{}/{}/{} /bin/sh'.format(self.parameters['organization'],
                    self.parameters['ip'], self.parameters['organization'], self.parameters['service_uuid'],
                    self.parameters['pod_instance'], self.parameters['service_name'])
        return cmd

    def login_container(self):
        cmd = self.commands()
        logger.debug("exec command: {}".format(cmd))
        child = pexpect.spawn(cmd)
        ret = child.expect([pexpect.EOF, pexpect.TIMEOUT, 'yes/no', 'password:'])
        if ret == 0:
            logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
            return
            # raise EOFError('ssh connect terminated: {}'.format(pexpect.EOF))
        elif ret == 1:
            logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
            return
            # raise TimeoutError('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
        elif ret == 2:
            child.sendline('yes')
            rev = child.expect([pexpect.EOF, pexpect.TIMEOUT, 'password:'])
            if rev == 0:
                logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
                return
                # raise EOFError('ssh connect terminated: {}'.format(pexpect.EOF))
            elif rev == 1:
                logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                return
                # raise TimeoutError('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
            elif rev == 2:
                child.sendline(self.parameters['password'])
                r = child.expect([pexpect.EOF, pexpect.TIMEOUT, '#'])
                if r == 0:
                    logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
                    return
                    # raise EOFError('ssh connect terminated: {}'.format(pexpect.EOF))
                elif r == 1:
                    logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                    return
                    # raise TimeoutError('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                elif r == 2:
                    return child
        elif ret == 3:
            child.sendline(self.parameters['password'])
            r = child.expect([pexpect.EOF, pexpect.TIMEOUT, '#'])
            if r == 0:
                logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
                return
                # raise EOFError('ssh connect terminated: {}'.format(pexpect.EOF))
            elif r == 1:
                logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                return
                # raise TimeoutError('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
            elif r == 2:
                return child

    def send_command(self):
        child = self.login_container()
        if child:
            child.sendline(self.parameters['command'])
            ret = child.expect('#')
            logger.debug(child.before)
            return ret