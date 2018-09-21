import pytest
from test_case.plugin.plugin import Plugin
from test_case.application.app import Application
from test_case.integrations.ci_cd_integrations import Integrations
from common.log import logger


class TestPluginSuite(object):
    def setup_class(self):
        self.plugin_tool = Plugin()
        self.app_tool = Application()
        self.integration_tool = Integrations()

        self.plugin_instance_name = 'alauda-plugin-app'
        self.suff = self.plugin_tool.randstring()
        self.sonarqube_volume = '/plugin/sonarqube{}'.format(self.suff)
        self.db_volume = '/plugin/db{}'.format(self.suff)
        self.integration_name = 'alauda-plugin-integration'

        self.region_id = self.plugin_tool.global_info.get('$REGION_ID')
        self.network_modes = self.plugin_tool.global_info.get('NETWORK_MODES')
        # self.region_volume = self.plugin_tool.global_info.get('$REGION_VOLUME')

        # get plugin list
        self.plugin_list = self.plugin_tool.get_plugin_list(self.region_id)

        self.teardown_class(self)

    def teardown_class(self):
        self.app_tool.delete_app(self.plugin_instance_name)

        # sonar_volume_id = self.volume_tool.get_volume_id_from_list(self.sonarqube_volume)
        # db_volume_id = self.volume_tool.get_volume_id_from_list(self.db_volume)
        #
        # self.volume_tool.delete_volume(sonar_volume_id)
        # self.volume_tool.delete_volume(db_volume_id)

        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

    @pytest.mark.sonarqube
    def test_sonarqube_plugin(self):
        if 'flannel' not in self.network_modes and 'macvlan' not in self.network_modes:
            logger.info("网络模式不为flannel或macvlan，不需要执行")
            assert True, "网络模式不为flannel或macvlan，不需要执行"
            return

        if self.plugin_list.status_code != 200:
            assert False, "获取插件中心列表失败"
        else:
            if '"plugin_type": "SonarQube"' not in self.plugin_list.text:
                logger.info("插件中心列表中不包含sonarqube，不需要执行")
                assert True, "插件中心列表中不包含sonarqube，不需要执行"

        if 'flannel' in self.network_modes:
            network_mode = 'flannel'
        else:
            network_mode = 'macvlan'

        # integration_name = "{}-{}".format(self.plugin_instance_name, self.integration_name)

        # install sonarqube plugin
        ret = self.plugin_tool.install_plugin('SonarQube', './test_data/plugin/install_clair_plugin.yaml',
                                              {"$plugin_instance_name": self.plugin_instance_name,
                                               "$network_mode": network_mode,
                                               "$sonarqube_volume": self.sonarqube_volume,
                                               "$db_volume": self.db_volume,
                                               "$integration_name": self.integration_name})

        assert ret.status_code == 201, "安装sonarqube插件操作失败"

        plugin_uuid = ret.json().get('uuid')

        # get app status
        ret = self.plugin_tool.get_install_plugin_status('SonarQube', plugin_uuid, 'pluginapplication.status',
                                                         'Running')

        assert ret, "sonarqube插件部署应用失败"

        # get integration instance status
        ret = self.plugin_tool.get_install_plugin_status('SonarQube', plugin_uuid, 'pluginintegration.status',
                                                         'Succeed')

        assert ret, "sonarqube插件创建集成中心实例失败"

        # get plugin status
        ret = self.plugin_tool.get_install_plugin_status('SonarQube', plugin_uuid, 'status', 'Succeed')

        assert ret, "安装sonarqube插件失败"

        ret = self.plugin_tool.get_install_plugin_detail('SonarQube', plugin_uuid)

        assert ret.status_code == 200, "获取已安装的插件的详情失败"

        app_uuid = ret.json()['pluginapplication']['uuid']

        integration_id = ret.json()['pluginintegration']['uuid']

        # get running plugin
        ret = self.plugin_tool.get_running_plugin('SonarQube', self.region_id)

        assert ret.status_code == 200, "获取运行中的插件的操作失败"

        assert app_uuid in ret.text, "已成功安装的插件不在运行中的插件列表中"

        # delete app
        ret = self.app_tool.delete_app(self.plugin_instance_name)

        assert ret.status_code == 204, "删除应用操作失败"

        ret = self.app_tool.check_app_exist(app_uuid, 404)

        assert ret, "删除应用失败"

        # delete integration instance
        ret = self.integration_tool.delete_integration(integration_id)

        assert ret.status_code == 204, "删除集成中心实例操作失败"

        ret = self.integration_tool.check_integration_exist(integration_id, 404)

        assert ret, "删除集成中心实例失败"
