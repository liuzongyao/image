import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.catalog.catalog import Catalog
from test_case.newapp.newapp import Newapplication


class TestMongodbSuite(object):

    def setup_class(self):
        self.middleware = Middleware()
        self.catalog = Catalog()
        self.newapp = Newapplication()
        self.name = "e2e-mongodb-pub"
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]

    def teardown_class(self):
        self.newapp.delete_newapp(self.namespace, self.name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.name), 404)

    @pytest.mark.middleware_mongodb
    def test_mongodb(self):

        # 中间件获取mongodb的模板id-获取mongodb可用的version id-创建mongodb应用-获取应用状态-删除应用
        result = {'flag': True}

        mongodb_template_id = self.middleware.get_template_id("mongodb")
        logger.info("中间件mongodb模板id：{}".format(mongodb_template_id))

        version_id = self.middleware.get_version_id(mongodb_template_id)
        logger.info("中间件mongodb的可使用的version id:{}".format(version_id))

        create_result = self.middleware.create_application('./test_data/middleware/mongodb.json',
                                                           {"$name": self.name, "$template_id": mongodb_template_id,
                                                            "$version_id": version_id})
        assert create_result.status_code == 201, "创建mongodb失败 {}".format(create_result.text)
        app_id = create_result.json()["kubernetes"]["metadata"]["uid"]
        logger.info("创建mongodb成功，name是：{}".format(self.name))

        app_status = self.middleware.get_application_status(self.namespace, self.name, "Running")
        assert app_status, "创建应用后，验证应用状态出错：app: {} is not running".format(self.name)
        logger.info("mongodb的应用状态为：Running")

        # pods_result = self.middleware.get_pods(self.namespace, self.name)
        # logger.info("拿到了pod请求的返回值")
        # hostIP = pods_result.json()[0]["kubernetes"]["status"]["hostIP"]
        # logger.info("获取mongodb容器Ip为：{}".format(hostIP))
        # podIP = pods_result.json()[0]["kubernetes"]["status"]["podIP"]
        # logger.info("获取mongodb所在podIp为：{}".format(podIP))
        delete_result = self.newapp.delete_newapp(self.namespace, self.name)
        assert delete_result.status_code == 204, "删除中间件创建的mongodb应用失败 {}".format(delete_result.text)
        logger.info("删除中间件创建的mongodb应用成功")
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.name), 404)
        assert result["flag"], True









