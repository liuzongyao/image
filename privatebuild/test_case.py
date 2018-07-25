import pytest
from privatebuild.build import PrivateBuild


@pytest.mark.region
@pytest.mark.privatebuild
class TestPrivateBuildTestSuit(object):
    def setup_class(self):
        self.client = PrivateBuild()
        self.svn_build_name = "e2e-svn-{}".format(self.client.region_name)

    def teardown_class(self):
        self.client.delete_build(self.svn_build_name)

    def test_svn_build(self):
        result = {"flag": True}
        self.client.delete_build(self.svn_build_name)
        ret_create = self.client.create_build("svn_build.json", {"$NAME": self.svn_build_name})
        assert ret_create.status_code == 201, ret_create.text
        config_id = ret_create.json()["config_id"]

        ret_trigger = self.client.trigger_build(config_id)
        assert ret_trigger.status_code == 201, ret_trigger.text

        history_id = ret_trigger.json()["build_id"]
        ret_status = self.client.get_build_status(history_id)
        assert ret_status, "build failed"

        ret_log = self.client.get_build_log(history_id)
        result = self.client.update_result(result, ret_log, "get build log")

        ret_del = self.client.delete_build(self.svn_build_name)
        assert ret_del.status_code == 204, ret_del.text
        assert result["flag"], result
