import pytest
from test_case.job.job import Job


@pytest.mark.region
@pytest.mark.job
class TestJobSuit(object):
    def setup_class(self):
        self.job = Job()
        self.job_config_name = "e2e-job{}".format(self.job.region_name)

    def teardown_class(self):
        self.job.delete_job_config(self.job_config_name)

    def test_job_config(self):
        result = {"flag": True}
        self.job.delete_job_config(self.job_config_name)
        ret_create = self.job.create_job_config("./test_data/job/job_config.json", {"$CONFIG_NAME": self.job_config_name})
        assert ret_create.status_code == 201, ret_create.text
        config_id = ret_create.json()["config_uuid"]

        ret_trigger = self.job.trigger_job_config(config_id)
        assert ret_trigger.status_code == 201, ret_trigger.text

        job_id = ret_trigger.json()["job_uuid"]
        ret_status = self.job.get_job_status(job_id)
        assert ret_status, "job failed"

        ret_log = self.job.get_job_log(job_id)
        result = self.job.update_result(result, ret_log, "get job log")

        # delete job
        ret_del = self.job.delete_job_config(self.job_config_name)
        assert ret_del.status_code == 204, ret_del.text
        assert result["flag"], result
