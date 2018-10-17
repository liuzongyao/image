import json
from test_case.loadbalancers.lb import LoadBalancer


class TestLoadBalancer(object):
    def setup_class(self):
        self.loadbalancer = LoadBalancer()
        self.lb_name = 'alauda-lb-{}'.format(self.loadbalancer.region_name).replace('_', '-')
        self.create_type = "import"
        self.type = "haproxy"
        self.address_type = "internal"
        self.dns_name = "alauda-dns-{}".format(self.loadbalancer.region_name).replace('_', '-')
        self.app_id = self.loadbalancer.global_info['$GLOBAL_APP_ID']
        self.ha_name = self.loadbalancer.get_lb_name()

    def teardown_class(self):
        self.loadbalancer.delete_lb(self.lb_name)

    def test_lb(self):
        """
        创建(导入)lb-获取lb列表-删除新创建lb-添加自定义域名后缀-查看lb详情自定义域名-添加挂ha服务-获取服务域名(包括默认域名)-验证服务能够访问
        -不使用默认域名-获取lb域名信息-验证ha地址不能访问-删除域名后缀-域名后缀地址不能访问-删除域名后地址减少
        :return:
        """
        global default_domain_url, dns_domain_url
        result = {"flag": True}
        self.loadbalancer.delete_lb(self.lb_name)
        ret_create = self.loadbalancer.create_lb("./test_data/loadbalancers/lb.json",
                                                 {"$LB_NAME": self.lb_name, "$create_type": self.create_type,
                                                  "$type": self.type, "$address_type": self.address_type})
        assert ret_create.status_code == 201, "创建lb出错:{}".format(ret_create.text)
        content = ret_create.json()
        lb_id = self.loadbalancer.get_value(content, "load_balancer_id")

        # check lb_list
        ret_list_lb = self.loadbalancer.get_list_lb()
        result = self.loadbalancer.update_result(result, ret_list_lb.status_code == 200, '获取lb列表出错')
        result = self.loadbalancer.update_result(result, self.lb_name in ret_list_lb.text, '获取lb列表：新建lb不在列表内')

        # check lb event
        ret_event = self.loadbalancer.get_lb_events(lb_id, 'create')
        result = self.loadbalancer.update_result(result, ret_event, '操作事件：获取lb创建事件出错')

        # delete lb
        ret_detele_lb = self.loadbalancer.delete_lb(self.lb_name)
        assert ret_detele_lb.status_code == 204, "删除lb失败:{}".format(ret_detele_lb.text)
        assert result["flag"], "delete lb result is {}".format(result)

        # update lb_dns
        ret_update_dns = self.loadbalancer.update_lb_dns(self.ha_name, './test_data/loadbalancers/update_dns.json',
                                                         {"$dns_name": self.dns_name, "$tf": False})
        assert ret_update_dns.status_code == 204, "更新lb_dns失败：{}".format(ret_update_dns.text)

        # check lb detail
        ret_lb_detail = self.loadbalancer.get_lb_detail(self.ha_name)
        result = self.loadbalancer.update_result(result, ret_lb_detail.status_code == 200, '获取lb_detail详情出错')
        domin_info = json.loads(ret_lb_detail.text)["domain_info"]
        result = self.loadbalancer.update_result(result, self.dns_name in domin_info, '获取lb详情：期望存在自定义域名后缀')

        # get app lb detail
        ret_app_lbdetail = self.loadbalancer.get_app_lbdetail(self.app_id)
        result = self.loadbalancer.update_result(result, ret_app_lbdetail.status_code == 200, '获取app_lb_detail详情出错')
        content = ret_app_lbdetail.json()
        if len(content) > 0:
            protocol = self.loadbalancer.get_value(content, '0.listeners.0.protocol')
            dns_domain = self.loadbalancer.get_value(content, '0.frontends.0.rules.1.domain')
            default_domain = self.loadbalancer.get_value(content, '0.frontends.0.rules.0.domain')
            result = self.loadbalancer.update_result(result, self.dns_name in dns_domain, '获取app_lb详情:期望存在自定义域名后缀')
            result = self.loadbalancer.update_result(result, self.loadbalancer in default_domain,
                                                     '获取app_lb详情:期望存在默认域名后缀怒')

            # check access service
            dns_domain_url = "{}://{}".format(protocol, dns_domain)
            ret_access_dns = self.loadbalancer.access_service(dns_domain_url, "Hello")
            result = self.loadbalancer.update_result(result, ret_access_dns,
                                                     "访问自定义域名生成的服务地址:({})不可访问，错误:{}".format(dns_domain_url,
                                                                                            ret_access_dns))
            default_domain_url = "{}://{}".format(protocol, default_domain)
            ret_access_default = self.loadbalancer.access_service(default_domain_url, "Hellp")
            result = self.loadbalancer.update_result(result, ret_access_default,
                                                     "访问默认服务地址:({})不可访问，错误:{}".format(default_domain_url,
                                                                                      ret_access_default))
        else:
            result = self.loadbalancer.update_result(result, False, "获取app_lb_detail为空")

        # don't use default and dns domain
        ret_disable_defaule_dns = self.loadbalancer.update_lb_dns(self.ha_name, '/test_data/loadbalances/update_dns',
                                                                  {"$dns_name": "[]", "$true/false": "true"})
        assert ret_disable_defaule_dns.status_code == 204, "更新lb_dns失败：{}".format(ret_disable_defaule_dns)

        # check lb detail
        ret_lb_detail = self.loadbalancer.get_lb_detail(self.ha_name)
        result = self.loadbalancer.update_result(result, ret_lb_detail.status_code == 200, '获取lb_detail详情出错')
        domin_info = self.loadbalancer.get_uuid_accord_name(ret_lb_detail.json().get("domain_info"),
                                                            {"type": "default-domain"},
                                                            "disabled")
        if domin_info is True:
            # 不使用默认域名后，服务的HA地址不能访问
            ret_access_default = self.loadbalancer.access_service(default_domain_url, [503, 404])
            result = self.loadbalancer.update_result(result, ret_access_default, "删除默认域名后，访问默认地址期望返回为503")
            # 不使用自定义域名后缀，服务的自定义域名后缀不能访问
            ret_access_dns = self.loadbalancer.access_service(dns_domain_url, [503, 404])
            result = self.loadbalancer.update_result(result, ret_access_dns, "删除自定义域名后缀，访问自定义地址期望返回为503")
        else:
            result = self.loadbalancer.update_result(result, domin_info, "返回体中域名信息数组默认域名没有被禁用")

        # check num of lb_app
