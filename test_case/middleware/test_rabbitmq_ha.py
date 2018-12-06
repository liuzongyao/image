import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication


class TestRabbitmq(object):

    def setup_class(self):
        self.middleware = Middleware()
        self.newapp = Newapplication()
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]
        self.name = "e2e-rabbitmq-ha"

    def teardown_class(self):
        self.newapp.delete_newapp(self.namespace, self.name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.name), 404)

    @pytest.mark.middleware_rabbitmq_ha
    def test_rabbitmq_ha(self):
        result = {"flag": True}
        template_id = self.middleware.get_template_id("rabbitmq-ha")
        version_id = self.middleware.get_version_id(template_id)
        create_result = self.middleware.create_application('./test_data/middleware/rabbitmq-ha.json',
                                                           {"$name": self.name, "$template_id": template_id,
                                                            "$version_id": version_id})

        assert create_result.status_code == 201, "中间件创建rabbitmq-ha应用失败 {}".format(create_result.text)

        logger.info("中间件创建rabbitmq-ha应用成功")

        app_status = self.middleware.get_application_status(self.namespace, self.name, "Running")
        assert app_status, "rabbitmq-ha应用状态不是运行中"
        logger.info("rabbitmq-ha应用状态是运行中")

        delete_result = self.newapp.delete_newapp(self.namespace, self.name)
        assert delete_result.status_code == 204, "删除rabbitnq-ha应用失败 {}".format(delete_result.text)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.name), 404)
        logger.info("删除rabbitmq-ha应用成功")

        assert result["flag"], True
