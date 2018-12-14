import pytest

from test_case.alb.alb import Alb
from test_case.newapp.newapp import Newapplication


@pytest.mark.alb
@pytest.mark.ace
class TestAlbSuite(object):
    def setup_class(self):
        self.alb = Alb()
        self.alb2_name = 'nginx-{}'.format(self.alb.region_name).replace('_', '-')
        self.k8s_namespace = self.alb.global_info["$K8S_NAMESPACE"]
        list_result = self.alb.list_alb()
        assert list_result.status_code == 200, "获取负载均衡列表失败 {}".format(list_result.text)
        if len(list_result.json()) == 0:
            return True, "集群负载均衡列表为空，请先部署alb2"
        self.alb_name = list_result.json()[-1]['kubernetes']['metadata']['name']
        self.alb_namespace = list_result.json()[-1]['kubernetes']['metadata']['namespace']
        self.tcpportname = "{}-999".format(self.alb_name)
        self.httpportname = "{}-777-http".format(self.alb_name)
        self.rulename = "rule-{}".format(self.httpportname)
        self.newapp = Newapplication()
        self.teardown_class(self)

    def teardown_class(self):
        self.alb.delete_rule(self.alb_namespace, self.rulename)
        self.alb.delete_frontend(self.alb_namespace, self.tcpportname)
        self.alb.delete_frontend(self.alb_namespace, self.httpportname)
        self.alb.delete_alb(self.k8s_namespace, self.alb2_name)

    @pytest.mark.BAT
    def test_alb(self):
        '''
        创建tcp端口-获取tcp端口详情-设置默认内部路由-获取应用访问地址-获取端口列表-删除tcp端口-
        创建http端口-创建规则-获取应用访问地址-获取规则详情-更新规则-获取规则列表-删除规则-删除http端口
        :return:
        '''
        crd_result = self.alb.get_alb_crd()
        assert crd_result.status_code == 200, "获取alb2的crd 失败:{}".format(crd_result.text)
        if len(crd_result.json()) == 0:
            return True, "集群不支持alb2,请先部署alb2"
        result = {"flag": True}

        # create tcp frontend
        tcp_result = self.alb.create_frontend("./test_data/alb2/frontend-tcp.json",
                                              {"$alb_name": self.alb_name, "$alb-namespace": self.alb_namespace
                                               })
        assert tcp_result.status_code == 201, "创建tcp监听端口失败:{}".format(tcp_result.text)

        # get frontend detail
        frontend_result = self.alb.get_detail_frontend(self.alb_namespace, self.tcpportname)
        result = self.alb.update_result(result, frontend_result.status_code == 200, frontend_result.text)
        version = frontend_result.json()['kubernetes']['metadata']['resourceVersion']

        # update tcp frontend
        update_frontend_result = self.alb.update_frontend(self.alb_namespace, self.tcpportname,
                                                          "./test_data/alb2/update-frontend-tcp.json",
                                                          {"$alb_name": self.alb_name,
                                                           "$alb-namespace": self.alb_namespace,
                                                           "$resourceVersion": version})
        assert update_frontend_result.status_code == 204, "更新tcp默认内部路由失败:{}".format(update_frontend_result.text)

        # get app address
        address_result = self.newapp.get_newapp_address(self.k8s_namespace, self.newapp.global_info['$GLOBAL_APP_NAME'])
        result = self.alb.update_result(result, self.tcpportname in address_result.text,
                                        "更新tcp默认内部路由,获取应用地址失败 {}".format(address_result.text))

        # list frontend
        frontend_result = self.alb.list_frontend(self.alb_namespace, self.alb_name)
        result = self.alb.update_result(result, frontend_result.status_code == 200, frontend_result.text)
        result = self.alb.update_result(result, len(frontend_result.json()) > 0, frontend_result.text)

        # delete tcp frontend
        delete_result = self.alb.delete_frontend(self.alb_namespace, self.tcpportname)
        assert delete_result.status_code == 204, "删除tcp端口失败：{}".format(delete_result.text)
        assert self.alb.check_exists(self.alb.common_frontend_url(self.alb_namespace, self.tcpportname), 404, params={})

        # create http frontend
        http_result = self.alb.create_frontend("./test_data/alb2/frontend-http.json",
                                               {"$alb_name": self.alb_name, "$alb-namespace": self.alb_namespace
                                                })
        assert http_result.status_code == 201, "创建http监听端口失败:{}".format(http_result.text)

        # create rule
        create_rule_result = self.alb.create_rule("./test_data/alb2/rule.json",
                                                  {"$rule_name": self.rulename, "$alb_name": self.alb_name,
                                                   "$alb-namespace": self.alb_namespace})
        assert create_rule_result.status_code == 201, "创建规则失败:{}".format(create_rule_result.text)

        # get app address
        address_result = self.newapp.get_newapp_address(self.k8s_namespace, self.newapp.global_info['$GLOBAL_APP_NAME'])
        result = self.alb.update_result(result, address_result.status_code == 200, address_result.text)
        result = self.alb.update_result(result, self.rulename in address_result.text,
                                        "添加http规则后,获取应用地址失败 {}".format(address_result.text))

        # detail rule
        detail_rule_result = self.alb.detail_rule(self.alb_namespace, self.rulename)
        assert detail_rule_result.status_code == 200, "获取规则详情失败 {}".format(detail_rule_result.text)
        version = detail_rule_result.json()['kubernetes']['metadata']['resourceVersion']

        # update rule
        update_rule_result = self.alb.update_rule(self.alb_namespace, self.rulename,
                                                  "./test_data/alb2/update-rule.json",
                                                  {"$rule_name": self.rulename, "$alb_name": self.alb_name,
                                                   "$alb-namespace": self.alb_namespace, "$resourceVersion": version})
        assert update_rule_result.status_code == 204, "更新规则失败:{}".format(update_rule_result.text)

        # list rule
        list_rule_result = self.alb.list_rule(self.alb_namespace, self.alb_name, self.httpportname)
        result = self.alb.update_result(result, list_rule_result.status_code == 200, list_rule_result.text)
        result = self.alb.update_result(result, len(list_rule_result.json()) > 0, list_rule_result.text)

        # delete rule
        delete_rule_result = self.alb.delete_rule(self.alb_namespace, self.rulename)
        assert delete_rule_result.status_code == 204, "删除规则失败：{}".format(delete_rule_result.text)
        assert self.alb.check_exists(self.alb.common_rule_url(self.alb_namespace, self.rulename), 404, params={})

        # delete http frontend
        delete_result = self.alb.delete_frontend(self.alb_namespace, self.httpportname)
        assert delete_result.status_code == 204, "删除http端口失败：{}".format(delete_result.text)
        assert self.alb.check_exists(self.alb.common_frontend_url(self.alb_namespace, self.httpportname), 404,
                                     params={})
        assert result['flag'], result

    def test_alb2(self):
        '''
        创建负载均衡-负载均衡列表-更新域名后缀-获取负载均衡详情-删除负载均衡
        :return:
        '''
        crd_result = self.alb.get_alb_crd()
        assert crd_result.status_code == 200, "获取alb2的crd 失败:{}".format(crd_result.text)
        if len(crd_result.json()) == 0:
            return True, "集群不支持alb2,请先部署alb2"
        result = {"flag": True}
        # create alb
        masterip = self.alb.global_info['$MASTERIPS'].split(",")[0]
        createalb_result = self.alb.create_alb("./test_data/alb2/alb2.json",
                                               {"$alb_name": self.alb2_name, "$address": masterip})
        assert createalb_result.status_code == 201, "创建负载均衡失败:{}".format(createalb_result.text)

        # list alb
        list_result = self.alb.list_alb()
        result = self.alb.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.alb.update_result(result, self.alb2_name in list_result.text, "负载均衡列表：新建负载均衡不在列表中")

        # detail alb
        detail_result = self.alb.get_alb_detail(self.k8s_namespace, self.alb2_name)
        result = self.alb.update_result(result, detail_result.status_code == 200, detail_result.text)
        version = detail_result.json()['kubernetes']['metadata']['resourceVersion']

        # update alb
        update_result = self.alb.update_alb(self.k8s_namespace, self.alb2_name, "./test_data/alb2/update-alb2.json",
                                            {"$alb_name": self.alb2_name, "$address": masterip,
                                             "$resourceVersion": version})
        assert update_result.status_code == 204, "更新域名后缀失败:{}".format(update_result.text)

        # detail alb
        detail_result = self.alb.get_alb_detail(self.k8s_namespace, self.alb2_name)
        result = self.alb.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.alb.update_result(result,
                                        self.alb.get_value(detail_result.json(), 'kubernetes.spec.address') == masterip,
                                        detail_result.text)
        result = self.alb.update_result(result,
                                        len(self.alb.get_value(detail_result.json(), 'kubernetes.spec.domains')) == 2,
                                        detail_result.text)
        # delete alb
        delete_result = self.alb.delete_alb(self.k8s_namespace, self.alb2_name)
        assert delete_result.status_code == 204, "删除负载均衡失败：{}".format(delete_result.text)
        assert self.alb.check_exists(self.alb.get_common_alb_url(self.k8s_namespace, self.alb2_name), 404, params={})
        assert result['flag'], result
