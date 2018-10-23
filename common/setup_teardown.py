# coding=utf-8
import json
import os

import requests

from common import settings
from common.api_requests import AlaudaRequest
from common.base_request import Common
from common.utils import retry
from test_case.namespace.namespace import Namespace
from test_case.newapp.newapp import Newapplication
from test_case.space.space import Space
from test_case.project.project import Project
from test_case.notification.notification import Notification
from test_case.image.image import Image
from test_case.application.app import Application
from common.loadfile import FileUtils


class SetUp(AlaudaRequest):
    """
    测试前先获取global信息已经新建一些测试的必须资源
    """

    def __init__(self):
        super(SetUp, self).__init__()
        self.app_name = "alauda-global-app"
        self.common = {
            "$NAMESPACE": settings.ACCOUNT,
            "$PASSWORD": settings.PASSWORD,
            "$SVN_CREDENTIAL": settings.SVN_CREDENTIAL,
            "$SVN_PASSWORD": settings.SVN_PASSWORD,
            "$SVN_USERNAME": settings.SVN_USERNAME,
            "$SVN_REPO": settings.SVN_REPO,
            "$REGISTRY": settings.REGISTRY_NAME,
            "$REPO_NAME": settings.REPO_NAME,
            "$SPACE_NAME": settings.SPACE_NAME,
            "$REGION_NAME": settings.REGION_NAME,
            "$REG_CREDENTIAL": settings.REGISTRY_CREDENTIAL,
            "$K8S_NAMESPACE": settings.K8S_NAMESPACE,
            "$IMAGE": settings.IMAGE,
            "$PROJECT_NAME": settings.PROJECT_NAME,
            "$JENKINS_ENDPOINT": settings.JENKINS_ENDPOINT,
            "$JENKINS_USER": settings.JENKINS_USER,
            "$JENKINS_TOKEN": settings.JENKINS_TOKEN,
            "$GIT_REPO": settings.GIT_REPO,
            "$GIT_CREDENTIAL": settings.GIT_CREDENTIAL,
            "$GIT_USERNAME": settings.GIT_USERNAME,
            "$GIT_PASSWORD": settings.GIT_PASSWORD,
            "$SONAR_ENDPOINT": settings.SONAR_ENDPOINT,
            "$SONAR_TOKEN": settings.SONAR_TOKEN,
            "$CLAIR_ENDPOINT": settings.CLAIR_ENDPOINT,
            "$CLAIR_SERVICE_PORT": settings.CLAIR_SERVICE_PORT,
            "$CLAIR_HEALTH_PORT": settings.CLAIR_HEALTH_PORT,
            "$CLAIR_DATABASE_ADDR": settings.CLAIR_DATABASE_ADDR,
            "$CLAIR_DATABASE_NAME": settings.CLAIR_DATABASE_NAME,
            "$CLAIR_DATABASE_USER_NAME": settings.CLAIR_DATABASE_USER_NAME,
            "$CLAIR_DATABASE_PASSWORD": settings.CLAIR_DATABASE_PASSWORD
        }
        self.get_user_weblab()
        self.input_file(self.common)
        self.get_region_data()
        if not self.is_weblab_open("USER_VIEW_ENABLED"):
            self.get_build_endpointid()
            self.get_load_balance_info()
            self.get_registry_uuid()
        self.get_master_ips()
        self.get_slave_ips()
        self.input_file(self.common)
        self.namespace_client = Namespace()
        self.space_client = Space()
        self.project_client = Project()
        self.noti_client = Notification()
        self.image_client = Image()
        self.app_client = Application()
        self.newapp = Newapplication()
        self.prepare()
        self.create_global_app()
        self.input_file(self.common)

    def get_rubick_url(self):
        env = os.environ.get('ENV') or "STAGING"
        if env.upper() == "STAGING":
            rubick_url = "https://console-staging.alauda.cn"
        elif env.upper() == "CN":
            rubick_url = "https://enterprise.alauda.cn"
        else:
            rubick_url = os.getenv('API_URL').replace('20081', '32005')
        if not rubick_url.startswith('http'):
            rubick_url = "http://" + rubick_url
        return rubick_url

    def get_user_weblab(self):
        FRONTEND_URL = self.get_rubick_url()
        login_url = "{}/ajax/landing/login".format(FRONTEND_URL)
        data = {
            "account": settings.ACCOUNT,
            "password": settings.PASSWORD
        }
        session = requests.Session()
        resp = session.post(login_url, data=data, verify=False)
        if resp.status_code != 200:
            return False
        url = "{}/ajax-sp/account/weblabs?namespace={}".format(FRONTEND_URL, settings.ACCOUNT)
        r = session.get(url)
        if r.status_code != 200:
            return False
        content = json.loads(r.text)['feature_flags']
        self.common.update({"$weblabs": content})

    def is_weblab_open(self, weblab_name):
        weblabs = self.common.get("$weblabs")
        if isinstance(weblabs, dict) and weblab_name in weblabs.keys() and weblabs[weblab_name]:
            return True
        else:
            return False

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        if not self.is_weblab_open("USER_VIEW_ENABLED"):
            response = self.send(method="GET", path="/v1/regions/{}/{}/".format(self.account, self.region_name))
        else:
            response = self.send(method="GET", path="/v2/regions/{}/{}/".format(self.account, self.region_name),
                                 params={})
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        self.region_id = self.region_data["id"]
        self.region_volume = self.network_modes = ""
        if self.region_data.get("features").get("volume") is not None:
            self.region_volume = ",".join(self.region_data.get("features").get("volume").get("features"))
        if self.region_data.get('features').get('network_modes') is not None:
            self.network_modes = ",".join(self.region_data.get('features').get('network_modes').get('features'))
        self.common.update({"$REGION_ID": self.region_id})
        self.common.update({"$REGION_VOLUME": self.region_volume})
        self.common.update({"NETWORK_MODES": self.network_modes})

    @retry()
    def get_build_endpointid(self):
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
        for content in reversed(contents):
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
        if not self.is_weblab_open("USER_VIEW_ENABLED"):
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
        else:
            response = self.send(method='GET',
                                 path='/v2/regions/{}/{}/nodes'.format(self.account, self.region_name), params={})
            assert response.status_code == 200, response.text
            contents = response.json()
            slaveips = []
            for content in contents.get("items"):
                if "node-role.kubernetes.io/node" in Common.get_value(content, "metadata.labels"):
                    slaveips.append(Common.get_uuid_accord_name(self, Common.get_value(content, "status.addresses"),
                                                                {'type': 'InternalIP'}, "address"))
            self.common.update({"$SLAVEIPS": ','.join(slaveips)})

    @retry()
    def get_master_ips(self):
        if not self.is_weblab_open("USER_VIEW_ENABLED"):
            response = self.send(method='GET',
                                 path='/v1/regions/{}/{}/nodes/'.format(self.account, self.region_name))
            assert response.status_code == 200, response.text
            contents = response.json()
            masterips = []
            for content in contents:
                if content.get("type") in ["SYSLAVE", "SYS"]:
                    masterips.append(content.get("private_ip"))
            self.common.update({"$MASTERIPS": ','.join(masterips)})
        else:
            response = self.send(method='GET',
                                 path='/v2/regions/{}/{}/nodes'.format(self.account, self.region_name), params={})
            assert response.status_code == 200, response.text
            contents = response.json()
            masterips = []
            for content in contents.get("items"):
                if "node-role.kubernetes.io/master" in Common.get_value(content, "metadata.labels"):
                    masterips.append(Common.get_uuid_accord_name(self, Common.get_value(content, "status.addresses"),
                                                                 {'type': 'InternalIP'}, "address"))
            self.common.update({"$MASTERIPS": ','.join(masterips)})

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
        response = self.project_client.get_project(settings.PROJECT_NAME)
        if response.status_code != 200:
            response = self.project_client.create_project('./test_data/project/project.yml',
                                                          {"$project": settings.PROJECT_NAME})
            assert response.status_code == 201, "prepare data failed: create project failed {}".format(response.text)
            self.common.update({"CREATE_PROJECT": True, "$PROJECT_UUID": response.json()['uuid']})
        else:
            self.common.update({"$PROJECT_UUID": response.json()['uuid']})
        if not self.is_weblab_open("USER_VIEW_ENABLED"):
            # create k8s namespace
            response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)
            if response.status_code != 200:
                response = self.namespace_client.create_namespaces("./test_data/namespace/namespace.yml",
                                                                   {"$K8S_NAMESPACE": settings.K8S_NAMESPACE})
                assert response.status_code == 201, "prepare data failed: create namespace failed {}".format(
                    response.text)
                self.common.update({"CREATE_NAMESPACE": True})
            response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)

            assert response.status_code == 200, "prepare data failed: get namespace detail failed {}".format(
                response.text)
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

            # 创建全局通知，提供给构建，流水线等使用
            global_noti_name = "e2e-global-noti"
            # 先删除已经存在的通知
            noti_id = self.noti_client.get_noti_id_from_list(global_noti_name)
            self.noti_client.delete_noti(noti_id)
            # 创建
            response = self.noti_client.create_noti("./test_data/notification/global_noti.json",
                                                    {"$noti_name": global_noti_name})
            assert response.status_code == 201, "创建全局通知失败了，原因是：{}".format(response.text)
            self.common.update({"$NOTI_NAME": response.json().get("name"), "$NOTI_UUID": response.json().get("uuid")})
        else:
            response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)
            if response.status_code != 200:
                response = self.namespace_client.create_general_namespaces('./test_data/namespace/newnamespace.yml',
                                                                           {'$K8S_NAMESPACE': settings.K8S_NAMESPACE})
                assert response.status_code == 201, "prepare data failed: create namespace failed {}".format(
                    response.text)
                self.common.update({"CREATE_NAMESPACE": True})
            response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)

            assert response.status_code == 200, "prepare data failed: get namespace detail failed {}".format(
                response.text)
            namespace_uuid = response.json()["kubernetes"]["metadata"]["uid"]
            self.common.update({"$K8S_NS_UUID": namespace_uuid})

    def create_global_app(self):
        if not self.is_weblab_open("USER_VIEW_ENABLED"):
            # 先删除已经存在的应用
            self.app_client.delete_app(self.app_name)
            # create service
            ret = self.app_client.create_app('./test_data/application/create_app.yml',
                                             {"$app_name": self.app_name, "$description": self.app_name,
                                              "$K8S_NS_UUID": self.common["$K8S_NS_UUID"]})

            assert ret.status_code == 201, "创建应用失败"

            # get service status
            content = ret.json()
            app_id = self.app_client.get_value(content, 'resource.uuid')
            service_uuid = self.app_client.get_value(content, 'services.0.resource.uuid')

            app_status = self.app_client.get_app_status(app_id, 'resource.status', 'Running')
            assert app_status, "应用运行失败"

            self.common.update({"$GLOBAL_APP_NAME": self.app_name, "$GLOBAL_APP_ID": app_id,
                                "$GLOBAL_SERVICE_ID": service_uuid})
        else:
            create_result = self.newapp.create_newapp('./test_data/newapp/newapp.json',
                                                      {'$newapp_name': self.app_name})
            assert create_result.status_code == 201, "新版应用创建失败 {}".format(create_result.text)
            app_status = self.newapp.get_newapp_status(settings.K8S_NAMESPACE, self.app_name, 'Running')
            assert app_status, "创建应用后，验证应用状态出错：app: {} is not running".format(self.app_name)
            self.common.update({"$GLOBAL_APP_NAME": self.app_name})


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
        self.noti_client = Notification()
        self.app_client = Application()
        self.newapp = Newapplication()
        self.delete()

    def delete(self):
        if not self.newapp.is_weblab_open("USER_VIEW_ENABLED"):
            self.app_client.delete_app(self.global_info['$GLOBAL_APP_NAME'])
            self.app_client.check_exists(self.app_client.app_common_url(self.global_info['$GLOBAL_APP_ID']), 404)
        else:
            self.newapp.delete_newapp(settings.K8S_NAMESPACE, self.global_info['$GLOBAL_APP_NAME'])
            self.newapp.check_exists(
                self.newapp.get_newapp_common_url(settings.K8S_NAMESPACE, self.global_info['$GLOBAL_APP_NAME']), 404)

        if "CREATE_NAMESPACE" in self.global_info:
            if not self.newapp.is_weblab_open("USER_VIEW_ENABLED"):
                self.namespace_client.delete_namespaces(settings.K8S_NAMESPACE)
            else:
                self.namespace_client.delete_general_namespaces(settings.K8S_NAMESPACE)

        if "CREATE_SPACE" in self.global_info:
            self.space_client.delete_space(settings.SPACE_NAME)

        if "CREATE_PROJECT" in self.global_info:
            self.project_client.delete_project_role(settings.PROJECT_NAME)
            self.project_client.delete_project(settings.PROJECT_NAME)

        noti_id = self.global_info.get("$NOTI_UUID")
        self.noti_client.delete_noti(noti_id)
