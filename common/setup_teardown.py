# coding=utf-8
import json
import os
from time import sleep
from common import settings
from common.api_requests import AlaudaRequest
from common.base_request import Common
from common.loadfile import FileUtils
from common.utils import retry
from test_case.image.image import Image
from test_case.namespace.namespace import Namespace
from test_case.newapp.newapp import Newapplication
from test_case.notification.notification import Notification
from test_case.project.project import Project
from test_case.cluster.cluster import Cluster
from test_case.cluster.qcloud import create_instance, destroy_instance, get_instance

instances_id = []
global_app_name = ''


class SetUp(AlaudaRequest):
    """
    测试前先获取global信息已经新建一些测试的必须资源
    """

    def __init__(self):
        super(SetUp, self).__init__()
        global global_app_name
        global_app_name = "alauda-global-app"
        self.common = {
            "$NAMESPACE": settings.ACCOUNT,
            "$PASSWORD": settings.PASSWORD,
            "$SVN_CREDENTIAL": settings.SVN_CREDENTIAL,
            "$SVN_PASSWORD": settings.SVN_PASSWORD,
            "$SVN_USERNAME": settings.SVN_USERNAME,
            "$SVN_REPO": settings.SVN_REPO,
            "$REGISTRY": settings.REGISTRY_NAME,
            "$REPO_NAME": settings.REPO_NAME,
            "$TARGET_REPO_NAME": settings.TARGET_REPO_NAME,
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
            "$GIT_PATH": settings.GIT_PATH,
            "$GIT_BRANCH": settings.GIT_BRANCH,
            "$SONAR_ENDPOINT": settings.SONAR_ENDPOINT,
            "$SONAR_TOKEN": settings.SONAR_TOKEN,
            "$CLAIR_ENDPOINT": settings.CLAIR_ENDPOINT,
            "$CLAIR_SERVICE_PORT": settings.CLAIR_SERVICE_PORT,
            "$CLAIR_HEALTH_PORT": settings.CLAIR_HEALTH_PORT,
            "$CLAIR_DATABASE_ADDR": settings.CLAIR_DATABASE_ADDR,
            "$CLAIR_DATABASE_NAME": settings.CLAIR_DATABASE_NAME,
            "$CLAIR_DATABASE_USER_NAME": settings.CLAIR_DATABASE_USER_NAME,
            "$CLAIR_DATABASE_PASSWORD": settings.CLAIR_DATABASE_PASSWORD,
            "$MIDDLEWARE_REGISTRY": settings.MIDDLEWARE_REGISTRY
        }
        self.input_file(self.common)
        self.cluster_client = Cluster()
        self.deploy_region()
        self.get_region_data()
        self.get_registry_uuid()
        self.get_master_ips()
        self.get_slave_ips()
        self.input_file(self.common)
        self.namespace_client = Namespace()
        self.project_client = Project()
        self.noti_client = Notification()
        self.image_client = Image()
        self.newapp = Newapplication()
        self.prepare()
        self.create_global_app()
        self.input_file(self.common)

    def deploy_region(self):
        if settings.ENV != "private":
            return
        if self.cluster_client.get_region_info(settings.REGION_NAME).status_code == 200:
            return
        self.common.update({"CREATE_REGION": True})
        ret_create = create_instance(2)
        assert ret_create["success"], ret_create["message"]
        global instances_id
        instances_id = ret_create['instances_id']
        # instances_id = ['ins-9g5juvv6', 'ins-6t6okkqc']
        ret_get = get_instance(instances_id)
        assert ret_get["success"], ret_get["message"]
        private_ips = ret_get['private_ips']
        public_ips = ret_get['public_ips']
        self.cluster_client.restart_sshd(public_ips[0])
        for public_ip in public_ips:
            self.cluster_client.excute_script("hostname node$RANDOM", public_ip)
        get_script = self.cluster_client.generate_install_cmd("test_data/cluster/two_node_cluster_cmd.json",
                                                              {"$cluster_name": settings.REGION_NAME,
                                                               "$master_ip": private_ips[0],
                                                               "$slave_ip": private_ips[1]})
        assert get_script.status_code == 200, "获取创建集群脚本失败:{}".format(get_script.text)
        cmd = "export LANG=zh_CN.utf8;export LC_ALL=zh_CN.utf8;{}".format(get_script.json()["commands"]["install"])
        ret_excute = self.cluster_client.excute_script(cmd, public_ips[0])
        assert "Install successfully!" in ret_excute[1], "执行脚本失败:{}".format(ret_excute[1])
        is_exist = self.cluster_client.check_value_in_response("v1/regions/{}".format(self.cluster_client.account),
                                                               settings.REGION_NAME,
                                                               params={})
        assert is_exist, "添加集群超时"

        ret_list = self.cluster_client.get_region_list()
        assert ret_list.status_code == 200, "获取集群列表失败:{}".format(ret_list.text)
        region_name_list = self.cluster_client.get_value_list(ret_list.json(), "name")
        assert settings.REGION_NAME in region_name_list, "新建集群不在集群列表内"
        region_id = self.cluster_client.get_uuid_accord_name(ret_list.json(), {"name": settings.REGION_NAME}, "id")
        self.cluster_client.region_id = region_id

        # 获取下namespace 不然安装不了nevermore 会出错default namespace找不到
        self.send(method="GET", path="v2/kubernetes/clusters/{}/namespaces".format(region_id), params={})
        sleep(5)
        self.cluster_client.check_exists(
            "v2/kubernetes/clusters/{}/namespaces/{}".format(region_id, "default"), 200, params={})

        # 部署完第一次安装会出错，需要等待一段时间才可以正常安装，但是不确定具体时间
        ret_log1 = self.cluster_client.install_nevermore(settings.REGION_NAME,
                                                         "test_data/cluster/install_nevermore.json")
        sleep(1)
        ret_log2 = self.cluster_client.install_nevermore(settings.REGION_NAME,
                                                         "test_data/cluster/install_nevermore.json")
        assert ret_log1.status_code == 200 or ret_log2.status_code == 200, "安装nevermore失败：{}, {}".format(
            ret_log1.text, ret_log2.text)

        ret_registry = self.cluster_client.install_registry(settings.REGION_NAME, settings.REGISTRY_NAME,
                                                            "test_data/cluster/install_registry.json")
        assert ret_registry.status_code == 200, "安装registry失败：{}".format(ret_registry.text)

        ret_result = self.cluster_client.check_feature_status(settings.REGION_NAME)
        assert ret_result['success'], "特性安装失败:{}".format(ret_result)

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        response = self.send(method="GET", path="/v2/regions/{}/{}/".format(self.account, self.region_name),
                             params={})
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        self.region_id = self.region_data["id"]
        self.region_volume = self.network_modes = self.network_type = self.network_policy = ""
        if self.region_data.get("features").get("volume") is not None:
            self.region_volume = ",".join(self.region_data.get("features").get("volume").get("features"))
        if self.region_data.get('features').get('network_modes') is not None:
            self.network_modes = ",".join(self.region_data.get('features').get('network_modes').get('features'))
        if self.region_data.get('attr').get('kubernetes').get('cni') is not None:
            self.network_type = self.region_data.get('attr').get('kubernetes').get('cni').get('type')
            self.network_policy = self.region_data.get('attr').get('kubernetes').get('cni').get('network_policy')
        self.common.update({"$REGION_ID": self.region_id})
        self.common.update({"$REGION_VOLUME": self.region_volume})
        self.common.update({"NETWORK_MODES": self.network_modes})
        self.common.update({"$NETWORK_TYPE": self.network_type})
        self.common.update({"$NETWORK_POLICY": self.network_policy})

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
        self.project_client.delete_project(settings.PROJECT_NAME)
        response = self.project_client.get_project(settings.PROJECT_NAME)
        if response.status_code != 200:
            response = self.project_client.create_project('./test_data/project/project.yml',
                                                          {"$project": settings.PROJECT_NAME})
            assert response.status_code == 201, "prepare data failed: create project failed {}".format(response.text)
            self.common.update({"CREATE_PROJECT": True, "$PROJECT_UUID": response.json()['uuid']})
        else:
            self.common.update({"$PROJECT_UUID": response.json()['uuid']})
        self.namespace_client.delete_general_namespaces(settings.K8S_NAMESPACE)
        self.namespace_client.check_exists(self.namespace_client.get_namespace_url(settings.K8S_NAMESPACE), 404)
        response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)
        if response.status_code != 200:
            response = self.namespace_client.create_general_namespaces('./test_data/namespace/newnamespace.yml',
                                                                       {'$K8S_NAMESPACE': settings.K8S_NAMESPACE})
            assert response.status_code == 201, "prepare data failed: create namespace failed {}".format(
                response.text)
            self.common.update({"CREATE_NAMESPACE": True})
        response = self.namespace_client.get_namespaces(settings.K8S_NAMESPACE)

        assert response.status_code == 200, "prepare data failed: get namespace detail failed {}".format(response.text)
        namespace_uuid = response.json()["kubernetes"]["metadata"]["uid"]
        self.common.update({"$K8S_NS_UUID": namespace_uuid})

    def create_global_app(self):
        self.newapp.delete_newapp(settings.K8S_NAMESPACE, global_app_name)
        self.newapp.check_exists(
            self.newapp.get_newapp_common_url(settings.K8S_NAMESPACE, global_app_name), 404)
        create_result = self.newapp.create_newapp('./test_data/newapp/newapp.json',
                                                  {'$newapp_name': global_app_name})
        assert create_result.status_code == 201, "新版应用创建失败 {}".format(create_result.text)
        app_status = self.newapp.get_newapp_status(settings.K8S_NAMESPACE, global_app_name, 'Running')
        assert app_status, "创建应用后，验证应用状态出错：app: {} is not running".format(global_app_name)
        app_uuid = self.newapp.get_value(create_result.json(), '0.kubernetes.metadata.uid')
        self.common.update({"$GLOBAL_APP_NAME": global_app_name})
        self.common.update({"$GLOBAL_APP_ID": app_uuid})


