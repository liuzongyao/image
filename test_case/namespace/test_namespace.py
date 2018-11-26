import pytest

from backup.application.app import Application
from test_case.namespace.namespace import Namespace
from test_case.persistentvolumeclaims.pvc import Pvc


class TestNamespaceSuite(object):
    def setup_class(self):
        self.namespace = Namespace()
        self.namespace_name = '{}-alauda-ns-{}'.format(self.namespace.project_name,
                                                       self.namespace.region_name).replace('_', '-')
        self.resourcequota_name = 'alauda-quota-{}'.format(self.namespace.region_name).replace('_', '-')
        self.pvc = Pvc()
        self.pvc_name = 'alauda-pvcforquota-{}'.format(self.namespace.region_name).replace('_', '-')
        self.nsforquota_name = 'alauda-nsforquota-{}'.format(self.namespace.region_name).replace('_', '-')
        self.application = Application()
        self.app_name = 'alauda-appforquota-{}'.format(self.namespace.region_name).replace('_', '-')
        self.general_namespace_name = "{}-alauda-gens-{}".format(self.namespace.project_name,
                                                                 self.namespace.region_name).replace('_', '-')

        self.teardown_class(self)

    def teardown_class(self):
        self.pvc.delete_pvc(self.namespace_name, self.pvc_name)
        self.namespace.delete_resourcequota(self.namespace_name, self.resourcequota_name)
        self.namespace.delete_namespaces(self.namespace_name)
        self.application.delete_app(self.app_name)
        self.namespace.delete_namespaces(self.nsforquota_name)
        self.namespace.delete_general_namespaces(self.general_namespace_name)

    @pytest.mark.BAT
    def test_namespace(self):
        '''
        创建命名空间-获取命名空间列表-获取命名空间详情-创建配额-获取配额列表-验证配额pvc-更新配额-验证配额pvc-获取配额详情-删除配额-删除命名空间
        '''
        result = {"flag": True}
        create_ns_result = self.namespace.create_namespaces('./test_data/namespace/namespace.yml',
                                                            {'$K8S_NAMESPACE': self.namespace_name})
        assert create_ns_result.status_code == 201, "创建命名空间失败 {}".format(create_ns_result.text)
        list_ns_result = self.namespace.list_namespaces()
        result = self.namespace.update_result(result, list_ns_result.status_code == 200, '获取命名空间列表失败')
        result = self.namespace.update_result(result, self.namespace_name in list_ns_result.text, '获取命名空间列表失败:新建的不在列表中')
        detail_ns_result = self.namespace.get_namespaces(self.namespace_name)
        result = self.namespace.update_result(result, detail_ns_result.status_code == 200, '获取命名空间详情失败')
        result = self.namespace.update_result(result, self.namespace.get_value(detail_ns_result.json(),
                                                                               'kubernetes.status.phase') == 'Active',
                                              '获取命名空间详情失败:状态不是运行中')
        create_rq_result = self.namespace.create_resourcequota('./test_data/namespace/resourcequota.json',
                                                               {"$resourcequota_name": self.resourcequota_name,
                                                                "$namespace_name": self.namespace_name,
                                                                '"$pod_size"': '0'})
        assert create_rq_result.status_code == 201, "创建配额失败 {}".format(create_rq_result.text)
        list_rq_result = self.namespace.list_resourcequota(self.namespace_name)
        result = self.namespace.update_result(result, list_rq_result.status_code == 200, '获取命名空间下的配额列表失败')
        result = self.namespace.update_result(result, self.resourcequota_name in list_rq_result.text,
                                              '获取命名空间下的配额列表失败:新建的不在列表中')
        create_pvc_result = self.pvc.create_pvc("./test_data/pvc/pvc.json",
                                                {"$pvc_name": self.pvc_name, "$pvc_mode": "ReadWriteOnce",
                                                 "$scs_name": "", "$size": "1", "$K8S_NAMESPACE": self.namespace_name})
        assert create_pvc_result.status_code == 403, "超出配额后,应该不能创建pvc"
        update_rq_result = self.namespace.update_resourcequota(self.namespace_name, self.resourcequota_name,
                                                               './test_data/namespace/resourcequota.json',
                                                               {"$resourcequota_name": self.resourcequota_name,
                                                                "$namespace_name": self.namespace_name,
                                                                '"$pod_size"': '1'})
        assert update_rq_result.status_code == 204, "更新配额失败 {}".format(update_rq_result.text)
        create_pvc_result = self.pvc.create_pvc("./test_data/pvc/pvc.json",
                                                {"$pvc_name": self.pvc_name, "$pvc_mode": "ReadWriteOnce",
                                                 "$scs_name": "", "$size": "1", "$K8S_NAMESPACE": self.namespace_name})
        assert create_pvc_result.status_code == 201, "配额内,应该能创建pvc"
        self.namespace.get_status(self.namespace.get_resourcequota_url(self.namespace_name, self.resourcequota_name),
                                  'kubernetes.status.used.persistentvolumeclaims', '1')
        detail_rq_result = self.namespace.detail_resourcequota(self.namespace_name, self.resourcequota_name)
        result = self.namespace.update_result(result, detail_rq_result.status_code == 200, '获取配额详情失败')
        used = self.namespace.get_value(detail_rq_result.json(), 'kubernetes.status.used.persistentvolumeclaims')
        result = self.namespace.update_result(result, used == '1', '获取配额详情失败:已使用的pvc数不是1 而是{}'.format(used))

        delete_rq_result = self.namespace.delete_resourcequota(self.namespace_name, self.resourcequota_name)
        assert delete_rq_result.status_code == 204, "删除配额失败 {}".format(delete_rq_result.text)
        delete_flag = self.namespace.check_exists(
            self.namespace.get_resourcequota_url(self.namespace_name, self.resourcequota_name), 404)
        assert delete_flag, "删除配额失败"
        delete_ns_result = self.namespace.delete_namespaces(self.namespace_name)
        assert delete_ns_result.status_code == 204, "删除命名空间失败 {}".format(delete_ns_result.text)
        delete_flag = self.namespace.check_exists(self.namespace.get_namespace_url(self.namespace_name), 404)
        assert delete_flag, "删除命名空间失败"

        assert result['flag'], result

    @pytest.mark.BAT
    def test_resourcequota(self):
        '''
        创建命名空间-创建配额-验证配额pod-更新配额-验证配额pod-查看命名空间下的资源-删除有资源的命名空间-删除配额-删除应用-删除命名空间
        '''
        result = {"flag": True}
        create_ns_result = self.namespace.create_namespaces('./test_data/namespace/namespace.yml',
                                                            {'$K8S_NAMESPACE': self.nsforquota_name})
        assert create_ns_result.status_code == 201, "创建命名空间失败 {}".format(create_ns_result.text)
        namespace_id = self.namespace.get_value(create_ns_result.json(), '0.kubernetes.metadata.uid')
        create_rq_result = self.namespace.create_resourcequota('./test_data/namespace/resourcequota.json',
                                                               {"$resourcequota_name": self.resourcequota_name,
                                                                "$namespace_name": self.nsforquota_name,
                                                                '"$pod_size"': '0'})
        assert create_rq_result.status_code == 201, "创建配额失败 {}".format(create_rq_result.text)
        create_app_result = self.application.create_app('./test_data/application/create_app.yml',
                                                        {"$app_name": self.app_name, "$description": self.app_name,
                                                         "$K8S_NAMESPACE": self.nsforquota_name,
                                                         "$K8S_NS_UUID": namespace_id})
        assert create_app_result.status_code == 201, "超出配额后，创建应用失败"
        app_id = self.application.get_value(create_app_result.json(), 'resource.uuid')
        app_status = self.application.get_app_status(app_id, 'resource.status', 'Error')
        assert app_status, "超出配额后，应用状态不是error"
        delete_app_result = self.application.delete_app(self.app_name)
        assert delete_app_result.status_code == 204, "删除应用失败 {}".format(delete_app_result.text)
        delete_flag = self.application.check_exists(self.application.app_common_url(app_id), 404)
        assert delete_flag, "删除应用失败"

        update_rq_result = self.namespace.update_resourcequota(self.nsforquota_name, self.resourcequota_name,
                                                               './test_data/namespace/resourcequota.json',
                                                               {"$resourcequota_name": self.resourcequota_name,
                                                                "$namespace_name": self.nsforquota_name,
                                                                '"$pod_size"': '1'})
        assert update_rq_result.status_code == 204, "更新配额失败 {}".format(update_rq_result.text)
        create_app_result = self.application.create_app('./test_data/application/create_app.yml',
                                                        {"$app_name": self.app_name, "$description": self.app_name,
                                                         "$K8S_NAMESPACE": self.nsforquota_name,
                                                         "$K8S_NS_UUID": namespace_id})
        assert create_app_result.status_code == 201, "配额内，应该可以创建应用"
        app_id = self.application.get_value(create_app_result.json(), 'resource.uuid')
        app_status = self.application.get_app_status(app_id, 'resource.status', 'Running')
        assert app_status, "配额内，应用状态不是running"
        resource_result = self.namespace.get_resource(self.nsforquota_name)
        result = self.namespace.update_result(result, resource_result.status_code == 200, '获取命名空间下的资源列表失败')
        result = self.namespace.update_result(result, self.app_name in resource_result.text,
                                              '获取命名空间下的资源列表失败:新建的应用不在列表中')
        delete_ns_result = self.namespace.delete_namespaces(self.nsforquota_name)
        assert delete_ns_result.status_code == 409, "有资源的命名空间不应该删除成功 {}".format(delete_ns_result.text)
        delete_rq_result = self.namespace.delete_resourcequota(self.nsforquota_name, self.resourcequota_name)
        assert delete_rq_result.status_code == 204, "删除配额失败 {}".format(delete_rq_result.text)
        delete_flag = self.namespace.check_exists(
            self.namespace.get_resourcequota_url(self.nsforquota_name, self.resourcequota_name), 404)
        assert delete_flag, "删除配额失败"
        delete_app_result = self.application.delete_app(self.app_name)
        assert delete_app_result.status_code == 204, "删除应用失败 {}".format(delete_app_result.text)
        delete_flag = self.application.check_exists(self.application.app_common_url(app_id), 404)
        assert delete_flag, "删除应用失败"
        delete_ns_result = self.namespace.delete_namespaces(self.nsforquota_name)
        assert delete_ns_result.status_code == 204, "删除命名空间失败 {}".format(delete_ns_result.text)
        delete_flag = self.namespace.check_exists(self.namespace.get_namespace_url(self.nsforquota_name), 404)
        assert delete_flag, "删除命名空间失败"
        assert result['flag'], result

    @pytest.mark.BAT
    def test_general_namespaces(self):
        # if not self.namespace.is_weblab_open("USER_VIEW_ENABLED"):
        #     return True, "用户视角未打开，不需要测试"
        result = {"flag": True}
        create_ns_result = self.namespace.create_general_namespaces('./test_data/namespace/newnamespace.yml',
                                                                    {'$K8S_NAMESPACE': self.general_namespace_name})
        assert create_ns_result.status_code == 201, "创建新命名空间失败 {}".format(create_ns_result.text)
        resourcequota_flag = self.namespace.check_exists(
            self.namespace.get_resourcequota_url(self.general_namespace_name, 'default'), 200)
        result = self.namespace.update_result(result, resourcequota_flag, 'resourcequota创建失败')
        limitrange_flag = self.namespace.check_exists(
            self.namespace.get_limitrange_url(self.general_namespace_name, 'default'), 200)
        result = self.namespace.update_result(result, limitrange_flag, 'limitrange创建失败')
        list_ns_result = self.namespace.list_namespaces()
        result = self.namespace.update_result(result, list_ns_result.status_code == 200, '获取命名空间列表失败')
        result = self.namespace.update_result(result, self.general_namespace_name in list_ns_result.text,
                                              '获取命名空间列表失败:新建的不在列表中')
        delete_ns_result = self.namespace.delete_general_namespaces(self.general_namespace_name)
        assert delete_ns_result.status_code == 204, "删除命名空间失败 {}".format(delete_ns_result.text)
        delete_flag = self.namespace.check_exists(self.namespace.get_namespace_url(self.general_namespace_name), 404)
        assert delete_flag, "删除命名空间失败"
        assert result['flag'], result
