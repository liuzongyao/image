import pytest

from common.log import logger
from test_case.integrations.ci_cd_integrations import Integrations


@pytest.mark.ace
@pytest.mark.BAT
@pytest.mark.flaky(reruns=2, reruns_delay=3)
class TestCICDSuite(object):
    def setup_class(self):
        self.integration_tool = Integrations()
        self.integration_name = 'alauda-integration-{}'.format(self.integration_tool.region_name).replace('_', '-')
        self.sonar_integration_name = 'alauda-sonar-integration'
        self.clair_integration_name = 'alauda-clair-integration'
        self.description = "update instance"
        self.teardown_class(self)

    def teardown_class(self):
        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        sonar_integration_id = self.integration_tool.get_integration_id(self.sonar_integration_name)
        clair_integration_id = self.integration_tool.get_integration_id(self.clair_integration_name)
        self.integration_tool.delete_integration(integration_id)
        self.integration_tool.delete_integration(sonar_integration_id)
        self.integration_tool.delete_integration(clair_integration_id)

    def test_ci_cd(self):
        # create integration instance
        create_ret = self.integration_tool.create_integration('./test_data/integration/ci_cd/create_integration.json',
                                                              {"$INTEGRATION_NAME": self.integration_name})
        assert create_ret.status_code == 201, "创建集成中心实例失败"
        logger.info("创建集成中心实例成功")

        integration_id = create_ret.json()['id']

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        status = get_ret.json()['enabled']

        assert status, "实例不是启用状态"
        logger.info("集成实例是启用状态")

        # stop integration instance
        stop = self.integration_tool.stop_integration(integration_id,
                                                      './test_data/integration/ci_cd/stop_integration.json',
                                                      {"$INTEGRATION_NAME": self.integration_name})
        assert stop.status_code == 200, "停用实例操作失败"

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        status = get_ret.json()['enabled']

        assert not status, "实例停用失败"
        logger.info("实例停用成功")

        # update integration instance
        update_ret = self.integration_tool.update_integration(integration_id,
                                                              './test_data/integration/ci_cd/update_integration.json',
                                                              {"$INTEGRATION_NAME": self.integration_name,
                                                               "$DESCRIPTION": self.description})
        assert update_ret.status_code == 200, "更新实例操作失败"

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        description = get_ret.json()['description']
        assert description == self.description, "更新实例失败"
        logger.info("更新实例成功")

        # delete integration instance
        delete_ret = self.integration_tool.delete_integration(integration_id)
        assert delete_ret.status_code == 204, "删除实例操作失败"

        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 404, "实例没有被成功删除掉"
        logger.info("删除实例成功")

    def test_sonar_integration(self):
        # create integration instance
        create_ret = self.integration_tool.create_integration(
            './test_data/integration/sonar/create_sonar_integration.json',
            {"$integration_name": self.sonar_integration_name})

        assert create_ret.status_code == 201, "创建集成中心实例失败"

        integration_id = create_ret.json()['id']

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        status = get_ret.json()['enabled']

        assert status, "实例不是启用状态"

        # stop integration instance
        stop = self.integration_tool.stop_integration(integration_id,
                                                      './test_data/integration/sonar/stop_sonar_integration.json',
                                                      {"$integration_name": self.sonar_integration_name})
        assert stop.status_code == 200, "停用实例操作失败"

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        status = get_ret.json()['enabled']

        assert not status, "实例停用失败"

        # update integration instance
        update_ret = self.integration_tool.update_integration(
            integration_id, './test_data/integration/sonar/update_sonar_integration.json',
            {"$integration_name": self.sonar_integration_name, "$description": self.description})

        assert update_ret.status_code == 200, "更新实例操作失败"

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, '获取集成中心状态失败'

        description = get_ret.json()['description']
        assert description == self.description, "更新实例失败"

        # delete integration instance
        delete_ret = self.integration_tool.delete_integration(integration_id)
        assert delete_ret.status_code == 204, "删除实例操作失败"

        get_ret = self.integration_tool.check_integration_exist(integration_id, 404)
        assert get_ret, "实例没有被成功删除掉"

        # 2.0后没有镜像扫描，所以不测clair了

        # @pytest.mark.clair_integration
        # def test_clair_integration(self):
        #     # create integration instance
        #     create_ret = self.integration_tool.create_integration(
        #         './test_data/integration/clair/create_clair_integration.yaml',
        #         {"$integration_name": self.clair_integration_name})
        #
        #     assert create_ret.status_code == 201, "创建集成中心实例失败"
        #
        #     integration_id = create_ret.json()['id']
        #
        #     # get integration instance status
        #     get_ret = self.integration_tool.get_integration_detail(integration_id)
        #     assert get_ret.status_code == 200, '获取集成中心状态失败'
        #
        #     status = get_ret.json()['enabled']
        #
        #     assert status, "实例不是启用状态"
        #
        #     # stop integration instance
        #     stop = self.integration_tool.stop_integration(integration_id,
        #                                                   './test_data/integration/clair/stop_clair_integration.yaml',
        #                                                   {"$integration_id": integration_id,
        #                                                    "$integration_name": self.clair_integration_name})
        #     assert stop.status_code == 200, "停用实例操作失败"
        #
        #     # get integration instance status
        #     get_ret = self.integration_tool.get_integration_detail(integration_id)
        #     assert get_ret.status_code == 200, '获取集成中心状态失败'
        #
        #     status = get_ret.json()['enabled']
        #
        #     assert not status, "实例停用失败"
        #
        #     # update integration instance
        #     update_ret = self.integration_tool.update_integration(
        #         integration_id, './test_data/integration/sonar/update_sonar_integration.yaml',
        #         {"$integration_name": self.clair_integration_name, "$description": self.description})
        #
        #     assert update_ret.status_code == 200, "更新实例操作失败"
        #
        #     # get integration instance status
        #     get_ret = self.integration_tool.get_integration_detail(integration_id)
        #     assert get_ret.status_code == 200, '获取集成中心状态失败'
        #
        #     description = get_ret.json()['description']
        #     assert description == self.description, "更新实例失败"
        #
        #     # delete integration instance
        #     delete_ret = self.integration_tool.delete_integration(integration_id)
        #     assert delete_ret.status_code == 204, "删除实例操作失败"
        #
        #     get_ret = self.integration_tool.check_integration_exist(integration_id, 404)
        #     assert get_ret, "实例没有被成功删除掉"