class TearDown(AlaudaRequest):
    """
    测试结束后删除setup创建的资源
    """

    def __init__(self):
        super(TearDown, self).__init__()
        self.global_info = FileUtils.load_file(self.global_info_path)
        self.namespace_client = Namespace()
        self.project_client = Project()
        self.noti_client = Notification()
        self.newapp = Newapplication()
        self.cluster = Cluster()
        self.delete()

    def delete(self):
        self.newapp.delete_newapp(settings.K8S_NAMESPACE, global_app_name)
        self.newapp.check_exists(
            self.newapp.get_newapp_common_url(settings.K8S_NAMESPACE, global_app_name), 404)

        if "CREATE_NAMESPACE" in self.global_info:
            self.namespace_client.delete_general_namespaces(settings.K8S_NAMESPACE)

        if "CREATE_PROJECT" in self.global_info:
            self.project_client.delete_project_role(settings.PROJECT_NAME)
            self.project_client.delete_project(settings.PROJECT_NAME)

        if "CREATE_REGION" in self.global_info:
            self.cluster.uninstall_nevermore(settings.REGION_NAME)
            self.cluster.uninstall_registry(settings.REGION_NAME)
            self.namespace_client.delete_general_namespaces("default")
            self.namespace_client.delete_general_namespaces("kube-system")
            self.cluster.delete_cluster(settings.REGION_NAME)
            destroy_instance(instances_id)

        noti_id = self.global_info.get("$NOTI_UUID")
        self.noti_client.delete_noti(noti_id)
