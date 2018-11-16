import pytest

from common.log import logger
from test_case.service.service import Service


@pytest.mark.service
@pytest.mark.ace
class TestServiceSuite(object):
    def setup_class(self):
        self.service = Service()
        self.service_name = 'service-{}'.format(self.service.region_name).replace('_', '-')
        self.namespace = self.service.global_info["$K8S_NAMESPACE"]
        self.teardown_class(self)

    def teardown_class(self):
        self.service.delete_service(self.namespace, self.service_name)

    @pytest.mark.BAT
    def test_service(self):
        '''
        创建内部路由-内部路由列表-获取详情-更新内部路由-搜索内部路由-删除内部路由
        :return:
        '''
        result = {"flag": True}
        # create service
        createservice_result = self.service.create_service("./test_data/service/service.json",
                                                           {"$service_name": self.service_name, '"$targetport"': "80"})
        assert createservice_result.status_code == 201, "创建内部路由失败:{}".format(createservice_result.text)

        # list service
        list_result = self.service.list_service(self.namespace)
        result = self.service.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.service.update_result(result, self.service_name in list_result.text, "内部路由列表：新建内部路由不在列表中")

        # get service detail
        detail_result = self.service.get_service_detail(self.namespace, self.service_name)
        result = self.service.update_result(result, detail_result.status_code == 200, detail_result.text)
        logger.info(detail_result.text)
        service_json = detail_result.json()['kubernetes']
        service_json['spec']['ports'][0]['targetPort'] = 8088

        # update service
        update_result = self.service.update_service(self.namespace, self.service_name, service_json)
        assert update_result.status_code == 204, "更新内部路由出错:{}".format(update_result.text)

        # search service
        search_result = self.service.search_service(self.namespace, self.service_name)
        result = self.service.update_result(result, search_result.status_code == 200, search_result.text)
        result = self.service.update_result(result, len(search_result.json()) == 1, search_result.text)
        result = self.service.update_result(result, self.service.get_value(search_result.json(),
                                                                           '0.kubernetes.spec.ports.0.targetPort') == 8088,
                                            "更新内部路由失败 targetport没有更新 {}".format(search_result.text))

        # delete service
        delete_result = self.service.delete_service(self.namespace, self.service_name)
        assert delete_result.status_code == 204, "删除内部路由失败：{}".format(delete_result.text)
        assert self.service.check_exists(self.service.get_common_service_url(self.namespace, self.service_name), 404)
        assert result['flag'], result
