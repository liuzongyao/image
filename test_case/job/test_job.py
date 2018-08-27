import pytest
from test_case.job.job import Job


@pytest.mark.region
@pytest.mark.job
class TestJobSuit(object):
    def setup_class(self):
        self.job = Job()
        self.job_config_name = "e2e-job-{}".format(self.job.region_name)
        self.job_registry_index = self.job.global_info["$IMAGE"].split("/")[0]
        self.job_image_name = self.job.global_info["$IMAGE"].split("/", 1)[1].split(':')[0]
        self.job_image_tag = self.job.global_info["$IMAGE"].split(":")[1]

    def teardown_class(self):
        self.job.delete_job_config(self.job_config_name)

    def test_job(self):
        """
        创建任务(镜像，环境变量，超时时长,命令sleep)-获取创建任务事件-获取任务列表-获取任务配置详情(验证环境变量，命令，镜像)
        -触发任务配置-查看任务历史-查看任务历史日志(验证环境变量)-停止任务-查看任务历史
        更新任务配置(命令)-更新任务事件-获取任务配置详情(命令)-触发任务-获取触发任务事件-任务历史列表和日志(任务命令)-删除任务历史
        -删除任务配置-查看删除任务配置事件
        :return:
        """
        result = {"flag": True}
        self.job.delete_job_config(self.job_config_name)

        ret_create = self.job.create_job_config("./test_data/job/job_config.json",
                                                {"$CONFIG_NAME": self.job_config_name,
                                                 "$registry": self.job_registry_index,
                                                 "$image_name": self.job_image_name,
                                                 "$image_tag": self.job_image_tag})
        assert ret_create.status_code == 201, "创建job_config出错:{}".format(ret_create.text)
        config_id = ret_create.json()["config_uuid"]

        ret_trigger = self.job.trigger_job_config(config_id)
        assert ret_trigger.status_code == 201, "验证job状态出错:job".format(ret_trigger.text)

        job_id = ret_trigger.json()["job_uuid"]
        ret_status = self.job.get_job_status(job_id, 'status', 'SUCCEEDED')
        assert ret_status, "验证job状态出错： job: {} is not runnning".format(job_id)

        ret_log = self.job.get_job_log(job_id)
        result = self.job.update_result(result, ret_log, "get job log expexcted to contain hello")

        # delete job
        ret_del = self.job.delete_job_config(self.job_config_name)
        assert ret_del.status_code == 204, ret_del.text
        assert result["flag"], "delete job_config result is {}".format(result)
