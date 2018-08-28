import pytest
from test_case.integrations.ci_cd_integrations import Integrations


@pytest.mark.region
@pytest.mark.ci_cd
class TestCICDSuite(object):
    def setup_class(self):
        self.integration_tool = Integrations()

        self.integration_name = 'alauda-integration-{}'.format(self.integration_tool.region_name).replace('_', '-')

        self.description = "update instance"

        self.teardown_class(self)

    def teardown_class(self):
        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

    def test_ci_cd(self):
        # create integration instance
        create_ret = self.integration_tool.create_integration('./test_data/integration/ci_cd/create_integration.yaml',
                                                              {"$INTEGRATION_NAME": self.integration_name})
        assert create_ret.status_code == 201, "创建集成中心实例失败"

        integration_id = create_ret.json()['id']

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        status = get_ret.json()['enabled']

        assert status, "实例不是启用状态"

        # stop integration instance
        stop = self.integration_tool.stop_integration(integration_id,
                                                      './test_data/integration/ci_cd/stop_integration.yaml',
                                                      {"$INTEGRATION_ID": integration_id,
                                                       "$INTEGRATION_NAME": self.integration_name})
        assert stop.status_code == 200, "停用实例操作失败"

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        status = get_ret.json()['enabled']

        assert not status, "实例停用失败"

        # update integration instance
        update_ret = self.integration_tool.update_integration(integration_id,
                                                              './test_data/integration/ci_cd/update_integration.yaml',
                                                              {"$INTEGRATION_NAME": self.integration_name,
                                                               "$DESCRIPTION": self.description})
        assert update_ret.status_code == 200, "更新实例操作失败"

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        description = get_ret.json()['description']
        assert description == self.description, "更新实例失败"

        # delete integration instance
        delete_ret = self.integration_tool.delete_integration(integration_id)
        assert delete_ret.status_code == 204, "删除实例操作失败"

        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 404, "实例没有被成功删除掉"