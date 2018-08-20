import time

import pytest

from test_case.persistentvolumeclaims.pvc import Pvc
from test_case.persistentvolumes.pv import Pv
from test_case.storageclasses.scs import Scs
from test_case.volume.volume import Volume


@pytest.mark.pvc
class TestPvSuite(object):
    def setup_class(self):
        self.volume = Volume()
        self.volume_name = 'alauda-volforpvc-{}'.format(self.volume.region_name).replace('_', '-')
        self.region_volumes = self.volume.global_info['$REGION_VOLUME'].split(",")
        self.pv = Pv()
        self.pv_name = 'alauda-pv-{}'.format(self.pv.region_name).replace('_', '-')
        self.pvc = Pvc()
        self.pvc_name = 'alauda-pvc-{}'.format(self.pvc.region_name).replace('_', '-')

        self.scs = Scs()
        self.scs_name = 'alauda-scsforpvc-{}'.format(self.pvc.region_name).replace('_', '-')
        self.pvcusescs_name = 'alauda-pvcusescs-{}'.format(self.pvc.region_name).replace('_', '-')
        self.masterips = self.scs.global_info["$MASTERIPS"].split(",")
        self.default_size = self.scs.get_default_size()

        self.defaultscs_name = 'alauda-defaultscsforpvc-{}'.format(self.pvc.region_name).replace('_', '-')
        self.pvcusedefaultscs_name = 'alauda-pvcusedefaultscs-{}'.format(self.pvc.region_name).replace('_', '-')

        self.teardown_class(self)

    def teardown_class(self):
        self.scs.delete_scs(self.defaultscs_name)
        self.pvc.delete_pvc(self.pvc.global_info["$K8S_NAMESPACE"], self.pvcusedefaultscs_name)
        self.scs.delete_scs(self.scs_name)
        self.pvc.delete_pvc(self.pvc.global_info["$K8S_NAMESPACE"], self.pvcusescs_name)
        self.pvc.delete_pvc(self.pvc.global_info["$K8S_NAMESPACE"], self.pvc_name)
        self.pv.delete_pv(self.pv_name)
        volume_id = self.volume.get_volume_id_from_list(self.volume_name)
        self.volume.delete_volume(volume_id)

    @pytest.mark.BAT
    def test_pvc(self):
        if len(self.region_volumes) == 0:
            assert True, "集群不支持存储卷"
            return
        result = {"flag": True}
        # create volume
        if self.region_volumes[0] == "glusterfs":
            createvolume_result = self.volume.create_volume("./test_data/volume/glusterfs.json",
                                                            {"$volume_name": self.volume_name, '"$size"': "1"})
        elif self.region_volumes[0] == "ebs":
            createvolume_result = self.volume.create_volume("./test_data/volume/ebs.json",
                                                            {"$volume_name": self.volume_name, '"$size"': "1"})
        else:
            assert True, "未知的存储卷类型{}".format(self.pv.global_info['$REGION_VOLUME'])
            return
        assert createvolume_result.status_code == 201, createvolume_result.text
        volume_id = createvolume_result.json().get("id")
        # create pv
        createpv_result = self.pv.create_pv("./test_data/pv/pv.json",
                                            {"$pv_name": self.pv_name, "$pv_policy": "Retain", "$size": "1",
                                             "$volume_id": volume_id, "$volume_driver": self.region_volumes[0]})
        assert createpv_result.status_code == 201, createpv_result.text
        # create pvc
        createpvc_result = self.pvc.create_pvc("./test_data/pvc/pvc.json",
                                               {"$pvc_name": self.pvc_name, "$pvc_mode": "ReadWriteOnce",
                                                "$scs_name": "", "$size": "1"})
        assert createpvc_result.status_code == 201, createpvc_result.text
        # list pvc
        list_result = self.pvc.list_pvc()
        result = self.pvc.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.pvc.update_result(result, self.pvc_name in list_result.text, "list pvcs error")
        # get pvc detail
        detail_result = self.pvc.get_pvc_detail(self.pvc.global_info["$K8S_NAMESPACE"], self.pvc_name)
        result = self.pvc.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.pvc.update_result(result, self.pvc.get_value(detail_result.json(), "status.phase") == "Bound",
                                        detail_result.text)
        result = self.pvc.update_result(result, self.pvc.get_value(detail_result.json(),
                                                                   "kubernetes.spec.volumeName") == self.pv_name,
                                        detail_result.text)
        # delete pvc
        delete_result = self.pvc.delete_pvc(self.pvc.global_info["$K8S_NAMESPACE"], self.pvc_name)
        assert delete_result.status_code == 204
        assert self.pvc.check_exists(self.pvc.get_common_pvc_url(self.pvc.global_info["$K8S_NAMESPACE"], self.pvc_name),
                                     404)
        assert result['flag'], result

    @pytest.mark.scs
    def test_pvc_use_scs(self):
        result = {"flag": True}
        # create scs
        if len(self.masterips) == 0:
            assert True, "获取master节点失败，不能创建正常使用的存储类"
            return
        masterip = self.masterips[0]
        create_result = self.scs.create_scs("./test_data/scs/scs.yml",
                                            {"$scs_name": self.scs_name, "$is_default": "false",
                                             "$master_ip": masterip})
        assert create_result.status_code == 201, create_result.text

        # create pvc
        createpvc_result = self.pvc.create_pvc("./test_data/pvc/pvc.json",
                                               {"$pvc_name": self.pvcusescs_name, "$pvc_mode": "ReadWriteOnce",
                                                "$scs_name": self.scs_name, "$size": "1"})
        assert createpvc_result.status_code == 201, createpvc_result.text
        time.sleep(60)
        # get pvc detail
        detail_result = self.pvc.get_pvc_detail(self.pvc.global_info["$K8S_NAMESPACE"], self.pvcusescs_name)
        result = self.pvc.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.pvc.update_result(result, self.pvc.get_value(detail_result.json(), "status.phase") == "Bound",
                                        detail_result.text)
        result = self.pvc.update_result(result, self.pvc.get_value(detail_result.json(),
                                                                   "kubernetes.spec.volumeName").startswith("pvc"),
                                        detail_result.text)
        self.pvc.delete_pvc(self.pvc.global_info["$K8S_NAMESPACE"], self.pvcusescs_name)
        self.scs.delete_scs(self.scs_name)
        assert result['flag'], result

    @pytest.mark.scs
    def test_pvc_use_defaultscs(self):
        if self.default_size > 1:
            assert True, "有两个以上的默认存储类，无法测试"
            return
        elif self.default_size == 0:
            # create scs
            if len(self.masterips) == 0:
                assert True, "获取master节点失败，不能创建正常使用的存储类"
                return
            masterip = self.masterips[0]
            create_result = self.scs.create_scs("./test_data/scs/scs.yml",
                                                {"$scs_name": self.defaultscs_name, "$is_default": "true",
                                                 "$master_ip": masterip})
            assert create_result.status_code == 201, create_result.text
        result = {"flag": True}
        # create pvc
        createpvc_result = self.pvc.create_pvc("./test_data/pvc/pvc_usedefault.json",
                                               {"$pvc_name": self.pvcusedefaultscs_name, "$pvc_mode": "ReadWriteOnce",
                                                "$size": "1"})
        assert createpvc_result.status_code == 201, createpvc_result.text
        time.sleep(60)
        # get pvc detail
        detail_result = self.pvc.get_pvc_detail(self.pvc.global_info["$K8S_NAMESPACE"], self.pvcusedefaultscs_name)
        result = self.pvc.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.pvc.update_result(result, self.pvc.get_value(detail_result.json(), "status.phase") == "Bound",
                                        detail_result.text)
        result = self.pvc.update_result(result, self.pvc.get_value(detail_result.json(),
                                                                   "kubernetes.spec.volumeName").startswith("pvc"),
                                        detail_result.text)
        self.pvc.delete_pvc(self.pvc.global_info["$K8S_NAMESPACE"], self.pvcusedefaultscs_name)
        self.scs.delete_scs(self.defaultscs_name)
        assert result['flag'], result
