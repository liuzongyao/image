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
        创建任务(镜像，环境变量，超时时长)-获取创建任务事件-获取任务列表-获取任务配置详情(验证环境变量，命令，镜像)
        -触发任务配置-查看任务历史-查看任务历史日志(验证环境变量)-定时任务
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

        # get create job_config event
        event_cratejob = self.job.get_job_events(config_id, "create", "job_config")
        result = self.job.update_result(result, event_cratejob, '操作事件：获取创建任务事件出错')

        # list job_config
        ret_list = self.job.get_list_jobconfig()
        result = self.job.update_result(result, ret_list.status_code == 200, '获取job_config列表出错')
        result = self.job.update_result(result, self.job_config_name in ret_list.text, '获取任务配置列表：新建job_config不在列表中')

        # job_config detail
        ret_detail = self.job.get_job_config(config_id)
        result = self.job.update_result(result, ret_detail.status_code == 200, '获取job_config详情出错')
        result = self.job.update_result(result, "CUSTOM_COMMAND" in ret_detail.text,
                                        '获取job_config: 期望存在关键字CUSTOM_COMMAND')

        # trigger job
        ret_trigger = self.job.trigger_job_config(config_id)
        assert ret_trigger.status_code == 201, "触发job_config出错:错误信息{}".format(ret_trigger.text)

        job_id = ret_trigger.json()["job_uuid"]
        ret_status = self.job.get_job_status(job_id, 'status', 'SUCCEEDED')
        assert ret_status, "验证job状态出错： job: {} is not runnning，".format(job_id)

        # get trigger job event
        # event_triggerjob = self.job.get_job_events(config_id, "trigger", "job_config")
        # result = self.job.update_result(result, event_triggerjob, '操作事件：获取触发任务事件出错')

        # get job history list
        ret_jobhisttory_list = self.job.get_list_job()
        result = self.job.update_result(result, ret_jobhisttory_list.status_code == 200, '获取任务历史列表出错')
        result = self.job.update_result(result, self.job_config_name in ret_jobhisttory_list.text,
                                        '获取任务历史列表:新触发的任务不在列表中')

        # get job log
        ret_log = self.job.get_job_log(job_id, 'create')
        result = self.job.update_result(result, ret_log, "获取任务历史日志失败，期望存在关键字create")

        # schedule_rule
        ret_job_list = self.job.get_job_list(config_id, "count", 2)
        assert ret_job_list, "验证定时任务错误，错误信息{}".format(ret_job_list.text)

        # update job_config
        ret_update = self.job.update_job_config(config_id, './test_data/job/update_job_config.json',
                                                {"$CONFIG_NAME": self.job_config_name})
        assert ret_update.status_code == 204, "更新任务配置失败:{}".format(ret_update.text)

        # get update job_config event
        event_updatejob = self.job.get_job_events(config_id, "update", "job_config")
        result = self.job.update_result(result, event_updatejob, '操作事件:获取更新任务配置事件出错')

        # get job history list
        ret_jobhisttory_list = self.job.get_list_job()
        result = self.job.update_result(result, ret_jobhisttory_list.status_code == 200, '获取任务历史列表出错')
        result = self.job.update_result(result, self.job_config_name in ret_jobhisttory_list.text,
                                        '获取任务历史列表:新触发的任务不在列表中')

        # trigger update_job
        ret_trigger = self.job.trigger_job_config(config_id)
        assert ret_trigger.status_code == 201, "触发job_config出错:错误信息{}".format(ret_trigger.text)

        job_id = ret_trigger.json()["job_uuid"]
        ret_status = self.job.get_job_status(job_id, 'status', 'SUCCEEDED')
        assert ret_status, "验证job状态出错： job: {} is not runnning，".format(job_id)

        # get trigger job event
        # event_triggerjob = self.job.get_job_events(config_id, "trigger", "job_config")
        # result = self.job.update_result(result, event_triggerjob, '操作事件：获取触发任务事件出错')

        # get update job log
        ret_log = self.job.get_job_log(job_id, 'command')
        result = self.job.update_result(result, ret_log, "获取任务历史日志失败，期望存在关键字command，")

        # delete job histrory
        job_uuid = ret_trigger.json()["job_uuid"]
        ret_del = self.job.delete_job(job_uuid)
        assert ret_del.status_code == 204, ret_del.text
        assert result["flag"], "delete job_history result is {}".format(result)

        # delete job_config
        ret_del = self.job.delete_job_config(self.job_config_name)
        assert ret_del.status_code == 204, ret_del.text
        assert result["flag"], "delete job_config result is {}".format(result)
