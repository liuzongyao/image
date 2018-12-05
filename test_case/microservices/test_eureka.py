import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication


class TestEureka(object):
    def setup_class(self):

        self.middleware = Middleware()
        self.newapp = Newapplication()
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]
        self.name = "e2e-eureka"

    def teardown_class(self):
        self.newapp.delete_newapp(self.namespace, self.name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.name), 404)

    @pytest.mark.microservices_eureka
    def test_eureka(self):

        result = {"flag": True}
        template_id = self.middleware.get_template_id("eureka")
        logger.info("eureka template id: {}".format(template_id))
        version_id = self.middleware.get_version_id(template_id)
        logger.info("eureka version id: {}".format(version_id))

        create_result = self.middleware.create_application('./test_data/microservices/eureka.json',
                                                           {"name": self.name, "$template_id": template_id,
                                                            "$version_id": version_id})

        assert create_result.status_code == 201, "微服务创建应用eureka失败 {}".format(create_result.text)
        logger.info("微服务创建应用eureka成功")

        # todo 这里的状态会报错，看一下返回值之类的一样么？
        app_status = self.middleware.get_application_status(self.namespace, self.name, "Running")
        assert app_status, "eureka应用状态不为running"
        logger.info("eureka应用状态为running")

        delete_result = self.newapp.delete_newapp(self.namespace, self.name)
        assert delete_result.status_code == 204, "删除微服务eureka应用成功 {}".format(delete_result.text)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.name), 404)
        logger.info("删除微服务应用eureka成功")

        assert result["flag"], True
