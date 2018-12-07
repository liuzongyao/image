import pytest

from test_case.storageclasses.scs import Scs


@pytest.mark.scs
@pytest.mark.ace
class Teststorageclass():
    def setup_class(self):
        self.scs = Scs()
        self.scs_name = "e2e-scs{}".format(self.scs.region_name).replace('_', '-')
        self.masterips = self.scs.global_info["$MASTERIPS"].split(",")

    def teardown_class(self):
        self.scs.delete_scs(self.scs_name)

    @pytest.mark.BAT
    def test_scs(self):
        result = {"flag": True}
        # create scs
        create_result = self.scs.create_scs("./test_data/scs/scs.yml",
                                            {"$scs_name": self.scs_name, "$is_default": "false",
                                             })
        assert create_result.status_code == 201, "创建sc失败{}".format(create_result.text)
        self.scs.check_value_in_response(self.scs.get_common_scs_url(), self.scs_name, params={})
        # list scs
        list_result = self.scs.list_scs()
        result = self.scs.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.scs.update_result(result, self.scs_name in list_result.text, "获取存储类列表：新建sc不在列表中")
        # update scs
        update_result = self.scs.update_scs(self.scs_name, "./test_data/scs/scs.yml",
                                            {"$scs_name": self.scs_name, "$is_default": "true",
                                             })
        assert update_result.status_code == 204, "sc设为默认失败{}".format(update_result.text)
        self.scs.get_status(self.scs.get_common_scs_url(self.scs_name),
                            "kubernetes#metadata#annotations#storageclass.kubernetes.io/is-default-class",
                            "true", delimiter="#", params={})
        # get scs detail
        detail_result = self.scs.get_scs_detail(self.scs_name)
        result = self.scs.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.scs.update_result(result, self.scs.get_value(detail_result.json(),
                                                                   "kubernetes#metadata#annotations#storageclass.kubernetes.io/is-default-class",
                                                                   delimiter="#") == "true",
                                        "sc设为默认失败")
        # delete scs
        delete_result = self.scs.delete_scs(self.scs_name)
        assert delete_result.status_code == 204, "删除sc失败 {}".format(delete_result.text)
        assert result['flag'], result
