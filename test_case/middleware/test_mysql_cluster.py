import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication


class TestMysqlClusterSuite(object):

    def setup_class(self):

        self.middleware = Middleware()
        self.newapp = Newapplication()
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]
        self.mysql_cluster_name = "e2e-mysql-clu"

    def teardown_class(self):
        self.newapp.delete_newapp(self.namespace, self.mysql_cluster_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.mysql_cluster_name), 404)

    @pytest.mark.middleware_mysql_cluster
    def test_mysql_cluster(self):

        result = {"flag": True}
        template_id = self.middleware.get_template_id("mysql-cluster")
        version_id = self.middleware.get_version_id(template_id)

        create_result = self.middleware.create_application('./test_data/middleware/mysql-cluster.json',
                                                           {"$name": self.mysql_cluster_name,
                                                            "$template_id": template_id, "$version_id": version_id})
        assert create_result.status_code == 201, "中间件创建应用mysql-cluster失败 {}".format(create_result.text)
        logger.info("中间件创建mysql-cluster应用成功")

        app_status = self.middleware.get_application_status(self.namespace, self.mysql_cluster_name, "Running")
        assert app_status, "mysql-cluster应用的状态不在运行中"
        logger.info("mysql-cluster应用在运行中")

        delete_result = self.newapp.delete_newapp(self.namespace, self.mysql_cluster_name)
        assert delete_result.status_code == 204, "删除mysql-cluster应用失败 {}".format(delete_result.text)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.mysql_cluster_name), 404)
        logger.info("删除mysql-cluster应用成功")

        assert result['flag'], True
