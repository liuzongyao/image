import re
import time
import pytest
from test_case.newapp.newapp import Newapplication
from common.log import logger
from test_case.image.image import Image
from test_case.integrations.ci_cd_integrations import Integrations
from test_case.jenkins.jenkins import Jenkins


class TestJenkinsBuildImageUpdateService(object):
    def setup_class(self):
        self.app_tool = Newapplication()
        self.jenkins_tool = Jenkins()
        self.integration_tool = Integrations()
        self.image_tool = Image()

        self.pipeline_name = "alauda-jenkins-pipeline"
        self.git_buidl_pipeline = "alauda-jenkins-pipeline-git-build"
        self.svn_build_pipeline_no_sonar = "alauda-jenkins-pipeline-svn-build-no-sonar"
        self.svn_build_pipeline_with_sonar = "alauda-jenkins-pipeline-svn-build-with-sonar"
        self.update_service_pipeline = "alauda-jenkins-update-service-pipeline"
        self.sync_registry_pipeline = "alauda-jenkins-sync-registry-pipeline"

        self.code_credential_name = self.app_tool.global_info.get('$SVN_CREDENTIAL')
        self.registry_credential_name = self.app_tool.global_info.get('$REG_CREDENTIAL')
        self.git_code_credential_name = self.app_tool.global_info.get('$GIT_CREDENTIAL')

        # self.get_publick_registry = self.app_tool.global_info.get('PUBLIC_REGISTRY')
        self.image = self.app_tool.global_info.get('$IMAGE')

        self.registry_name = self.app_tool.global_info.get("$REGISTRY")
        self.integration_name = "alauda-integration-instance-name-svn"
        self.sonar_integration_name = "alauda-sonar-integration-instance-name"
        self.namespace = self.app_tool.global_info["$K8S_NAMESPACE"]
        self.app_name = self.app_tool.global_info.get("$GLOBAL_APP_NAME")
        # self.app_id = self.app_tool.global_info.get("$GLOBAL_APP_ID")
        self.repo_tag = "alauda-e2e"
        self.repo_additional_tag = "alauda-e2e-additional"
        self.sync_repo_tag = "alauda-e2e-sync"
        self.branch = "master"

        self.template_name = "newalaudaBuildImageAndDeployService"
        self.build_template_name = "alaudaBuildImage"
        self.syncimage_template_name = "alaudaSyncImage"
        self.updateservice_template_name = "newalaudaDeployService"

        self.time_out = '300'
        self.repo = self.app_tool.global_info.get("$REPO_NAME")
        self.target_repo = self.app_tool.global_info.get("$TARGET_REPO_NAME")
        self.pipeline_description = "alauda jenkins pipeline"

        self.qualitygates_name = "SonarQube way"
        self.language_name = 'Java'

        self.teardown_class(self)

        # create jenkins integration instance
        self.create_integration = self.integration_tool.create_integration(
            './test_data/integration/ci_cd/create_integration.yaml', {"$INTEGRATION_NAME": self.integration_name})

        # create sonar integration instance
        self.create_sonar_integration = self.integration_tool.create_integration(
            './test_data/integration/sonar/create_sonar_integration.yaml',
            {"$integration_name": self.sonar_integration_name})

    def teardown_class(self):
        pipeline_id = self.jenkins_tool.get_pipeline_id(self.pipeline_name)
        git_build_pipeline_id = self.jenkins_tool.get_pipeline_id(self.git_buidl_pipeline)
        svn_build_pipeline_no_sonar_id = self.jenkins_tool.get_pipeline_id(self.svn_build_pipeline_no_sonar)
        svn_build_pipeline_with_sonar_id = self.jenkins_tool.get_pipeline_id(self.svn_build_pipeline_with_sonar)
        update_service_pipeline_id = self.jenkins_tool.get_pipeline_id(self.update_service_pipeline)
        sync_registry_pipeline_id = self.jenkins_tool.get_pipeline_id(self.sync_registry_pipeline)

        self.jenkins_tool.delete_pipeline(pipeline_id)
        self.jenkins_tool.delete_pipeline(git_build_pipeline_id)
        self.jenkins_tool.delete_pipeline(svn_build_pipeline_no_sonar_id)
        self.jenkins_tool.delete_pipeline(svn_build_pipeline_with_sonar_id)
        self.jenkins_tool.delete_pipeline(update_service_pipeline_id)
        self.jenkins_tool.delete_pipeline(sync_registry_pipeline_id)

        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        sonar_integration_id = self.integration_tool.get_integration_id(self.sonar_integration_name)
        self.integration_tool.delete_integration(integration_id)
        self.integration_tool.delete_integration(sonar_integration_id)

        self.image_tool.delete_repo_tag(self.repo, self.repo_tag)
        self.image_tool.delete_repo_tag(self.repo, self.repo_additional_tag)
        self.image_tool.delete_repo_tag(self.repo, self.sync_repo_tag)

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

        script = re.search(r'("script":) "(.*)"(, "namespace": "[a-zA-Z0-9_-]*?", "created_by")', ret.text).group(2)

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
        ret = self.app_tool.get_newapp_detail(self.namespace, self.app_name)

        assert ret.status_code == 200, "获取应用的镜像版本失败"

        image_tag = ""
        for i in range(0, len(ret.json())):
            if ("image" in str(ret.json()[i])):
                image_tag = self.app_tool.get_value(ret.json()[i], 'kubernetes.spec.template.spec.containers.0.image'
                                                    ).split(":")[-1]

        assert image_tag == self.repo_tag, "流水线更新应用失败"

        # delete jenkins pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)
        assert ret.status_code == 204, "删除Jenkins流水线项目操作失败"

        ret = self.jenkins_tool.get_pipeline_detail(pipeline_id)
        assert ret.status_code == 404, "流水线没有被成功删除掉"

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

        # 由于执行流水线后立即取消执行会导致取消执行失败，添加2秒的等待时间
        time.sleep(2)

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

        # get pipeline logs
        ret = self.jenkins_tool.get_pipeline_log(history_id, pipeline_id)
        assert ret, "获取流水线日志失败"

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

    def test_jenkins_build_with_svn_no_sonar(self):
        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # Verify that the integration instance was created successfully
        assert self.create_integration.status_code == 201, "创建集成中心实例失败"
        integration_id = self.create_integration.json()['id']

        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.build_template_name, 'uuid')
        assert template_id, "获取模板失败"

        # get registry url
        registry_endpoint = self.app_tool.get_uuid_accord_name(self.app_tool.global_info.get("PRIVATE_REGISTRY"),
                                                               {"name": self.app_tool.global_info.get("$REGISTRY")},
                                                               "endpoint")

        # get repo tag
        ret = self.image_tool.get_repo_tag(self.repo)
        assert ret.status_code == 200, "获取镜像版本失败"

        contents = ret.json()['results']

        assert len(contents) > 0, "镜像版本为空"

        repo_tag = contents[0]['tag_name']

        # create code credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_svn_code_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.code_credential_name)
        assert ret, "创建svn代码库凭证失败或获取凭证失败"

        # create registry credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_registry_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.registry_credential_name)
        assert ret, "创建镜像仓库凭证失败或获取凭证失败"

        # create jenkins pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_build_pipeline_no_sonar_svn.yaml',
                                                {"$pipeline_name": self.svn_build_pipeline_no_sonar,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id, "$REG_URL": registry_endpoint,
                                                 "$repo_tag": repo_tag, "$ci_commands": "ls"})

        assert ret.status_code == 201, "创建Jenkins流水线项目失败"

        pipeline_id = ret.json()['uuid']

        # get pipeline list
        ret = self.jenkins_tool.get_pipeline_list()

        assert ret.status_code == 200, "获取流水线项目列表失败"

        contents = ret.text

        assert pipeline_id in contents, "流水线项目列表中不包含该流水线项目"

        # execute pipeline
        ret = self.jenkins_tool.execute_pipeline('./test_data/jenkins/execute_pipeline.yaml',
                                                 {"$pipeline_uuid": pipeline_id})

        assert ret.status_code == 200, "执行流水线项目失败"

        history_id = ret.json()['uuid']

        # get pipeline status
        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'SUCCESS')

        assert ret, "流水线项目执行失败"

        # get pipeline history list
        ret = self.jenkins_tool.get_pipeline_history_list(integration_id)

        assert ret.status_code == 200, "获取流水线运行历史列表失败"

        assert pipeline_id in ret.text, "流水线运行历史列表中不包含该流水线运行的历史记录"

        # delete pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)

        assert ret.status_code == 204, "删除流水线项目操作失败"

        ret = self.jenkins_tool.check_pipeline_exist(pipeline_id, 404)

        assert ret, "删除流水线项目失败"

    def test_jenkins_update_service(self):
        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # Verify that the integration instance was created successfully
        assert self.create_integration.status_code == 201, "创建集成中心实例失败"
        integration_id = self.create_integration.json()['id']

        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.updateservice_template_name, 'uuid')
        assert template_id, "获取模板失败"

        # get registry url
        registry_endpoint = self.app_tool.get_uuid_accord_name(self.app_tool.global_info.get("PRIVATE_REGISTRY"),
                                                               {"name": self.app_tool.global_info.get("$REGISTRY")},
                                                               "endpoint")

        # get repo tag
        ret = self.image_tool.get_repo_tag(self.repo)
        assert ret.status_code == 200, "获取镜像版本失败"

        contents = ret.json()['results']

        assert len(contents) > 0, "镜像版本为空"

        repo_tag = contents[0]['tag_name']

        # create pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_update_service_pipeline.yaml',
                                                {"$pipeline_name": self.update_service_pipeline,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id, "$service_name": self.app_name,
                                                 "$REG_URL": registry_endpoint, "$imageTag": repo_tag,
                                                 "$time_out": self.time_out})

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

        # get the service info
        ret = self.app_tool.get_newapp_detail(self.namespace, self.app_name)

        assert ret.status_code == 200, "获取应用的详情失败"

        image_tag = ""
        for i in range(0, len(ret.json())):
            if ("image" in str(ret.json()[i])):
                image_tag = self.app_tool.get_value(ret.json()[i], 'kubernetes.spec.template.spec.containers.0.image'
                                                    ).split(":")[-1]

        assert image_tag == repo_tag, "流水线更新应用镜像版本失败"

        # delete pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)

        assert ret.status_code == 204, "执行删除Jenkins流水线操作失败"

        ret = self.jenkins_tool.check_pipeline_exist(pipeline_id, 404)

        assert ret, "删除Jenkins流水线失败"

    def test_jenkins_build_with_svn_sonar(self):
        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # access sonar
        ret = self.jenkins_tool.access_sonar()
        assert ret, "访问sonar失败，请确认sonar是否正常"

        # Verify that the integration instance was created successfully
        assert self.create_integration.status_code == 201, "创建jenkins集成中心实例失败"
        integration_id = self.create_integration.json()['id']

        assert self.create_sonar_integration.status_code == 201, "创建sonar集成中心实例失败"
        sonar_integration_id = self.create_sonar_integration.json()['id']

        # create code credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_svn_code_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.code_credential_name)
        assert ret, "创建svn代码库凭证失败或获取凭证失败"

        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.build_template_name, 'uuid')
        assert template_id, "获取模板失败"

        # get qualitygates
        ret = self.jenkins_tool.get_sonar_qualitygates(sonar_integration_id)

        assert ret.status_code == 200, "获取sonar扫描质量阈值失败"

        quality_id = self.jenkins_tool.get_uuid_accord_name(ret.json()['qualitygates'],
                                                            {"name": self.qualitygates_name}, 'id')

        logger.info("qualitygates id: {}".format(quality_id))

        # get languages
        ret = self.jenkins_tool.get_languages(sonar_integration_id)

        assert ret.status_code == 200, "获取开发语言失败"

        language = self.jenkins_tool.get_uuid_accord_name(ret.json()['languages'], {"name": self.language_name}, 'key')

        logger.info("language: {}".format(language))

        # create pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_build_pipeline_with_sonar_svn.yaml',
                                                {"$pipeline_name": self.svn_build_pipeline_with_sonar,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id,
                                                 "$integrationSonarQubeID": sonar_integration_id,
                                                 "$quality": str(quality_id),
                                                 "$lang": language})

        assert ret.status_code == 201, "创建Jenkins流水线失败"

        pipeline_id = ret.json()['uuid']

        # execute pipeline
        ret = self.jenkins_tool.execute_pipeline('./test_data/jenkins/execute_pipeline.yaml',
                                                 {"$pipeline_uuid": pipeline_id})

        assert ret.status_code == 200, "执行流水线项目失败"

        history_id = ret.json()['uuid']

        # get pipeline status
        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'SUCCESS')

        assert ret, "流水线项目执行失败"

        # get pipeline history detail
        ret = self.jenkins_tool.get_pipeline_history_detail(history_id, pipeline_id)

        assert ret.status_code == 200, "获取流水线运行历史详情失败"

        assert "SonarQube" in ret.text, "流水线运行历史中没有代码扫描的结果"

        # delete pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)

        assert ret.status_code == 204, "执行删除Jenkins流水线操作失败"

        ret = self.jenkins_tool.check_pipeline_exist(pipeline_id, 404)

        assert ret, "删除Jenkins流水线失败"

    def test_jenkins_sync_registry(self):
        # if not self.get_publick_registry:
        # assert True, "no public registry, no need to run"
        # return

        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # Verify that the integration instance was created successfully
        assert self.create_integration.status_code == 201, "创建jenkins集成中心实例失败"
        integration_id = self.create_integration.json()['id']

        # create registry credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_registry_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.registry_credential_name)
        assert ret, "创建镜像仓库凭证失败或获取镜像仓库凭证失败"

        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.syncimage_template_name, 'uuid')
        assert template_id, "获取模板失败"

        # get source registry info
        # contents = self.image.split('/', 1)

        # source_reg_url = contents[0]

        # content = contents[1].split(":")

        # source_repo = content[0]

        # source_tag = content[1]

        # get dest registry url
        # reg_url = self.jenkins_tool.global_info.get("PRIVATE_REGISTRY")[0]['endpoint']

        source_reg_url = self.app_tool.get_uuid_accord_name(self.app_tool.global_info.get("PRIVATE_REGISTRY"),
                                                            {"name": self.app_tool.global_info.get("$REGISTRY")},
                                                            "endpoint")

        # get repo tag
        ret = self.image_tool.get_repo_tag(self.repo)
        assert ret.status_code == 200, "获取镜像版本失败"

        contents = ret.json()['results']

        assert len(contents) > 0, "镜像版本为空"

        self.sync_repo_tag = contents[0]['tag_name']

        # create source_repo
        ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                          {"$REPO_IMAGE": self.target_repo})
        assert ret.status_code == 201, "创建目标镜像仓库失败"

        # create pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_sync_registry_pipeline.yaml',
                                                {"$pipeline_name": self.sync_registry_pipeline,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id, "$source_reg_url": source_reg_url,
                                                 "$source_tag": self.sync_repo_tag,
                                                 "$reg_url": source_reg_url, "$target_repo": self.target_repo,
                                                 "$tag": self.sync_repo_tag})

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

        # 加2秒的等待时间，以防镜像仓库中的数据还没有更新
        time.sleep(2)

        # get repo tag
        ret = self.image_tool.get_repo_tag(self.target_repo)
        assert ret.status_code == 200, "获取镜像版本失败"

        logger.info("image tags list: {}".format(ret.text))

        assert self.sync_repo_tag in ret.text, "同步镜像仓库失败"

        # delete image repo
        ret = self.image_tool.delete_repo(self.target_repo)
        assert ret.status_code == 204, "删除镜像版本操作失败"

        # delete pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)

        assert ret.status_code == 204, "执行删除Jenkins流水线操作失败"

        ret = self.jenkins_tool.check_pipeline_exist(pipeline_id, 404)

        assert ret, "删除Jenkins流水线失败"

    @pytest.mark.BAT
    @pytest.mark.ace
    @pytest.mark.flaky(reruns=2, reruns_delay=3)
    def test_jenkins_template(self):
        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # get system template list
        ret = self.jenkins_tool.get_template_list()

        assert ret.status_code == 200, "获取模板列表失败"

        assert len(ret.json()['results']) > 0, "模板列表为空"

        # get template source
        ret = self.jenkins_tool.get_template_source_list()

        assert ret.status_code == 200, "获取模板仓库列表失败"

        content = ret.json()['result']

        assert len(content) > 0, "模板仓库列表为空"

        template_source_id = self.jenkins_tool.get_uuid_accord_name(content, {"provider": "user"}, 'uuid')

        logger.info("template source id: {}".format(template_source_id))

        if not template_source_id:
            assert True, "用户未添加模板仓库，不需要进行后面的同步模板仓库操作"
            return

        # refresh template source
        ret = self.jenkins_tool.refresh_template_source(template_source_id)

        assert ret.status_code == 204, "同步模板仓库操作失败"

        # get refresh status
        ret = self.jenkins_tool.get_refresh_template_source_status(template_source_id, 'last_job.status', 'SUCCESS')

        assert ret, "同步模板仓库执行失败"

        # get template source detail
        ret = self.jenkins_tool.get_template_source_detail(template_source_id)

        assert ret.status_code == 200, "获取模板详情失败"

        report = ret.json()['last_job']['report']['items']

        # get user template list
        ret = self.jenkins_tool.get_template_list(template_resource_id=template_source_id, official=False)

        assert ret.status_code == 200, "获取用户定义的模板列表失败"

        if not report:
            assert len(ret.json()['results']) == 0, "同步模板仓库失败"
        else:
            add = self.jenkins_tool.get_uuid_accord_name(report, {"action": "ADD"}, "name")
            delete = self.jenkins_tool.get_uuid_accord_name(report, {"action": "DELETE"}, "name")
            skip = self.jenkins_tool.get_uuid_accord_name(report, {"action": "SKIP"}, "name")

            if add:
                assert add in ret.text, "同步模板仓库失败"

            if delete:
                assert delete not in ret.text, "同步模板仓库失败"

            if skip:
                assert add in ret.text, "同步模板仓库失败"
