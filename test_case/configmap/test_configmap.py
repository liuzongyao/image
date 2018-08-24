import pytest

from test_case.configmap.configmap import Configmap


@pytest.mark.configmap
class TestCmSuite(object):
    def setup_class(self):
        self.configmap = Configmap()
        self.configmap_name = 'alauda-configmap-{}'.format(self.configmap.region_name).replace('_', '-')

        self.teardown_class(self)

    def teardown_class(self):
        self.configmap.delete_configmap(self.configmap.global_info["$K8S_NAMESPACE"], self.configmap_name)

    @pytest.mark.BAT
    def test_configmap(self):
        result = {"flag": True}
        # create configmap
        createconfigmap_result = self.configmap.create_configmap("./test_data/configmap/configmap.json",
                                                                 {"$cm_name": self.configmap_name,
                                                                  "$cm_key": self.configmap_name})
        assert createconfigmap_result.status_code == 201, createconfigmap_result.text
        self.configmap.check_value_in_response(self.configmap.get_common_configmap_url(), self.configmap_name)
        # list configmap
        list_result = self.configmap.list_configmap()
        result = self.configmap.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.configmap.update_result(result, self.configmap_name in list_result.text, "cm列表：新建cm不在列表中")
        # update configmap
        update_result = self.configmap.update_configmap(self.configmap.global_info["$K8S_NAMESPACE"],
                                                        self.configmap_name, "./test_data/configmap/configmap.json",
                                                        {"$cm_name": self.configmap_name, "$cm_key": "updatecm"})
        assert update_result.status_code == 204, update_result.text
        self.configmap.check_value_in_response(
            self.configmap.get_common_configmap_url(self.configmap.global_info["$K8S_NAMESPACE"],
                                                    self.configmap_name), "updatecm")
        # get configmap detail
        detail_result = self.configmap.get_configmap_detail(self.configmap.global_info["$K8S_NAMESPACE"],
                                                            self.configmap_name)
        result = self.configmap.update_result(result, detail_result.status_code == 200, detail_result.text)
        result = self.configmap.update_result(result,

                                              self.configmap.get_value(detail_result.json(),
                                                                       "kubernetes.data.updatecm") == "updatecm",
                                              detail_result.text)
        # delete configmap
        delete_result = self.configmap.delete_configmap(self.configmap.global_info["$K8S_NAMESPACE"],
                                                        self.configmap_name)
        assert delete_result.status_code == 204
        assert self.configmap.check_exists(

            self.configmap.get_common_configmap_url(self.configmap.global_info["$K8S_NAMESPACE"], self.configmap_name),
            404)
        assert result['flag'], result
