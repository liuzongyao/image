import pytest

from test_case.ingress.ingress import Ingress


@pytest.mark.ingress
@pytest.mark.ace
class TestIngressSuite(object):
    def setup_class(self):
        self.ingress = Ingress()
        self.ingress_name = 'ingress-{}'.format(self.ingress.region_name).replace('_', '-')
        self.k8s_namespace = self.ingress.global_info["$K8S_NAMESPACE"]
        self.teardown_class(self)

    def teardown_class(self):
        self.ingress.delete_ingress(self.k8s_namespace, self.ingress_name)

    @pytest.mark.BAT
    def test_ingress(self):
        '''
        创建外部路由-外部路由列表-获取详情-更新外部路由-搜索外部路由-删除外部路由
        :return:
        '''
        result = {"flag": True}
        # create ingress
        createingress_result = self.ingress.create_ingress("./test_data/ingress/ingress.json",
                                                           {"$ingress_name": self.ingress_name})
        assert createingress_result.status_code == 201, "创建外部路由失败:{}".format(createingress_result.text)

        # list ingress
        list_result = self.ingress.list_ingress(self.k8s_namespace)
        result = self.ingress.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.ingress.update_result(result, self.ingress_name in list_result.text, "外部路由列表：新建外部路由不在列表中")

        # get ingress detail
        detail_result = self.ingress.get_ingress_detail(self.k8s_namespace, self.ingress_name)
        result = self.ingress.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.ingress.update_result(result, self.ingress.get_value(detail_result.json(),
                                                                           "kubernetes-metadata-annotations-kubernetes.io/ingress.class",
                                                                           '-') == 'erroringress',
                                            "访问控制器不是erroringress {}".format(detail_result.text))

        # update ingress
        update_result = self.ingress.update_ingress(self.k8s_namespace, self.ingress_name,
                                                    "./test_data/ingress/update-ingress.json",
                                                    {"$ingress_name": self.ingress_name})
        assert update_result.status_code == 204, "更新外部路由出错:{}".format(update_result.text)

        # search ingress
        search_result = self.ingress.search_ingress(self.k8s_namespace, self.ingress_name)
        result = self.ingress.update_result(result, search_result.status_code == 200, search_result.text)
        result = self.ingress.update_result(result, len(search_result.json()) == 1, search_result.text)
        result = self.ingress.update_result(result, len(search_result.json()[0]['kubernetes']['spec']['rules']) == 2,
                                            search_result.text)
        result = self.ingress.update_result(result,
                                            search_result.json()[0]['kubernetes']['spec']['tls'][0][
                                                'secretName'] == 'errorsecret',
                                            "https证书不是errorsecret")

        # delete ingress
        delete_result = self.ingress.delete_ingress(self.k8s_namespace, self.ingress_name)
        assert delete_result.status_code == 204, "删除外部路由失败：{}".format(delete_result.text)
        assert self.ingress.check_exists(self.ingress.get_common_ingress_url(self.k8s_namespace, self.ingress_name), 404)
        assert result['flag'], result
