import pytest

from common.log import logger
from test_case.persistentvolumes.pv import Pv


@pytest.mark.pv
class TestPvSuite(object):
    def setup_class(self):
        self.pv = Pv()
        self.pv_name = 'alauda-pv-{}'.format(self.pv.region_name).replace('_', '-')
        self.teardown_class(self)

    def teardown_class(self):
        self.pv.delete_pv(self.pv_name)

    @pytest.mark.BAT
    def test_pv(self):
        result = {"flag": True}

        # create pv
        create_result = self.pv.create_pv("./test_data/pv/pv.json",
                                          {"$pv_name": self.pv_name, "$size": "1",
                                           })
        assert create_result.status_code == 201, "创建pv失败{}".format(create_result.text)
        self.pv.check_value_in_response(self.pv.get_common_pv_url(), self.pv_name, params={})
        # list pv
        list_result = self.pv.list_pv()
        result = self.pv.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.pv.update_result(result, self.pv_name in list_result.text, "获取持久卷列表：新建pv不在列表中")
        # update pv
        update_result = self.pv.update_pv(self.pv_name, "./test_data/pv/pv.json",
                                          {"$pv_name": self.pv_name, "$size": "2",
                                           })
        assert update_result.status_code == 204, "更新pv失败{}".format(update_result.text)
        # get pv detail
        detail_result = self.pv.get_pv_detail(self.pv_name)
        logger.info(detail_result.text)
        result = self.pv.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.pv.update_result(result,
                                       self.pv.get_value(detail_result.json(),
                                                         "kubernetes.status.phase") == "Available",
                                       "获取持久卷详情失败：状态不是可用")
        result = self.pv.update_result(result,
                                       self.pv.get_value(detail_result.json(),
                                                         "kubernetes.spec.capacity.storage") == "2G",
                                       "获取持久卷详情失败：大小不是2G")
        # delete pv
        delete_result = self.pv.delete_pv(self.pv_name)
        assert delete_result.status_code == 204, "删除pv失败{}".format(delete_result.text)
        exists_result = self.pv.check_exists(self.pv.get_common_pv_url(self.pv_name), 404)
        assert exists_result, "删除持久卷失败"
        assert result['flag'], result
