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

    def teardown_class(self):
        self.loadbalancer.delete_lb(self.lb_name)

    def test_lb(self):
        """
        创建(导入)lb-获取lb列表-删除新创建lb-添加自定义域名后缀-查看lb详情自定义域名-添加挂ha服务-获取服务域名(包括默认域名)-验证服务能够访问
        -不使用默认域名-获取lb域名信息-验证ha地址不能访问-删除域名后缀-域名后缀地址不能访问-删除域名后地址减少-删除服务
        :return:
        """
        result = {"flag": True}
        self.loadbalancer.delete_lb(self.lb_name)
        ret_create = self.loadbalancer.create_lb("./test_data/loadbalancers/lb.json",
                                                 {"$LB_NAME": self.lb_name, "$create_type": self.create_type,
                                                  "$type": self.type, "$address_type": self.address_type})
        assert ret_create.status_code == 201, "创建lb出错:{}".format(ret_create.text)
        lb_id = ret_create.json("load_balancer_id")

        # check lb_list
        ret_list_lb = self.loadbalancer.get_list_lb()
        result = self.loadbalancer.update_result(result, ret_list_lb.status_code == 200, '获取lb列表出错')
        result = self.loadbalancer.update_result(result, self.lb_name in ret_list_lb.text, '获取lb列表：新建lb不在列表内')

        # check lb event
        ret_event = self.loadbalancer.get_lb_events(lb_id, 'create')
        result = self.loadbalancer.update_result(result, ret_event, '操作事件：获取lb创建事件出错')

        # delete lb
        ret_detele_lb = self.loadbalancer.delete_lb(self.lb_name)
        assert ret_detele_lb.status_code == 204, ret_detele_lb.text
        assert result["flag"], "delete lb result is {}".format(result)

        # update lb_dns
        ret_update_dns = self.loadbalancer.update_lb_dns("./test_data/loadbalances/update_dns",
                                                         {"$dns_name": self.dns_name})
        assert ret_update_dns.status_code == 204, "更新lb_dns失败：{}".format(ret_update_dns.text)

        # check lb detail
        ret_detail = self.loadbalancer.get_lb_detail(lb_id)
        domin_info = json.loads(ret_detail.text)["domain_info"]
        result = self.loadbalancer.update_result(result, ret_detail.status_code == 200, '获取lb_detail详情出错')
        result = self.loadbalancer.update_result(result, self.dns_name in domin_info, '获取lb详情：期望存在自定义域名后缀')

        # update app
        ret_updateapp = get
