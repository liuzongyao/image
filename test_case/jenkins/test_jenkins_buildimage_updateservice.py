import re
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
        self.git_buidl_pipeline = "alauda-jenkins-pipeline-git-build"

        self.code_credential_name = self.app_tool.global_info.get('$SVN_CREDENTIAL')
        self.registry_credential_name = self.app_tool.global_info.get('$REG_CREDENTIAL')
        self.git_code_credential_name = self.app_tool.global_info.get('$GIT_CREDENTIAL')

        self.registry_name = self.app_tool.global_info.get("$REGISTRY")
        self.integration_name = "alauda-integration-instance-name-svn"
        self.app_name = self.app_tool.global_info.get("$GLOBAL_APP_NAME")
        self.app_id = self.app_tool.global_info.get("$GLOBAL_APP_ID")
        self.repo_tag = "alauda-e2e"
        self.repo_additional_tag = "alauda-e2e-additional"
        self.branch = "master"

        self.template_name = "alaudaBuildImageAndDeployService"
        self.build_template_name = "alaudaBuildImage"
        self.syncimage_template_name = "alaudaSyncImage"
        self.updateservice_template_name = "alaudaDeployService"

        self.time_out = '300'
        self.repo = self.app_tool.global_info.get("$REPO_NAME")
        self.pipeline_description = "alauda jenkins pipeline"

        self.teardown_class(self)

        # create jenkins integration instance
        self.create_integration = self.integration_tool.create_integration(
            './test_data/integration/ci_cd/create_integration.yaml', {"$INTEGRATION_NAME": self.integration_name})

    def teardown_class(self):
        pipeline_id = self.jenkins_tool.get_pipeline_id(self.pipeline_name)
        self.jenkins_tool.delete_pipeline(pipeline_id)

        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

        self.image_tool.delete_repo_tag(self.repo, self.repo_tag)
        self.image_tool.delete_repo_tag(self.repo, self.repo_additional_tag)

    def test_jenkins_buildimage_updateservice(self):
        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # Verify that the integration instance was created successfully
        assert self.create_integration.status_code == 201, "创建集成中心实例失败"
        integration_id = self.create_integration.json()['id']

        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.template_name, 'uuid')
        assert template_id, "获取模板失败"

        # create code credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_svn_code_credential.yaml',
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

        # get jenkins pipeline detail
        ret = self.jenkins_tool.get_pipeline_detail(pipeline_id)

        assert ret.status_code == 200, "获取流水线详情失败"

        contents = ret.json()

        script = re.search(r'("script":) "(.*)"(, "namespace": "[a-zA-Z0-9_-]*?",)', ret.text).group(2)

        logger.info("script: {}".format(script))

        pipeline_name = contents['name']

        # update jenkins pipeline
        ret = self.jenkins_tool.update_pipeline(pipeline_id,
                                                './test_data/jenkins/update_buildimage_updateservice_pipeline_svn.yaml',
                                                {"$pipeline_name": pipeline_name,
                                                 "$display_name": self.pipeline_name,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$pipeline_description": self.pipeline_description,
                                                 "$pipeline_script": script,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id,
                                                 "$REG_URL": registry_endpoint,
                                                 "$imageTag": self.repo_tag,
                                                 "$imageExtraTag": self.repo_additional_tag,
                                                 "$service_name": self.app_name,
                                                 "$time_out": self.time_out
                                                 })

        assert ret.status_code == 204, "更新流水线操作失败"

        # get jenkins pipeline detail
        ret = self.jenkins_tool.get_pipeline_detail(pipeline_id)

        assert ret.status_code == 200, "获取流水线详情失败"

        assert ret.json()['description'] == self.pipeline_description, "更新流水线失败"

        # execute pipeline
        ret = self.jenkins_tool.execute_pipeline('./test_data/jenkins/execute_pipeline.yaml',
                                                 {"$pipeline_uuid": pipeline_id})

        assert ret.status_code == 200, "执行流水线项目失败"

        history_id = ret.json()['uuid']

        # get pipeline status
        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'SUCCESS')

        assert ret, "流水线项目执行失败"

        # get the service image tag
        ret = self.app_tool.get_app_detail(self.app_id)

        assert ret.status_code == 200, "获取应用的镜像版本失败"

        image_tag = self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image'
                                            ).split(":")[-1]

        logger.info("image tag: {}".format(
            self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image')))

        assert image_tag == self.repo_additional_tag, "流水线更新应用失败"

        # delete jenkins pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)
        assert ret.status_code == 204, "删除Jenkins流水线项目操作失败"

        ret = self.jenkins_tool.get_pipeline_detail(pipeline_id)
        assert ret.status_code == 404, "流水线没有被成功删除掉"

        # delete image tag
        ret = self.image_tool.delete_repo_tag(self.repo, self.repo_tag)
        assert ret.status_code == 204, "删除镜像版本操作失败"

        ret = self.image_tool.delete_repo_tag(self.repo, self.repo_additional_tag)
        assert ret.status_code == 204, "删除镜像版本操作失败"

        ret = self.image_tool.get_repo_tag(self.repo)
        assert ret.status_code == 200, "获取镜像版本失败"

        assert self.repo_tag not in ret.text, "镜像版本没有被成功删除掉"

        assert self.repo_additional_tag not in ret.text, "镜像版本没有被成功删除掉"

    def test_jenkins_build_with_git(self):
        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # Verify that the integration instance was created successfully
        assert self.create_integration.status_code == 201, "创建集成中心实例失败"
        integration_id = self.create_integration.json()['id']

        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.build_template_name, 'uuid')
        assert template_id, "获取模板失败"

        # create code credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_git_code_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.git_code_credential_name)
        assert ret, "创建git代码库凭证失败或获取凭证失败"

        # create pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_build_pipeline_git.yaml',
                                                {"$pipeline_name": self.git_buidl_pipeline,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$branch": self.branch, "$template_uuid": template_id})

        assert ret.status_code == 201, "创建Jenkins流水线项目失败"

        pipeline_id = ret.json()['uuid']

        # execute pipeline
        ret = self.jenkins_tool.execute_pipeline('./test_data/jenkins/execute_pipeline.yaml',
                                                 {"$pipeline_uuid": pipeline_id})

        assert ret.status_code == 200, "执行流水线项目操作失败"

        history_id = ret.json()['uuid']

        # get pipeline status
        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'status', 'RUNNING')

        assert ret, "流水线项目未处于运行状态"

        # stop pipeline
        ret = self.jenkins_tool.pipeline_cancel(pipeline_id, history_id)

        assert ret.status_code == 204, "取消执行流水线操作失败"

        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'ABORTED')

        assert ret, "流水线项目取消执行失败"

        # replay pipeline
        ret = self.jenkins_tool.pipeline_replay('./test_data/jenkins/pipeline_replay.yaml',
                                                {"$pipeline_uuid": pipeline_id, "$history_id": history_id})

        assert ret.status_code == 200, "再次执行流水线操作失败"

        history_id = ret.json()['uuid']

        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'SUCCESS')

        assert ret, "流水线项目执行失败"

        # delete pipeline history
        ret = self.jenkins_tool.delete_pipeline_history(history_id, pipeline_id)

        assert ret.status_code == 204, "删除流水线历史操作失败"

        ret = self.jenkins_tool.check_pipeline_history_exist(history_id, pipeline_id, 404)

        assert ret, "删除流水线历史失败"

        # delete jenkins pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)
        assert ret.status_code == 204, "删除Jenkins流水线项目操作失败"

        ret = self.jenkins_tool.check_pipeline_exist(pipeline_id, 404)
        assert ret, "流水线没有被成功删除掉"
