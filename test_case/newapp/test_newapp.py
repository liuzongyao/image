import pytest
import time

from test_case.newapp.newapp import Newapplication


@pytest.mark.newapp
@pytest.mark.ace
class TestNewApplicationSuite(object):
    def setup_class(self):
        self.newapp = Newapplication()
        self.namespace = self.newapp.global_info["$K8S_NAMESPACE"]
        self.newapp_name = 'alauda-newapp'
        self.teardown_class(self)

    def teardown_class(self):
        self.newapp.delete_newapp(self.namespace, self.newapp_name)

    @pytest.mark.BAT
    def test_newapp(self):
        # if not self.newapp.is_weblab_open("USER_VIEW_ENABLED"):
        #     return True, "用户视角未打开，不需要测试"
        """
        创建应用-获取拓扑图-获取容器组-获取yaml-获取日志-获取事件-获取k8s事件-exec-获取全部应用-获取命名空间下的应用-搜索应用-
        更新应用-获取应用yaml-缩容-扩容-删除应用下的资源-获取应用详情-添加资源到应用-停止应用-启动应用-删除组件-删除应用
        """
        # 创建应用
        result = {"flag": True}
        create_result = self.newapp.create_newapp('./test_data/newapp/appcore.json', {'$newapp_name': self.newapp_name})
        assert create_result.status_code == 201, "新版应用创建失败 {}".format(create_result.text)
        app_uuid = self.newapp.get_value(create_result.json(), '0.kubernetes.metadata.uid')

        # 获取应用状态
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        assert app_status, "创建应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 获取拓扑图
        topology_result = self.newapp.get_newapp_topology(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, topology_result.status_code == 200, "获取拓扑图失败")
        result = self.newapp.update_result(result, len(topology_result.json().get('referenced_by')) == 2, "拓扑图关联错误")

        # 获取容器组
        pod_result = self.newapp.get_newapp_pods(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, pod_result.status_code == 200, "获取容器组失败")
        result = self.newapp.update_result(result, len(pod_result.json()) == 1,
                                           "容器组不是1 {}".format(len(pod_result.json())))
        container_name = self.newapp.get_value(pod_result.json(), '0.kubernetes.metadata.name')

        # 获取yaml
        yaml_result = self.newapp.get_newapp_yaml(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, yaml_result.status_code == 200, "创建应用后，yaml失败")
        result = self.newapp.update_result(result, 'Application' in yaml_result.text, "创建应用后，yaml失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in yaml_result.text, "创建应用后，yaml失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in yaml_result.text,
                                           "创建应用后，yaml失败:HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in yaml_result.text, "创建应用后，yaml失败:不存在Service")

        # 获取日志
        log_result = self.newapp.get_newapp_log(self.namespace, self.newapp_name, container_name)
        result = self.newapp.update_result(result, log_result.status_code == 200, "获取日志失败")
        result = self.newapp.update_result(result, len(log_result.json()['logs']) > 0, "获取日志为空")

        # 获取事件
        event_result = self.newapp.get_newapp_event(app_uuid)
        result = self.newapp.update_result(result, event_result.status_code == 200, "获取事件失败")
        result = self.newapp.update_result(result, event_result.json().get('total_items') != 0, "获取事件为空")

        # 获取k8s事件
        kevent_result = self.newapp.get_newapp_kevent(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, kevent_result.status_code == 200, "获取k8s事件失败")
        result = self.newapp.update_result(result, kevent_result.json().get('count') != 0, "获取k8s事件为空")

        # exec
        exec_result = self.newapp.exec_newapp(self.namespace, self.newapp_name, container_name)
        result = self.newapp.update_result(result, exec_result.status_code == 200, "exec失败")

        # 获取全部应用
        list_result = self.newapp.get_all_newapp()
        result = self.newapp.update_result(result, list_result.status_code == 200, "获取应用列表失败")
        result = self.newapp.update_result(result, self.newapp_name in list_result.text, "获取应用列表失败:新建应用不在列表中")

        # 获取命名空间下的应用
        namespace_result = self.newapp.get_newapp_in_namespace(self.namespace)
        result = self.newapp.update_result(result, namespace_result.status_code == 200, "获取命名空间下的应用列表失败")
        result = self.newapp.update_result(result, self.newapp_name in namespace_result.text,
                                           "获取命名空间下的应用列表失败:新建应用不在列表中")

        # 按名称搜索应用
        search_result = self.newapp.search_newapp(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, search_result.status_code == 200, "按名称搜索应用失败")
        result = self.newapp.update_result(result, self.newapp_name in search_result.text,
                                           "按名称搜索应用失败:新建应用不在列表中")

        # 更新应用,个数为2，添加ClusterRole
        update_result = self.newapp.update_newapp(self.namespace, self.newapp_name,
                                                  './test_data/newapp/update_appcore.json',
                                                  {'$newapp_name': self.newapp_name})
        assert update_result.status_code == 200, "更新应用失败 {}".format(update_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        assert app_status, "更新应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 获取应用yaml
        yaml_result = self.newapp.get_newapp_yaml(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, yaml_result.status_code == 200, "更新应用后，yaml失败")
        result = self.newapp.update_result(result, 'Application' in yaml_result.text, "更新应用后，yaml失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in yaml_result.text, "更新应用后，yaml失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in yaml_result.text,
                                           "更新应用后，yaml失败:HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in yaml_result.text, "更新应用后，yaml失败:不存在Service")
        result = self.newapp.update_result(result, 'ClusterRole' in yaml_result.text, "更新应用后，yaml失败:不存在ClusterRole")
        result = self.newapp.update_result(result, '15222222222' in yaml_result.text, "更新应用后，owners未更新")

        # 缩容
        scale_down_result = self.newapp.scale_down_newapp(self.namespace, self.newapp_name)
        assert scale_down_result.status_code == 204, "缩容失败 {}".format(scale_down_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        assert app_status, "缩容后，验证应用状态出错：app: {} is not running".format(self.newapp_name)
        flag = self.newapp.get_status(self.newapp.get_newapp_status_url(self.namespace, self.newapp_name),
                                      'workloads.Deployment-{}.desired'.format(self.newapp_name), 1)
        assert flag, "缩容后，预期个数不是1"

        # 扩容
        scale_up_result = self.newapp.scale_up_newapp(self.namespace, self.newapp_name)
        assert scale_up_result.status_code == 204, "扩容失败 {}".format(scale_up_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        assert app_status, "扩容后，验证应用状态出错：app: {} is not running".format(self.newapp_name)
        flag = self.newapp.get_status(self.newapp.get_newapp_status_url(self.namespace, self.newapp_name),
                                      'workloads.Deployment-{}.desired'.format(self.newapp_name), 2)
        assert flag, "扩容后，预期个数不是2"
        
        # 删除应用下的资源ClusterRole
        remove_result = self.newapp.remove_resource_newapp(self.namespace, self.newapp_name,
                                                           './test_data/newapp/resource.json',
                                                           {'$newapp_name': self.newapp_name})
        assert remove_result.status_code == 204, "删除应用下的资源失败 {}".format(remove_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        assert app_status, "删除应用下的资源后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 获取应用详情
        detail_result = self.newapp.get_newapp_detail(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, detail_result.status_code == 200, "获取应用详情失败")
        result = self.newapp.update_result(result, 'Application' in detail_result.text, "删除应用下的资源详情失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in detail_result.text, "删除应用下的资源详情失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in detail_result.text,
                                           "删除应用下的资源详情失败:不存在HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in detail_result.text, "删除应用下的资源详情失败:存在Service")
        result = self.newapp.update_result(result, 'ClusterRole' not in detail_result.text,
                                           "删除应用下的资源详情失败:存在ClusterRole")

        # 添加资源ClusterRole到应用
        add_result = self.newapp.add_resource_newapp(self.namespace, self.newapp_name,
                                                     './test_data/newapp/resource.json',
                                                     {'$newapp_name': self.newapp_name})
        assert add_result.status_code == 204, "添加资源到应用失败 {}".format(remove_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        assert app_status, "添加资源到应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)
        detail_result = self.newapp.get_newapp_detail(self.namespace, self.newapp_name)
        result = self.newapp.update_result(result, detail_result.status_code == 200, "获取应用详情失败")
        result = self.newapp.update_result(result, 'Application' in detail_result.text, "添加资源到应用详情失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in detail_result.text, "添加资源到应用详情失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in detail_result.text,
                                           "删除应用下的资源详情失败:不存在HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in detail_result.text, "添加资源到应用详情失败:不存在Service")
        result = self.newapp.update_result(result, 'ClusterRole' in detail_result.text,
                                           "添加资源到应用详情失败:不存在ClusterRole")

        # 停止应用
        stop_result = self.newapp.stop_newapp(self.namespace, self.newapp_name)
        assert stop_result.status_code == 204, "停止应用失败 {}".format(stop_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Stopped')
        assert app_status, "停止应用后，验证应用状态出错：app: {} is running".format(self.newapp_name)

        # 开始应用 有bug,暂时注释掉http://jira.alaudatech.com/browse/DEV-12803
        # start_result = self.newapp.start_newapp(self.namespace, self.newapp_name)
        # assert start_result.status_code == 204, "启动应用失败 {}".format(start_result.text)
        # app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Running')
        # assert app_status, "启动应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 删除组件
        deploy_result = self.newapp.delete_deployment(self.namespace, self.newapp_name)
        assert deploy_result.status_code == 204, "删除组件失败 {}".format(deploy_result.text)
        app_status = self.newapp.get_newapp_status(self.namespace, self.newapp_name, 'Empty')
        assert app_status, "删除组件后，验证应用状态出错：app: {} is not Empty".format(self.newapp_name)

        # 删除应用
        delete_result = self.newapp.delete_newapp(self.namespace, self.newapp_name)
        assert delete_result.status_code == 204, "删除应用失败 {}".format(delete_result.text)
        delete_flag = self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.newapp_name), 404)
        assert delete_flag, "删除应用失败"
        assert result['flag'], result
