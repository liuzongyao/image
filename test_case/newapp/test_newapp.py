import pytest
import time

from test_case.configmap.configmap import Configmap
from test_case.newapp.newapp import Newapplication
from test_case.persistentvolumeclaims.pvc import Pvc
from test_case.storageclasses.scs import Scs


@pytest.mark.newapp
@pytest.mark.ace
class TestNewApplicationSuite(object):
    def setup_class(self):
        self.newapp = Newapplication()
        self.k8s_namespace = self.newapp.global_info["$K8S_NAMESPACE"]
        self.newapp_name = 'alauda-newapp'

        self.configmap = Configmap()
        self.configmap_name = 'alauda-cmforapp-{}'.format(self.newapp.region_name).replace('_', '-')
        self.appwithcm_name = 'alauda-appwithcm-{}'.format(self.newapp.region_name).replace('_', '-')

        self.scs = Scs()
        self.scs_name = 'alauda-scsforapp-{}'.format(self.newapp.region_name).replace('_', '-')
        self.pvc = Pvc()
        self.pvc_name = 'alauda-pvcforapp-{}'.format(self.newapp.region_name).replace('_', '-')
        self.appwithpvc_name = 'alauda-appwithpvc-{}'.format(self.newapp.region_name).replace('_', '-')

        self.teardown_class(self)

    def teardown_class(self):
        self.newapp.delete_newapp(self.k8s_namespace, self.newapp_name)
        self.newapp.delete_newapp(self.k8s_namespace, self.appwithcm_name)
        self.newapp.delete_newapp(self.k8s_namespace, self.appwithpvc_name)
        self.configmap.delete_configmap(self.k8s_namespace, self.configmap_name)
        self.pvc.delete_pvc(self.k8s_namespace, self.pvc_name)
        self.scs.delete_scs(self.scs_name)

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
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "创建应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 获取拓扑图
        topology_result = self.newapp.get_newapp_topology(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, topology_result.status_code == 200, "获取拓扑图失败")
        result = self.newapp.update_result(result, len(topology_result.json().get('referenced_by')) == 2, "拓扑图关联错误")

        # 获取容器组
        pod_result = self.newapp.get_newapp_pods(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, pod_result.status_code == 200, "获取容器组失败")
        result = self.newapp.update_result(result, len(pod_result.json()) == 1,
                                           "容器组不是1 {}".format(len(pod_result.json())))
        container_name = self.newapp.get_value(pod_result.json(), '0.kubernetes.metadata.name')

        # 获取yaml
        yaml_result = self.newapp.get_newapp_yaml(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, yaml_result.status_code == 200, "创建应用后，yaml失败")
        result = self.newapp.update_result(result, 'Application' in yaml_result.text, "创建应用后，yaml失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in yaml_result.text, "创建应用后，yaml失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in yaml_result.text,
                                           "创建应用后，yaml失败:HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in yaml_result.text, "创建应用后，yaml失败:不存在Service")

        # 获取日志
        log_result = self.newapp.get_newapp_log(self.k8s_namespace, self.newapp_name, container_name)
        result = self.newapp.update_result(result, log_result.status_code == 200, "获取日志失败")
        result = self.newapp.update_result(result, len(log_result.json()['logs']) > 0, "获取日志为空")

        # 获取事件
        event_result = self.newapp.get_newapp_event(app_uuid)
        result = self.newapp.update_result(result, event_result.status_code == 200, "获取事件失败")
        result = self.newapp.update_result(result, event_result.json().get('total_items') != 0, "获取事件为空")

        # 获取k8s事件
        kevent_result = self.newapp.get_newapp_kevent(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, kevent_result.status_code == 200, "获取k8s事件失败")
        result = self.newapp.update_result(result, kevent_result.json().get('count') != 0, "获取k8s事件为空")

        # exec
        exec_result = self.newapp.exec_newapp(self.k8s_namespace, self.newapp_name, container_name)
        result = self.newapp.update_result(result, exec_result.status_code == 200, "exec失败")

        # 获取全部应用
        list_result = self.newapp.get_all_newapp()
        result = self.newapp.update_result(result, list_result.status_code == 200, "获取应用列表失败")
        result = self.newapp.update_result(result, self.newapp_name in list_result.text, "获取应用列表失败:新建应用不在列表中")

        # 获取命名空间下的应用
        namespace_result = self.newapp.get_newapp_in_namespace(self.k8s_namespace)
        result = self.newapp.update_result(result, namespace_result.status_code == 200, "获取命名空间下的应用列表失败")
        result = self.newapp.update_result(result, self.newapp_name in namespace_result.text,
                                           "获取命名空间下的应用列表失败:新建应用不在列表中")

        # 按名称搜索应用
        search_result = self.newapp.search_newapp(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, search_result.status_code == 200, "按名称搜索应用失败")
        result = self.newapp.update_result(result, self.newapp_name in search_result.text,
                                           "按名称搜索应用失败:新建应用不在列表中")

        # 更新应用,个数为2，添加ClusterRole
        update_result = self.newapp.update_newapp(self.k8s_namespace, self.newapp_name,
                                                  './test_data/newapp/update_appcore.json',
                                                  {'$newapp_name': self.newapp_name})
        assert update_result.status_code == 200, "更新应用失败 {}".format(update_result.text)
        self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Pending')
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "更新应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 获取应用yaml
        yaml_result = self.newapp.get_newapp_yaml(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, yaml_result.status_code == 200, "更新应用后，yaml失败")
        result = self.newapp.update_result(result, 'Application' in yaml_result.text, "更新应用后，yaml失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in yaml_result.text, "更新应用后，yaml失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in yaml_result.text,
                                           "更新应用后，yaml失败:HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in yaml_result.text, "更新应用后，yaml失败:不存在Service")
        result = self.newapp.update_result(result, 'ClusterRole' in yaml_result.text, "更新应用后，yaml失败:不存在ClusterRole")
        result = self.newapp.update_result(result, '15222222222' in yaml_result.text, "更新应用后，owners未更新")

        # 缩容
        scale_down_result = self.newapp.scale_down_newapp(self.k8s_namespace, self.newapp_name)
        assert scale_down_result.status_code == 204, "缩容失败 {}".format(scale_down_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "缩容后，验证应用状态出错：app: {} is not running".format(self.newapp_name)
        flag = self.newapp.get_status(self.newapp.get_newapp_status_url(self.k8s_namespace, self.newapp_name),
                                      'workloads.Deployment-{}.desired'.format(self.newapp_name), 1)
        assert flag, "缩容后，预期个数不是1"

        # 扩容
        scale_up_result = self.newapp.scale_up_newapp(self.k8s_namespace, self.newapp_name)
        assert scale_up_result.status_code == 204, "扩容失败 {}".format(scale_up_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "扩容后，验证应用状态出错：app: {} is not running".format(self.newapp_name)
        flag = self.newapp.get_status(self.newapp.get_newapp_status_url(self.k8s_namespace, self.newapp_name),
                                      'workloads.Deployment-{}.desired'.format(self.newapp_name), 2)
        assert flag, "扩容后，预期个数不是2"

        # 删除应用下的资源ClusterRole
        remove_result = self.newapp.remove_resource_newapp(self.k8s_namespace, self.newapp_name,
                                                           './test_data/newapp/resource.json',
                                                           {'$newapp_name': self.newapp_name})
        assert remove_result.status_code == 204, "删除应用下的资源失败 {}".format(remove_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "删除应用下的资源后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 获取应用详情
        detail_result = self.newapp.get_newapp_detail(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, detail_result.status_code == 200, "获取应用详情失败")
        result = self.newapp.update_result(result, 'Application' in detail_result.text, "删除应用下的资源详情失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in detail_result.text, "删除应用下的资源详情失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in detail_result.text,
                                           "删除应用下的资源详情失败:不存在HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in detail_result.text, "删除应用下的资源详情失败:存在Service")
        result = self.newapp.update_result(result, 'ClusterRole' not in detail_result.text,
                                           "删除应用下的资源详情失败:存在ClusterRole")

        # 添加资源ClusterRole到应用
        add_result = self.newapp.add_resource_newapp(self.k8s_namespace, self.newapp_name,
                                                     './test_data/newapp/resource.json',
                                                     {'$newapp_name': self.newapp_name})
        assert add_result.status_code == 204, "添加资源到应用失败 {}".format(remove_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "添加资源到应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)
        detail_result = self.newapp.get_newapp_detail(self.k8s_namespace, self.newapp_name)
        result = self.newapp.update_result(result, detail_result.status_code == 200, "获取应用详情失败")
        result = self.newapp.update_result(result, 'Application' in detail_result.text, "添加资源到应用详情失败:不存在Application")
        result = self.newapp.update_result(result, 'Deployment' in detail_result.text, "添加资源到应用详情失败:不存在Deployment")
        result = self.newapp.update_result(result, 'HorizontalPodAutoscaler' in detail_result.text,
                                           "删除应用下的资源详情失败:不存在HorizontalPodAutoscaler")
        result = self.newapp.update_result(result, 'Service' in detail_result.text, "添加资源到应用详情失败:不存在Service")
        result = self.newapp.update_result(result, 'ClusterRole' in detail_result.text,
                                           "添加资源到应用详情失败:不存在ClusterRole")

        # 停止应用
        stop_result = self.newapp.stop_newapp(self.k8s_namespace, self.newapp_name)
        assert stop_result.status_code == 204, "停止应用失败 {}".format(stop_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Stopped')
        assert app_status, "停止应用后，验证应用状态出错：app: {} is running".format(self.newapp_name)

        # 开始应用
        start_result = self.newapp.start_newapp(self.k8s_namespace, self.newapp_name)
        assert start_result.status_code == 204, "启动应用失败 {}".format(start_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Running')
        assert app_status, "启动应用后，验证应用状态出错：app: {} is not running".format(self.newapp_name)

        # 删除组件
        deploy_result = self.newapp.delete_deployment(self.k8s_namespace, self.newapp_name)
        assert deploy_result.status_code == 204, "删除组件失败 {}".format(deploy_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.newapp_name, 'Empty')
        assert app_status, "删除组件后，验证应用状态出错：app: {} is not Empty".format(self.newapp_name)

        # 删除应用
        delete_result = self.newapp.delete_newapp(self.k8s_namespace, self.newapp_name)
        assert delete_result.status_code == 204, "删除应用失败 {}".format(delete_result.text)
        delete_flag = self.newapp.check_exists(self.newapp.get_newapp_common_url(self.k8s_namespace, self.newapp_name),
                                               404)
        assert delete_flag, "删除应用失败"
        assert result['flag'], result

    @pytest.mark.cm
    @pytest.mark.BAT
    def test_app_with_cm(self):
        """
        应用使用configmap测试：创建configmap-创建应用-删除应用-删除configmap
        :return:
        """
        result = {"flag": True}
        # create configmap
        createconfigmap_result = self.configmap.create_configmap("./test_data/configmap/configmap.json",
                                                                 {"$cm_name": self.configmap_name,
                                                                  "$cm_key": self.configmap_name})
        assert createconfigmap_result.status_code == 201, "创建cm出错:{}".format(createconfigmap_result.text)

        # create app with cm
        create_result = self.newapp.create_newapp_by_yaml(self.k8s_namespace,
                                                          self.appwithcm_name, './test_data/newapp/daemonset_cm.yml',
                                                          {'$newapp_name': self.appwithcm_name,
                                                           "$cm_name": self.configmap_name,
                                                           "$cm_key": self.configmap_name})
        assert create_result.status_code == 201, "新版应用创建失败 {}".format(create_result.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.appwithcm_name, 'Running')
        assert app_status, "创建使用configmap的应用后，验证应用状态出错：app: {} is not running".format(self.appwithcm_name)
        daemonset_result = self.newapp.get_component(self.k8s_namespace, self.appwithcm_name, 'daemonsets')
        result = self.newapp.update_result(result, daemonset_result.status_code == 200, '获取daemonset详情失败')
        content = daemonset_result.json()
        v1 = self.newapp.get_value(content, 'kubernetes.spec.template.spec.volumes.0.configMap.name')
        result = self.newapp.update_result(result, v1 == self.configmap_name, '存储卷挂载configmap失败')
        v2 = self.newapp.get_value(content, 'kubernetes.spec.template.spec.volumes.1.configMap.name')
        result = self.newapp.update_result(result, v2 == self.configmap_name, '存储卷挂载configmap失败')
        e1 = self.newapp.get_value(content,
                                   'kubernetes.spec.template.spec.containers.0.envFrom.0.configMapRef.name')
        result = self.newapp.update_result(result, e1 == self.configmap_name, '环境变量完整引用configmap失败')
        e2 = ''
        env = self.newapp.get_value(content, 'kubernetes.spec.template.spec.containers.0.env')
        for e in env:
            if e.get('name') == 'cm':
                e2 = self.newapp.get_value(e, 'valueFrom.configMapKeyRef.name')
        result = self.newapp.update_result(result, e2 == self.configmap_name, '环境变量引用configmap的key失败')
        self.newapp.delete_newapp(self.k8s_namespace, self.appwithcm_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.k8s_namespace, self.appwithcm_name), 404)
        self.configmap.delete_configmap(self.k8s_namespace, self.configmap_name)
        assert result['flag'], result

    @pytest.mark.pvc
    def test_app_with_pvc(self):
        """
        应用使用pvc测试：创建sc-创建pvc-创建应用-删除应用-删除pvc-删除sc
        :return:
        """
        result = {"flag": True}
        create_result = self.scs.create_scs("./test_data/scs/scs.yml",
                                            {"$scs_name": self.scs_name, "$is_default": "false",
                                             })
        assert create_result.status_code == 201, "创建sc失败{}".format(create_result.text)

        # create pvc
        createpvc_result = self.pvc.create_pvc("./test_data/pvc/pvc.json",
                                               {"$pvc_name": self.pvc_name, "$pvc_mode": "ReadWriteOnce",
                                                "$scs_name": self.scs_name, "$size": "1"})
        assert createpvc_result.status_code == 201, "创建pvc失败{}".format(createpvc_result.text)
        self.pvc.get_status(self.pvc.get_common_pvc_url(self.pvc.global_info["$K8S_NAMESPACE"], self.pvc_name),
                            "status.phase", "Bound")
        # create app
        create_app = self.newapp.create_newapp_by_yaml(self.k8s_namespace,
                                                       self.appwithpvc_name,
                                                       './test_data/newapp/statefulset_pvc.yml',
                                                       {"$newapp_name": self.appwithpvc_name,
                                                        "$pvc_name": self.pvc_name})
        assert create_app.status_code == 201, "创建app出错:{}".format(create_app.text)
        app_status = self.newapp.get_newapp_status(self.k8s_namespace, self.appwithpvc_name, 'Running')
        assert app_status, "创建使用pvc的应用后，验证应用状态出错：app: {} is not running".format(self.appwithpvc_name)
        statefulset_result = self.newapp.get_component(self.k8s_namespace, self.appwithpvc_name, 'statefulsets')
        result = self.newapp.update_result(result, statefulset_result.status_code == 200, '获取statefulset详情失败')
        claimName = self.newapp.get_value(statefulset_result.json(),
                                          "kubernetes.spec.template.spec.volumes.0.persistentVolumeClaim.claimName")
        result = self.newapp.update_result(result, claimName == self.pvc_name, "详情中挂载pvc失败")

        self.newapp.delete_newapp(self.k8s_namespace, self.appwithpvc_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.k8s_namespace, self.appwithpvc_name), 404)
        time.sleep(60)
        self.pvc.delete_pvc(self.k8s_namespace, self.pvc_name)
        self.scs.delete_scs(self.scs_name)

        assert result['flag'], result
