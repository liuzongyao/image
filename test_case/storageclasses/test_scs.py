import pytest

from test_case.storageclasses.scs import Scs


@pytest.mark.scs
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
        if len(self.masterips) > 0:
            masterip = self.masterips[0]
        else:
            masterip = "0.0.0.0"
        create_result = self.scs.create_scs("./test_data/scs/scs.yml",
                                            {"$scs_name": self.scs_name, "$is_default": "false",
                                             "$master_ip": masterip})
        assert create_result.status_code == 201, create_result.text
        # list scs
        list_result = self.scs.list_scs()
        result = self.scs.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.scs.update_result(result, self.scs_name in list_result.text, "list scs error")
        # update scs
        update_result = self.scs.update_scs(self.scs_name, "./test_data/scs/scs.yml",
                                            {"$scs_name": self.scs_name, "$is_default": "true",
                                             "$$master_ip": masterip})
        assert update_result.status_code == 204, update_result.text
        # get scs detail
        detail_result = self.scs.get_scs_detail(self.scs_name)
        result = self.scs.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.scs.update_result(result, self.scs.get_value(detail_result.json(),
                                                                   "kubernetes#metadata#annotations#storageclass.kubernetes.io/is-default-class",
                                                                   delimiter="#") == "true",
                                        "set default error")
        # delete scs
        delete_result = self.scs.delete_scs(self.scs_name)
        assert delete_result.status_code == 204, delete_result.text
        assert result['flag'], result
