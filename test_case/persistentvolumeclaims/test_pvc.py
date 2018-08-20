import pytest

from test_case.persistentvolumeclaims.pvc import Pvc
from test_case.persistentvolumes.pv import Pv
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

        self.pv.delete_pv(self.pv_name)
        volume_id = self.volume.get_volume_id_from_list(self.volume_name)
        self.volume.delete_volume(volume_id)

    def teardown_class(self):
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
        result = self.pvc.update_result(result, createvolume_result.status_code == 201, createvolume_result.text)
        volume_id = createvolume_result.json().get("id")
        # create pv
        createpv_result = self.pv.create_pv("./test_data/pv/pv.json",
                                            {"$pv_name": self.pv_name, "$pv_policy": "Retain", "$size": "1",
                                             "$volume_id": volume_id, "$volume_driver": self.region_volumes[0]})
        result = self.pvc.update_result(result, createpv_result.status_code == 201, createpv_result.text)
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
