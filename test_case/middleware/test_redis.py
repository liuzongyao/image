import pytest

from common.log import logger
from test_case.newapp.newapp import Newapplication
from test_case.middleware.middleware import Middleware


class TestRedisSuite(object):

    def setup_class(self):
        self.newapp = Newapplication()
        self.middleware = Middleware()
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]
        self.redis_name = "e2e-redis-pub"

    def teardown_class(self):
        logger.info("清除redis应用资源")
        self.newapp.delete_newapp(self.namespace, self.redis_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.redis_name), 404)
        logger.info("清除完毕")

    @pytest.mark.middleware_redis
    def test_redis(self):
        result = {"flag": True}
        redis_template_id = self.middleware.get_template_id("redis")
        version_id = self.middleware.get_version_id(redis_template_id)
        create_result = self.middleware.create_application('./test_data/middleware/redis.json',
                                                           {"$name": self.redis_name, "$template_id": redis_template_id,
                                                            "$version_id": version_id})
        assert create_result.status_code == 201, "中间件创建redis应用失败 {}".format(create_result.text)
        logger.info("创建redis应用成功")

        app_status = self.middleware.get_application_status(self.namespace, self.redis_name, "Running")
        assert app_status, "创建应用后，验证应用状态出错，app:{} is not Running".format(self.redis_name)
        logger.info("redis应用为运行中")

        delete_result = self.newapp.delete_newapp(self.namespace, self.redis_name)
        assert delete_result.status_code == 204, "删除redis应用失败 {}".format(delete_result)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.redis_name), 404)
        logger.info("删除redis应用成功")

        assert result["flag"], True
