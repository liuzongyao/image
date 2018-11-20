import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication


class TestZookeeperSuite(object):

    def setup_class(self):
        self.newapp = Newapplication()
        self.middleware = Middleware()
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]
        self.zookeeper_name = "e2e-zookeeper-pub"

    def teardown_class(self):
        logger.info("清除zookeeper应用资源")
        self.newapp.delete_newapp(self.namespace, self.zookeeper_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.zookeeper_name), 404)
        logger.info("清除完毕")

    @pytest.mark.middleware_zookeeper
    def test_zookeeper(self):

        # todo: 创建zookeeper应用失败，报错500。但是页面可以创建成功
        result = {"flag": True}
        zookeeper_template_id = self.middleware.get_template_id("zookeeper")
        version_id = self.middleware.get_version_id(zookeeper_template_id)
        create_result = self.middleware.create_application('./test_data/middleware/zookeeper.json',
                                                           {"$name": self.zookeeper_name, "$template_id": zookeeper_template_id,
                                                            "$version_id": version_id})
        assert create_result.status_code == 201, "中间件创建zookeeper应用失败 {}".format(create_result.text)
        logger.info("中间件创建zookeeper应用成功")

        app_status = self.middleware.get_application_status(self.namespace, self.zookeeper_name, "Running")
        assert app_status, "创建应用后，验证应用状态出错，app:{} is not Running".format(self.zookeeper_name)
        logger.info("中间件zookeeper应用为运行中")

        delete_result = self.newapp.delete_newapp(self.namespace, self.zookeeper_name)
        assert delete_result.status_code == 204, "删除zookeeper应用失败 {}".format(delete_result.text)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.zookeeper_name), 404)
        logger.info("删除zookeeper应用成功")

        assert result["flag"], True

