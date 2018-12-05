import pytest

from common.log import logger
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication
from test_case.storageclasses.scs import Scs


@pytest.mark.BAT
class TestZookeeperSuite(object):

    def setup_class(self):
        self.newapp = Newapplication()
        self.middleware = Middleware()
        self.scs = Scs()

        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]
        self.zookeeper_name = "e2e-zookeeper-pub"
        self.kafka_name = "e2e-kafka-pub"

        scs_list_result = self.scs.list_scs()
        assert len(scs_list_result.json()) > 0, "没有存储类,不能创建zookeeper,创建zookeeper用例失败"
        self.scs_name = scs_list_result.json()[0]["kubernetes"]["metadata"]["name"]
        logger.info("查出来的第一个scs {}".format(self.scs_name))

        # 创建zookeeper
        zookeeper_template_id = self.middleware.get_template_id("zookeeper")
        version_id = self.middleware.get_version_id(zookeeper_template_id)
        create_result = self.middleware.create_application('./test_data/middleware/zookeeper.json',
                                                           {"$name": self.zookeeper_name,
                                                            "$template_id": zookeeper_template_id,
                                                            "$version_id": version_id, "$scs_name": self.scs_name})
        assert create_result.status_code == 201, "测试kafka前提条件创建zookeeper应用失败 {}".format(create_result.text)
        logger.info("测试kafka前提条件创建zookeeper应用成功")

        app_status = self.middleware.get_application_status(self.namespace, self.zookeeper_name, "Running")
        assert app_status, "测试kafka前提条件创建zookeeper应用后，验证应用状态出错，app:{} is not Running".format(self.zookeeper_name)
        logger.info("测试kafka前提条件zookeeper应用为运行中")

    def teardown_class(self):
        logger.info("清除zookeeper应用资源")
        self.newapp.delete_newapp(self.namespace, self.kafka_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.kafka_name), 404)
        self.newapp.delete_newapp(self.namespace, self.zookeeper_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.zookeeper_name), 404)
        logger.info("清除完毕")

    @pytest.mark.middleware_kafka
    def test_kafka(self):

        zookeeper_deploy = self.zookeeper_name + "-zookeeper"
        logger.info("拼接起来的zookeeper deploy的名称 {}".format(zookeeper_deploy))

        result = {"flag": True}
        kafka_template_id = self.middleware.get_template_id("kafka")
        version_id = self.middleware.get_version_id(kafka_template_id)
        create_result = self.middleware.create_application('./test_data/middleware/kafka.json',
                                                           {"$name": self.kafka_name, "$template_id": kafka_template_id,
                                                            "$version_id": version_id, "$zookeeper": zookeeper_deploy,
                                                            "$scs_name": self.scs_name})
        assert create_result.status_code == 201, "中间件创建kafka应用失败 {}".format(create_result)
        logger.info("中间件创建kafka应用成功")

        app_status = self.middleware.get_application_status(self.namespace, self.kafka_name, "Running")
        assert app_status, "创建应用后，验证应用状态出错，app:{} is not Running".format(self.kafka_name)
        logger.info("中间件kafka应用为运行中")

        delete_result = self.newapp.delete_newapp(self.namespace, self.kafka_name)
        assert delete_result.status_code == 204, "删除kafka应用失败 {}".format(delete_result.text)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.kafka_name), 404)
        logger.info("删除kafka应用成功")

        assert result["flag"], True



