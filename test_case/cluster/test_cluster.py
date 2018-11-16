import pytest
from test_case.cluster.cluster import Cluster
from test_case.cluster.qcloud import create_instance, destroy_instance, get_instance
from test_case.namespace.namespace import Namespace
from time import sleep


@pytest.mark.cluster
class TestClusterSuite(object):
    def setup_class(self):
        self.cluster = Cluster()
        self.namespace = Namespace()
        self.cluster_name = "e2e-region-test2"
        self.namespace.region_name = self.cluster_name
        ret_create = create_instance(1)
        assert ret_create["success"], ret_create["message"]
        ret_get = get_instance()
        assert ret_get["success"], ret_get["message"]
        self.private_ips = ret_get['private_ips']
        self.public_ips = ret_get['public_ips']
        print(self.private_ips)
        self.teardown_class(self)

    def teardown_class(self):
        self.namespace.delete_general_namespaces("default")
        self.namespace.delete_general_namespaces("kube-system")
        response = self.cluster.delete_cluster(self.cluster_name)
        if response.status_code in (204, 404):
            self.cluster.cleanup_cluster(self.public_ips)
        destroy_instance()

    def test_create_xvlan_region(self):
        """
        获取创建集群脚本-执行脚本-获取集群列表-添加主机节点-安装日志源-安装registry-获取主机列表-获取集群详情-更新主机标签-设置节点调度-
        设置节点不可调度-清理集群资源-删除集群
        """
        result = {"flag": True}
        get_script = self.cluster.generate_install_cmd("test_data/cluster/cluster_cmd.json",
                                                       {"$cluster_name": self.cluster_name,
                                                        "$node_ip": self.private_ips[0]})
        assert get_script.status_code == 200, "获取创建集群脚本失败:{}".format(get_script.text)
        cmd = "yum install -y sshpass;hostname node1;{}".format(get_script.json()["commands"]["install"])
        ret_excute = self.cluster.excute_script(cmd, self.public_ips[0])
        assert "Install successfully!" in ret_excute[1], "执行脚本失败:{}".format(ret_excute[1])
        is_exist = self.cluster.check_value_in_response("v1/regions/{}".format(self.cluster.account),
                                                        self.cluster_name,
                                                        params={})
        assert is_exist, "添加集群超时"

        ret_list = self.cluster.get_region_list()
        result = self.cluster.update_result(result, ret_list.status_code == 200, "获取集群列表失败:{}".format(ret_list.text))
        region_name_list = self.cluster.get_value_list(ret_list.json(), "name")
        assert self.cluster.region_name in region_name_list, "新建集群不在集群列表内"
        region_id = self.cluster.get_uuid_accord_name(ret_list.json(), {"name": self.cluster_name}, "id")
        self.namespace.region_id = region_id

        ret_namespace = self.namespace.list_namespaces()
        assert ret_namespace.status_code == 200, "获取命名空间出错".format(ret_namespace.text)
        # 获取namespace后需要留取时间给krobelus来同步namespace
        sleep(30)
        # 添加节点由于添加接点不会改docker deamon 所以暂时注释：http://jira.alaudatech.com/browse/AKE-44
        # ret_addnode = self.cluster.add_nodes(self.cluster_name, "test_data/cluster/addnode.json",
        #                                      {"$node_ip": self.private_ips[1]})
        # assert ret_addnode.status_code == 204, "添加节点失败:{}".format(ret_addnode.text)
        # is_exist = self.cluster.check_value_in_response(self.cluster.get_node_url(self.cluster_name),
        #                                                 self.private_ips[1],
        #                                                 params={})
        # assert is_exist, "添加节点超时"

        ret_log = self.cluster.install_nevermore(self.cluster_name, "test_data/cluster/install_nevermore.json")
        assert ret_log.status_code == 200, "安装nevermore失败：{}".format(ret_log.text)

        ret_registry = self.cluster.install_registry(self.cluster_name, "test_data/cluster/install_registry.json")
        assert ret_registry.status_code == 200, "安装registry失败：{}".format(ret_registry.text)

        ret_result = self.cluster.check_feature_status(self.cluster_name)
        result = self.cluster.update_result(result, ret_result['success'], "特性安装失败:{}".format(ret_result))

        ret_del_log = self.cluster.uninstall_nevermore(self.cluster_name)
        result = self.cluster.update_result(result, ret_del_log.status_code == 204,
                                            "删除日志特性失败:{}".format(ret_del_log.text))

        ret_del_resgitry = self.cluster.uninstall_registry(self.cluster_name)
        result = self.cluster.update_result(result, ret_del_resgitry.status_code == 204,
                                            "删除registry特性失败:{}".format(ret_del_resgitry.text))

        ret_node = self.cluster.get_node_list(self.cluster_name)
        assert ret_node.status_code == 200, "获取node列表失败:{}".format(ret_node.text)
        node_name = self.cluster.get_value(ret_node.json(), "items.0.metadata.name")
        lables = self.cluster.get_value(ret_node.json(), "items.0.metadata.labels")

        ret_detail = self.cluster.get_region_info(self.cluster_name)
        assert ret_detail.status_code == 200, "获取集群详情失败:{}".format(ret_detail.text)

        lables.update({"e2e": "test"})
        ret_label = self.cluster.update_node_labels(self.cluster_name, node_name, data=lables)
        result = self.cluster.update_result(result, ret_label.status_code == 204, "更新主机标签失败:{}".format(ret_label.text))

        ret_uncordon = self.cluster.uncordon_node(self.cluster_name, node_name)
        assert ret_uncordon.status_code == 204, "设置节点为不可调度失败:{}".format(ret_uncordon.text)
        flag = self.cluster.check_schedulable(self.cluster_name, 0)
        assert not flag, "节点设置为不可调度，但是获取列表还是可以调度"

        # 改成不可调度在马上改成可调度状态会不稳定
        sleep(3)
        ret_cordon = self.cluster.cordon_node(self.cluster_name, node_name)
        assert ret_cordon.status_code == 204, "设置节点为可调度失败:{}".format(ret_cordon.text)
        flag = self.cluster.check_schedulable(self.cluster_name, 0)
        result = self.cluster.update_result(result, flag, "节点设置为可调度，但是获取列表还是不可以调度")

        self.namespace.delete_general_namespaces("default")
        self.namespace.delete_general_namespaces("kube-system")
        ret_delete = self.cluster.delete_cluster(self.cluster_name)
        assert ret_delete.status_code == 204, "删除集群失败:{}".format(ret_delete.text)
        self.cluster.cleanup_cluster(self.public_ips)
        assert result['flag'], result
