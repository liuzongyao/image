# coding=utf-8
import json
import os

from common import settings
from common.api_requests import AlaudaRequest
from common.utils import retry
from test_case.namespace.namespace import Namespace
from test_case.space.space import Space
from test_case.project.project import Project
from common.loadfile import FileUtils


class SetUp(AlaudaRequest):
    """
    测试前先获取global信息已经新建一些测试的必须资源
    """

    def __init__(self):
        super(SetUp, self).__init__()
        self.common = {
            "$NAMESPACE": settings.ACCOUNT,
            "$SVN_PASSWORD": settings.SVN_PASSWORD,
            "$SVN_USERNAME": settings.SVN_USERNAME,
            "$SVN_REPO": settings.SVN_REPO,
            "$REGISTRY": settings.REGISTRY_NAME,
            "$REPO_NAME": settings.REPO_NAME,
            "$SPACE_NAME": settings.SPACE_NAME,
            "$REGION_NAME": settings.REGION_NAME,
            "$K8S_NAMESPACE": settings.K8S_NAMESPACE,
            "$IMAGE": settings.IMAGE,
            "$PROJECT_NAME": settings.PROJECT_NAME,
            "$JENKINS_ENDPOINT": settings.JENKINS_ENDPOINT,
            "$JENKINS_USER": settings.JENKINS_USER,
            "$JENKINS_TOKEN": settings.JENKINS_TOKEN
        }
        self.get_region_data()
        self.get_build_endpontid()
        self.get_load_balance_info()
        self.get_slave_ips()
        self.get_registry_uuid()
        self.input_file(self.common)
        self.namespace_client = Namespace()
        self.space_client = Space()
        self.project_client = Project()
        self.prepare()
        self.input_file(self.common)

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        response = self.send(method="GET", path="/v1/regions/{}/{}/".format(self.account, self.region_name))
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        self.region_id = self.region_data["id"]
        self.region_volume = ",".join(self.region_data.get("features").get("volume").get("features"))
        self.common.update({"$REGION_ID": self.region_id})
        self.common.update({"$REGION_VOLUME": self.region_volume})

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
                self.common.update({"$BUILD_ENDPOINT_ID": self.build_endpointid})
                break

    @retry()
    def get_load_balance_info(self):
        """
        :return:获取haproxy的ip和name
        """
        response = self.send(method='GET',
                             path='/v1/load_balancers/{}?region_name={}'.format(self.account, self.region_name))
        assert response.status_code == 200, response.text
        contents = response.json()
        assert len(contents) > 0, "get_load_balance_info is 空列表"
        for content in contents:
            if content['type'] == "nginx" or content["type"] == "haproxy":
                self.common.update({"$HAPROXY_NAME": content['name'], "$HAPROXY_IP": content['address']})
                break

    @retry()
    def get_registry_uuid(self):
        response = self.send(method='get', path="/v1/registries/{}/".format(self.account))
        assert response.status_code == 200, response.text
        public = []
        private = []
        contents = response.json()
        for index, content in enumerate(contents):
            public_dict = {}
            private_dict = {}

            if content['is_public']:
                public_dict['name'] = content['name']
                public_dict['uuid'] = content['uuid']
                public_dict['endpoint'] = content['endpoint']
                public.append(public_dict)
            elif content['name'] == settings.REGISTRY_NAME:
                private_dict['name'] = content['name']
                private_dict['uuid'] = content['uuid']
                private_dict['endpoint'] = content['endpoint']
                private.append(private_dict)
        self.common.update({"PUBLIC_REGISTRY": public, "PRIVATE_REGISTRY": private})

    @retry()
    def get_slave_ips(self):
        response = self.send(method='GET',
                             path='/v1/regions/{}/{}/nodes/'.format(self.account, self.region_name))
        assert response.status_code == 200, response.text
        contents = response.json()
        slaveips = []
        for content in contents:
            if content.get("type") == "SYSLAVE" or content.get("type") == "SLAVE" and content.get("attr").get(
                    "schedulable") is True:
                slaveips.append(content.get("private_ip"))
        self.common.update({"$SLAVEIPS": ','.join(slaveips)})

    def input_file(self, content):
        """
        将global数据写入临时文件
        :param content: str
        :return:
        """
        file_path = self.global_info_path.split('/')[-2]
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(self.global_info_path, 'w+') as write:
            write.write(json.dumps(content, indent=2))

    def prepare(self):
        # create project
        response = self.project_client.get_project()
        if response.status_code != 200:
            response = self.project_client.create_project('./test_data/project/project.yml',
                                                          {"$project": settings.PROJECT_NAME})
            assert response.status_code == 201, "prepare data failed: create project failed {}".format(response.text)
            self.common.update({"CREATE_PROJECT": True, "$PROJECT_UUID": response.json()['uuid']})
        else:
            self.common.update({"$PROJECT_UUID": response.json()['uuid']})

        # create k8s namespace
        response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)
        if response.status_code != 200:
            response = self.namespace_client.create_namespaces("./test_data/namespace/namespace.yml",
                                                               {"$K8S_NAMESPACE": settings.K8S_NAMESPACE})
            assert response.status_code == 201, "prepare data failed: create namespace failed {}".format(response.text)
            self.common.update({"CREATE_NAMESPACE": True})
        response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)

        assert response.status_code == 200, "prepare data failed: get namespace detail failed {}".format(response.text)
        namespace_uuid = response.json()["kubernetes"]["metadata"]["uid"]
        self.common.update({"$K8S_NS_UUID": namespace_uuid})

        # create space
        response = self.space_client.get_space(settings.SPACE_NAME)
        if response.status_code != 200:
            response = self.space_client.create_space("./test_data/space/space.json",
                                                      {"$SPACE_NAME": settings.SPACE_NAME})
            assert response.status_code == 201, "prepare data failed: create space failed {}".format(response.text)
            self.common.update({"CREATE_SPACE": True, "$SPACE_UUID": response.json()['uuid']})
        else:
            self.common.update({"$SPACE_UUID": response.json()['uuid']})


class TearDown(AlaudaRequest):
    """
    测试结束后删除setup创建的资源
    """

    def __init__(self):
        super(TearDown, self).__init__()
        self.global_info = FileUtils.load_file(self.global_info_path)
        self.namespace_client = Namespace()
        self.space_client = Space()
        self.project_client = Project()
        self.delete()

    def delete(self):
        if "CREATE_NAMESPACE" in self.global_info:
            self.namespace_client.delete_namespaces(settings.K8S_NAMESPACE)

        if "CREATE_SPACE" in self.global_info:
            self.space_client.delete_space(settings.SPACE_NAME)

        if "CREATE_PROJECT" in self.global_info:
            self.project_client.delete_project_role()
            self.project_client.delete_project(settings.PROJECT_NAME)
