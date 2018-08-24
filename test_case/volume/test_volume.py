import pytest

from test_case.volume.volume import Volume


@pytest.mark.volume
class TestVolumeSuite(object):
    def setup_class(self):
        self.volume = Volume()
        self.gfs_name = 'alauda-gfs-{}'.format(self.volume.region_name).replace('_', '-')
        self.ebs_name = 'alauda-ebs-{}'.format(self.volume.region_name).replace('_', '-')
        self.region_volumes = self.volume.global_info['$REGION_VOLUME'].split(",")
        self.teardown_class(self)

    def teardown_class(self):
        volume_id = self.volume.get_volume_id_from_list(self.gfs_name)
        self.volume.delete_volume(volume_id)
        volume_id = self.volume.get_volume_id_from_list(self.ebs_name)
        self.volume.delete_volume(volume_id)

    @pytest.mark.BAT
    def test_gfs_volume(self):
        if "glusterfs" not in self.region_volumes:
            assert True, "集群不支持glusterfs"
            return
        result = {"flag": True}
        driver_result = self.volume.list_drivers()
        result = self.volume.update_result(result, driver_result.status_code == 200, driver_result.text)
        result = self.volume.update_result(result, len(self.region_volumes) == len(driver_result.json()),
                                           "get driver error")
        create_result = self.volume.create_volume("./test_data/volume/glusterfs.json",
                                                  {"$volume_name": self.gfs_name, '"$size"': "1"})
        assert create_result.status_code == 201, create_result.text
        volume_id = create_result.json().get("id")

        list_result = self.volume.list_volume()
        result = self.volume.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.volume.update_result(result, self.gfs_name in list_result.text, "获取存储卷列表：新建gfs不在列表中")

        detail_result = self.volume.get_volume_detail(volume_id)
        result = self.volume.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.volume.update_result(result, detail_result.json().get("driver_name") == "glusterfs",
                                           "获取存储卷详情失败：driver_name不是glusterfs")
        result = self.volume.update_result(result, detail_result.json().get("state") == "available",
                                           "获取存储卷详情失败：状态不是可用")

        delete_result = self.volume.delete_volume(volume_id)
        assert delete_result.status_code == 204, delete_result.text
        exists_result = self.volume.check_exists(self.volume.get_common_volume_url(volume_id), 404)
        assert exists_result, "delete volume error"
        assert result['flag'], result

    def test_ebs_volume(self):
        if "ebs" not in self.region_volumes:
            assert True, "集群不支持ebs"
            return
        result = {"flag": True}
        driver_result = self.volume.list_drivers()
        result = self.volume.update_result(result, driver_result.status_code == 200, driver_result.text)
        result = self.volume.update_result(result, len(self.region_volumes) == len(driver_result.json()),
                                           "get driver error")
        create_result = self.volume.create_volume("./test_data/volume/ebs.json",
                                                  {"$volume_name": self.ebs_name, '"$size"': "1"})
        assert create_result.status_code == 201, create_result.text
        volume_id = create_result.json().get("id")

        list_result = self.volume.list_volume()
        result = self.volume.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.volume.update_result(result, self.ebs_name in list_result.text, "获取存储卷列表：新建ebs不在列表中")

        detail_result = self.volume.get_volume_detail(volume_id)
        result = self.volume.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.volume.update_result(result, detail_result.json().get("driver_name") == "ebs",
                                           "获取存储卷详情失败：driver_name不是ebs")
        result = self.volume.update_result(result, detail_result.json().get("state") == "available",
                                           "获取存储卷详情失败：状态不是可用")

        delete_result = self.volume.delete_volume(volume_id)
        assert delete_result.status_code == 204, delete_result.text
        exists_result = self.volume.check_exists(self.volume.get_common_volume_url(volume_id), 404)
        assert exists_result, "delete volume error"

        assert result['flag'], result
