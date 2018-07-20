import pytest

from privatebuild.build import PrivateBuild


@pytest.mark.region
@pytest.mark.privatebuild
class TestPrivateBuildTestSuit(object):
    def setup_class(self):
        self.clent = PrivateBuild()
        self.svn_build_name = "e2e-svn-{}".format(self.clent.region_name)

    def teardown_class(self):
        self.clent.delete_build(self.svn_build_name)

    def test_svn_build(self):
        self.clent.delete_build(self.svn_build_name)
        ret_create = self.clent.create_build("svn_build.json", {"$NAME": self.svn_build_name})
        assert ret_create.status_code == 201, ret_create.text
        config_id = ret_create.json()["config_id"]

        ret_trigger = self.clent.trigger_build(config_id)
        assert ret_trigger.status_code == 201, ret_trigger.text

        history_id = ret_trigger.json()["build_id"]
        ret_status = self.clent.get_build_status(history_id)
        assert ret_status, "build failed"

        ret_log = self.clent.get_build_log(history_id)
        assert ret_log, "get build log failed"

        ret_del = self.clent.delete_build(self.svn_build_name)
        assert ret_del.status_code == 204, ret_del.text