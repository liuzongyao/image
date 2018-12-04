import pytest

from test_case.networkpolicy.networkpolicy import Networkpolicy
from test_case.newapp.newapp import Newapplication


@pytest.mark.networkpolicy
@pytest.mark.ace
class TestNetworkpolicySuite(object):
    def setup_class(self):
        self.networkpolicy = Networkpolicy()
        self.networkpolicy_name = 'networkpolicy-{}'.format(self.networkpolicy.region_name).replace('_', '-')
        self.k8s_namespace = self.networkpolicy.global_info["$K8S_NAMESPACE"]
        self.newapp = Newapplication()
        self.newapp_name = self.networkpolicy.global_info["$GLOBAL_APP_NAME"]
        self.teardown_class(self)

    def teardown_class(self):
        self.networkpolicy.delete_networkpolicy(self.k8s_namespace, self.networkpolicy_name)

    @pytest.mark.BAT
    def test_networkpolicy(self):
        '''
        创建网络策略-网络策略列表-更新网络策略-获取详情-删除网络策略
        :return:
        '''
        if self.networkpolicy.global_info["$NETWORK_POLICY"] != "calico":
            return True, "网络策略不是calico,不需要测试"
        result = {"flag": True}
        # create networkpolicy
        createnetworkpolicy_result = self.networkpolicy.create_networkpolicy(
            "./test_data/networkpolicy/networkpolicy.json",
            {"$networkpolicy_name": self.networkpolicy_name})
        assert createnetworkpolicy_result.status_code == 201, "创建网络策略失败:{}".format(createnetworkpolicy_result.text)

        # list networkpolicy
        list_result = self.networkpolicy.list_networkpolicy()
        result = self.networkpolicy.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.networkpolicy.update_result(result, self.networkpolicy_name in list_result.text,
                                                  "网络策略列表：新建网络策略不在列表中")

        # update networkpolicy
        update_result = self.networkpolicy.update_networkpolicy(self.k8s_namespace, self.networkpolicy_name,
                                                                "./test_data/networkpolicy/update-networkpolicy.json",
                                                                {"$networkpolicy_name": self.networkpolicy_name})
        assert update_result.status_code == 204, "更新网络策略出错:{}".format(update_result.text)

        # get networkpolicy detail
        detail_result = self.networkpolicy.get_networkpolicy_detail(self.k8s_namespace, self.networkpolicy_name)
        result = self.networkpolicy.update_result(result, detail_result.status_code == 200, detail_result.text)

        # delete networkpolicy
        delete_result = self.networkpolicy.delete_networkpolicy(self.k8s_namespace, self.networkpolicy_name)
        assert delete_result.status_code == 204, "删除网络策略失败：{}".format(delete_result.text)
        assert self.networkpolicy.check_exists(
            self.networkpolicy.get_common_networkpolicy_url(self.k8s_namespace, self.networkpolicy_name), 404)
        assert result['flag'], result
