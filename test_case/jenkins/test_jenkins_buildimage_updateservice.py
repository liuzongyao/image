import pytest
from test_case.jenkins.jenkins import Jenkins
from test_case.application.app import Application
from test_case.image.image import Image
from test_case.integrations.ci_cd_integrations import Integrations
from common.log import logger


@pytest.mark.region
@pytest.mark.buildimageupdateservice
class TestJenkinsBuildImageUpdateService(object):
    def setup_class(self):
        self.app_tool = Application()
        self.jenkins_tool = Jenkins()
        self.integration_tool = Integrations()
        self.image_tool = Image()

        self.pipeline_name = "alauda-jenkins-pipeline"
        self.code_credential_name = self.app_tool.global_info.get('$SVN_CREDENTIAL')
        self.registry_credential_name = self.app_tool.global_info.get('$REG_CREDENTIAL')
        self.registry_name = self.app_tool.global_info.get("$REGISTRY")
        self.integration_name = "alauda-integration-instance-name-svn"
        self.app_name = "alauda-jenkins-pipeline-app"
        self.repo_tag = "alauda-e2e"
        self.repo_additional_tag = "alauda-e2e-additional"
        self.template_name = "alaudaBuildImageAndDeployService"
        self.time_out = '300'
        self.repo = self.app_tool.global_info.get("$REPO_NAME")

        self.teardown_class(self)

    def teardown_class(self):
        pipeline_id = self.jenkins_tool.get_pipeline_id(self.pipeline_name)
        self.jenkins_tool.delete_pipeline(pipeline_id)

        self.app_tool.delete_app(self.app_name)

        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

        self.image_tool.delete_repo_tag(self.repo, self.repo_tag)
        self.image_tool.delete_repo_tag(self.repo, self.repo_additional_tag)

    def test_jenkins_buildimage_updateservice(self):
        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.template_name, 'uuid')
        assert template_id, "获取模板失败"

        # create jenkins integration instance
        create_integration = self.integration_tool.create_integration(
            './test_data/integration/ci_cd/create_integration.yaml', {"$INTEGRATION_NAME": self.integration_name})

        assert create_integration.status_code == 201, "创建集成中心实例失败"

        integration_id = create_integration.json()['id']

        # create code credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_code_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.code_credential_name)
        assert ret, "创建svn代码库凭证失败或获取凭证失败"

        # create registry credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_registry_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.registry_credential_name)
        assert ret, "创建镜像仓库凭证失败"

        # get image info
        registry_endpoint = self.app_tool.get_uuid_accord_name(self.app_tool.global_info.get("PRIVATE_REGISTRY"),
                                                               {"name": self.app_tool.global_info.get("$REGISTRY")},
                                                               "endpoint")

        get_repo_tag_ret = self.image_tool.get_repo_tag(self.repo)

        assert get_repo_tag_ret.status_code == 200, "获取镜像版本列表失败"

        assert len(get_repo_tag_ret.json()['results']) > 0, "镜像版本为空"

        repo_tag = self.app_tool.get_value(get_repo_tag_ret.json(), 'results.0.tag_name')

        logger.info("repo tag: {}".format(repo_tag))

        image = "{}/{}:{}".format(registry_endpoint, self.repo, repo_tag)

        # create service
        ret = self.app_tool.create_app('./test_data/application/create_app.yml',
                                       {"$app_name": self.app_name, "$IMAGE": image})

        assert ret.status_code == 201, "创建应用失败"

        # get service status
        content = ret.json()
        app_id = self.app_tool.get_value(content, 'resource.uuid')

        app_status = self.app_tool.get_app_status(app_id, 'resource.status', 'Running')
        assert app_status, "应用运行失败"

        # create jenkins pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_buildimage_updateservice_pipeline_svn.yaml',
                                                {"$pipeline_name": self.pipeline_name,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id, "$REG_URL": registry_endpoint,
                                                 "$imageTag": self.repo_tag, "$imageExtraTag": self.repo_additional_tag,
                                                 "$service_name": self.app_name, "$time_out": self.time_out})

        assert ret.status_code == 201, "创建Jenkins流水线项目失败"

        pipeline_id = ret.json()['uuid']

        # execute pipeline
        ret = self.jenkins_tool.execute_pipeline('./test_data/jenkins/execute_pipeline.yaml',
                                                 {"$pipeline_uuid": pipeline_id})

        assert ret.status_code == 200, "执行流水线项目失败"

        history_id = ret.json()['uuid']

        # get pipeline status
        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'SUCCESS')

        assert ret, "流水线项目执行失败"

        # get the service image tag
        ret = self.app_tool.get_app_detail(app_id)

        assert ret.status_code == 200, "获取应用的镜像版本失败"

        image_tag = self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image'
                                            ).split(":")[-1]

        logger.info("image tag: {}".format(
            self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image')))

        assert image_tag == self.repo_additional_tag, "流水线更新应用失败"

        # delete service
        ret = self.app_tool.delete_app(self.app_name)
        assert ret.status_code == 204, "删除应用操作失败"

        ret = self.app_tool.check_app_exist(app_id, 404)

        assert ret, "应用没有被成功删除掉"

        # delete jenkins pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)
        assert ret.status_code == 204, "删除Jenkins流水线项目操作失败"

        ret = self.jenkins_tool.get_pipeline_detail(pipeline_id)
        assert ret.status_code == 404, "流水线没有被成功删除掉"

        # delete integration instance
        ret = self.integration_tool.delete_integration(integration_id)
        assert ret.status_code == 204, "删除集成中心实例操作失败"

        ret = self.integration_tool.get_integration_detail(integration_id)
        assert ret.status_code == 404, "集成中心实例没有被成功删除掉"

        # delete image tag
        ret = self.image_tool.delete_repo_tag(self.repo, self.repo_tag)
        assert ret.status_code == 204, "删除镜像版本操作失败"

        ret = self.image_tool.delete_repo_tag(self.repo, self.repo_additional_tag)
        assert ret.status_code == 204, "删除镜像版本操作失败"

        ret = self.image_tool.get_repo_tag(self.repo)
        assert ret.status_code == 200, "获取镜像版本失败"

        assert self.repo_tag not in ret.text, "镜像版本没有被成功删除掉"

        assert self.repo_additional_tag not in ret.text, "镜像版本没有被成功删除掉"
