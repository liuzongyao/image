from common.log import logger
from test_case.persistentvolumes.pv import Pv
from test_case.volume.volume import Volume


class TestPvSuite(object):
    def setup_class(self):
        self.volume = Volume()
        self.volume_name = 'alauda-volforpv-{}'.format(self.volume.region_name).replace('_', '-')
        self.region_volumes = self.volume.global_info['$REGION_VOLUME'].split(",")
        self.pv = Pv()
        self.pv_name = 'alauda-pv-{}'.format(self.pv.region_name).replace('_', '-')

    def teardown_class(self):
        self.pv.delete_pv(self.pv_name)
        volume_id = self.volume.get_volume_id_from_list(self.volume_name)
        self.volume.delete_volume(volume_id)

    def test_pv(self):
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
        create_result = self.pv.create_pv("./test_data/pv/pv.json",
                                          {"$pv_name": self.pv_name, "$pv_policy": "Retain", "$size": "1",
                                           "$volume_id": volume_id, "$volume_driver": self.region_volumes[0]})
        assert create_result.status_code == 201, create_result.text
        # list pv
        list_result = self.pv.list_pv()
        result = self.pv.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.pv.update_result(result, self.pv_name in list_result.text, "list pvs error")
        # update pv
        update_result = self.pv.update_pv(self.pv_name, "./test_data/pv/pv.json",
                                          {"$pv_name": self.pv_name, "$pv_policy": "Retain", "$size": "1",
                                           "$volume_id": volume_id, "$volume_driver": self.region_volumes[0]})
        assert update_result.status_code == 204, update_result.text
        # get pv detail
        detail_result = self.pv.get_pv_detail(self.pv_name)
        logger.info(detail_result.text)
        result = self.pv.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.pv.update_result(result, self.pv.get_value(detail_result.json(),
                                                                 "kubernetes-metadata-annotations-pv.alauda.io/volume_name",
                                                                 "-") == self.volume_name,
                                       "get pv detail volume_name error")

        result = self.pv.update_result(result,
                                       self.pv.get_value(detail_result.json(),
                                                         "kubernetes.status.phase") == "Available",
                                       "get pv detail status error")
        result = self.pv.update_result(result,
                                       self.pv.get_value(detail_result.json(),
                                                         "kubernetes.spec.persistentVolumeReclaimPolicy") == "Retain",
                                       "get pv detail policy error")
        # delete pv
        delete_result = self.pv.delete_pv(self.pv_name)
        assert delete_result.status_code == 204, delete_result.text
        exists_result = self.pv.check_exists(self.pv.get_common_pv_url(self.pv_name), 404)
        assert exists_result, "delete pv error"
        assert result['flag'], result
