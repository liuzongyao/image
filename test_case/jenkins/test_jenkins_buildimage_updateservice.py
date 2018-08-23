from time import sleep
import pytest
from test_case.jenkins.jenkins import Jenkins
from test_case.application.app import Application
from test_case.image.image import Image
from test_case.integrations.ci_cd_integrations import Integrations


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

        self.teardown_class(self)

    def teardown_class(self):
        pipeline_id = self.jenkins_tool.get_pipeline_id(self.pipeline_name)
        self.jenkins_tool.delete_pipeline(pipeline_id)
        self.app_tool.delete_app(self.app_name)
        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

    def test_jenkins_buildimage_updateservice(self):
        # get template id
        template_id = self.jenkins_tool.get_sys_template_id(self.template_name, 'uuid')
        assert template_id, "get id of the sys template: {} failed".format(self.template_name)

        # create jenkins integration instance
        create_integration = self.integration_tool.create_integration(
            './test_data/integration/ci_cd/create_integration.yaml', {"$INTEGRATION_NAME": self.integration_name})

        assert create_integration.status_code == 201, "create jenkins integration instance failed, " \
                                                      "Error code: {}, Response: {}" \
            .format(create_integration.status_code, create_integration.text)

        integration_id = create_integration.json()['id']

        # create code credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_code_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.code_credential_name)
        assert ret, "create code credential failed or get code credential failed, please confirm manually"

        # create registry credential
        self.jenkins_tool.create_credential('./test_data/jenkins/create_registry_credential.yaml',
                                            {"$jenkins_integration_id": integration_id})

        ret = self.jenkins_tool.get_credential(integration_id, self.registry_credential_name)
        assert ret, "create registry credential failed or get registry credential failed, please confirm manually"

        # get image info
        registry_endpoint = self.app_tool.get_uuid_accord_name(self.app_tool.global_info.get("PRIVATE_REGISTRY"),
                                                               {"name": self.app_tool.global_info.get("$REGISTRY")},
                                                               "endpoint")
        repo = self.app_tool.global_info.get("$REPO_NAME")

        get_repo_tag_ret = self.image_tool.get_repo_tag(repo)

        assert get_repo_tag_ret.status_code == 200, "get {} tag failed, Error code: {}, Response: {}".format(
            repo, get_repo_tag_ret.status_code, get_repo_tag_ret.text)

        assert len(get_repo_tag_ret.json()['results']) > 0, "the tag of repo: {} is null".format(repo)

        repo_tag = self.app_tool.get_value(get_repo_tag_ret.json(), 'results.0.tag_name')

        print("repo tag: {}".format(repo_tag))

        image = "{}/{}:{}".format(registry_endpoint, repo, repo_tag)

        # create service
        ret = self.app_tool.create_app('./test_data/application/create_app.yml',
                                       {"$app_name": self.app_name, "$IMAGE": image})

        assert ret.status_code == 201, "create service failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        # get service status
        content = ret.json()
        app_id = self.app_tool.get_value(content, 'resource.uuid')

        app_status = self.app_tool.get_app_status(app_id, 'resource.status', 'Running')
        assert app_status, "app: {} is not running".format(self.app_name)

        # create jenkins pipeline
        ret = self.jenkins_tool.create_pipeline('./test_data/jenkins/create_buildimage_updateservice_pipeline_svn.yaml',
                                                {"$pipeline_name": self.pipeline_name,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$template_uuid": template_id, "$REG_URL": registry_endpoint,
                                                 "$imageTag": self.repo_tag, "$imageExtraTag": self.repo_additional_tag,
                                                 "$service_name": self.app_name, "$time_out": self.time_out})

        assert ret.status_code == 201, "create jenkins pipeline falied, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        pipeline_id = ret.json()['uuid']

        # execute pipeline
        ret = self.jenkins_tool.execute_pipeline('./test_data/jenkins/execute_pipeline.yaml',
                                                 {"$pipeline_uuid": pipeline_id})

        assert ret.status_code == 200, "execute pipeline failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        history_id = ret.json()['uuid']

        # get pipeline status
        ret = self.jenkins_tool.get_pipeline_status(history_id, pipeline_id, 'result', 'SUCCESS')

        assert ret, "Pipeline execution failed"

        # get the service image tag
        ret = self.app_tool.get_app_detail(app_id)

        assert ret.status_code == 200, "get service info failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        image_tag = self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image'
                                            ).split(":")[-1]

        print("image tag: {}".format(self.app_tool.get_value(ret.json(),
                                                             'kubernetes.0.spec.template.spec.containers.0.image')))

        assert image_tag == self.repo_additional_tag, "update service falied, the image tag should be {}, but {}" \
            .format(self.repo_additional_tag, image_tag)

        # delete service
        ret = self.app_tool.delete_app(self.app_name)
        assert ret.status_code == 204, "delete service failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        sleep(15)

        ret = self.app_tool.get_app_detail(app_id)
        assert ret.status_code == 404, "the service should be deleted, but still exist"

        # delete jenkins pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)
        assert ret.status_code == 204, "delete pipeline failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        ret = self.jenkins_tool.get_pipeline_detail(pipeline_id)
        assert ret.status_code == 404, "the pipeline should be deleted, but still exist"

        # delete integration instance
        ret = self.integration_tool.delete_integration(integration_id)
        assert ret.status_code == 204, "delete integration instance failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        ret = self.integration_tool.get_integration_detail(integration_id)
        assert ret.status_code == 404, "the integration instance should be deleted, but still exist"

        # delete image tag
        ret = self.image_tool.delete_repo_tag(repo, self.repo_tag)
        assert ret.status_code == 204, "delete image tag failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        ret = self.image_tool.delete_repo_tag(repo, self.repo_additional_tag)
        assert ret.status_code == 204, "delete image tag failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        ret = self.image_tool.get_repo_tag(repo)
        assert ret.status_code == 200, "get image tag failed, Error code: {}, Response: {}" \
            .format(ret.status_code, ret.text)

        assert self.repo_tag not in ret.text, "the tag: {} of image: {} should be deleted, but still exist" \
            .format(self.repo_tag, repo)

        assert self.repo_additional_tag not in ret.text, "the tag: {} of image: {} should be deleted, but still exist" \
            .format(self.repo_additional_tag, repo)
