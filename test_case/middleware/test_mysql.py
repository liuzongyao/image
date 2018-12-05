import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication


@pytest.mark.BAT
class TestMysqlSuite(object):

    def setup_class(self):
        self.middleware = Middleware()
        self.newapp = Newapplication()
        self.mysql_name = "e2e-mysql-pub"
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]

    def teardown_class(self):
        logger.info("清除mysql应用资源")
        self.newapp.delete_newapp(self.namespace, self.mysql_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.mysql_name), 404)
        logger.info("清除完毕")

    @pytest.mark.middleware_mysql
    def test_mysql(self):

        result = {"flag": True}
        mysql_template_id = self.middleware.get_template_id("mysql")
        version_id = self.middleware.get_version_id(mysql_template_id)

        create_result = self.middleware.create_application('./test_data/middleware/mysql.json',
                                                           {"$name": self.mysql_name, "$template_id": mysql_template_id,
                                                            "$version_id": version_id})
        assert create_result.status_code == 201, "中间件创建mysql应用失败 {}".format(create_result.text)
        logger.info("中间间创建mysql应用成功，name:{}".format(self.mysql_name))

        app_status = self.middleware.get_application_status(self.namespace, self.mysql_name, "Running")
        assert app_status, "创建应用后，验证应用状态出错，app:{} is not Running".format(self.mysql_name)
        logger.info("mysql应用状态在运行中")

        delete_result = self.newapp.delete_newapp(self.namespace, self.mysql_name)
        assert delete_result.status_code == 204, "删除中间件创建出的mysql应用失败{}".format(delete_result)
        logger.info("删除mysql应用成功")
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.mysql_name), 404)

        assert result["flag"], True
