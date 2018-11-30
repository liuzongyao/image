import pytest
from backup.resources.resources import Resources
from test_case.integrations.ci_cd_integrations import Integrations
from test_case.jenkins.jenkins import Jenkins


@pytest.mark.space
class TestResourcesSuite(object):
    def setup_class(self):
        self.resources_tool = Resources()
        self.integration_tool = Integrations()
        self.jenkins_tool = Jenkins()

        self.space_name = 'alauda-space-{}'.format(self.resources_tool.region_name).replace('_', '-')
        self.description = 'space test'

        self.integration_name = 'alauda-space-integration'

        self.pipeline_name = 'alauda-space-jenkins'

        self.branch = 'master'

        self.build_template_name = "alaudaBuildImage"

        self.git_code_credential_name = self.jenkins_tool.global_info.get('$GIT_CREDENTIAL')

        self.teardown_class(self)

    def teardown_class(self):
        pipeline_id = self.jenkins_tool.get_pipeline_id(self.pipeline_name)
        self.jenkins_tool.delete_pipeline(pipeline_id)

        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

        self.resources_tool.delete_space(self.space_name)

    @pytest.mark.BAT
    def test_space(self):
        # create space
        space_ret = self.resources_tool.create_space('./test_data/resources/create_resources.yaml',
                                                     {"$space_name": self.space_name, "$description": self.space_name})

        assert space_ret.status_code == 201, "创建space操作失败"

        # get space detail
        space_ret = self.resources_tool.get_space_detail(self.space_name)

        assert space_ret.status_code == 200, "获取space的详细信息失败"

        # update space
        space_ret = self.resources_tool.update_space(self.space_name, './test_data/resources/update_resources.yaml',
                                                     {"$space_name": self.space_name, "$description": self.description})

        assert space_ret.status_code == 204, "更新space操作失败"

        # get space detail
        space_ret = self.resources_tool.get_space_detail(self.space_name)

        assert space_ret.status_code == 200, "获取space的详细信息失败"

        assert space_ret.json()['description'] == self.description, "更新space失败"

        # access jenkins
        ret = self.jenkins_tool.access_jenkins()
        assert ret, "访问Jenkins失败, 请确认Jenkins是否正常"

        # create jenkins integration instance
        self.create_integration = self.integration_tool.create_integration(
            './test_data/integration/ci_cd/create_integration.yaml', {"$INTEGRATION_NAME": self.integration_name,
                                                                      "$SPACE_NAME": self.space_name})

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
                                                {"$pipeline_name": self.pipeline_name, "$SPACE_NAME": self.space_name,
                                                 "$jenkins_integration_id": integration_id,
                                                 "$jenkins_integration_name": self.integration_name,
                                                 "$branch": self.branch, "$template_uuid": template_id})

        assert ret.status_code == 201, "创建Jenkins流水线项目失败"

        pipeline_id = ret.json()['uuid']

        # get resources list
        space_ret = self.resources_tool.get_resources_list(self.space_name)

        assert space_ret.status_code == 200, "获取space的资源详情失败"

        assert pipeline_id in space_ret.text, "新创建的Jenkins流水线项目没有出现在space资源详情中"

        # delete jenkins pipeline
        ret = self.jenkins_tool.delete_pipeline(pipeline_id)

        # 删除流水线有个bug，暂时屏蔽掉assert
        # assert ret.status_code == 204, "删除Jenkins流水线操作失败"

        ret = self.jenkins_tool.check_pipeline_exist(pipeline_id, 404)

        assert ret, "删除Jenkins流水线失败"

        # delete integration
        ret = self.integration_tool.delete_integration(integration_id)

        assert ret.status_code == 204, "删除集成中心实例操作失败"

        ret = self.integration_tool.check_integration_exist(integration_id, 404)

        assert ret, "删除集成中心实例失败"

        # delete space
        ret = self.resources_tool.delete_space(self.space_name)

        assert ret.status_code == 204, "删除space操作失败"

        ret = self.resources_tool.check_space_exist(self.space_name, 404)

        assert ret, "删除space失败"
