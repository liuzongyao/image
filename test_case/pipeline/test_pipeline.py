import pytest

from backup.application.app import Application
from common.log import logger
from test_case.image.image import Image
from test_case.pipeline.pipeline import Pipeline


@pytest.mark.region
@pytest.mark.pipeline
class TestPipelineSuite(object):
    def setup_class(self):
        self.pipeline_tool = Pipeline()
        self.image_tool = Image()
        self.app_tool = Application()

        self.pipeline_name = "alauda-pipeline-{}".format(self.pipeline_tool.region_name).replace('_', '-')
        self.registry_id = self.pipeline_tool.global_info['PRIVATE_REGISTRY'][0]['uuid']
        self.registry_endpoint = self.pipeline_tool.global_info['PRIVATE_REGISTRY'][0]['endpoint']
        self.repo_name = self.pipeline_tool.global_info['$REPO_NAME']
        self.organization = self.pipeline_tool.global_info['$NAMESPACE']
        self.description = "alauda pipeline"
        self.app_id = self.pipeline_tool.global_info['$GLOBAL_APP_ID']
        self.time_out = '5'

        self.teardown_class(self)

    def teardown_class(self):
        pipeline_id = self.pipeline_tool.get_pipeline_id(self.pipeline_name, 'uuid')
        self.pipeline_tool.delete_pipeline(pipeline_id)

    def test_pipeline(self):
        result = {"flag": True}

        triggerImage = "{}/{}".format(self.registry_endpoint, self.repo_name)

        share_path = "/images/{}/{}/{}".format(self.organization, self.organization, self.repo_name)

        # get repo id
        ret = self.image_tool.get_repo_detail(self.repo_name)
        assert ret.status_code == 200, "获取镜像仓库详情失败"
        repo_id = self.image_tool.get_value(ret.json(), 'uuid')

        # create pipeline config
        ret = self.pipeline_tool.create_pipeline('./test_data/pipeline/create_pipeline.yaml',
                                                 {"$registry_id": self.registry_id, "$triggerImage": triggerImage,
                                                  '"$timeout"': self.time_out, "$share_path": share_path,
                                                  "$pipeline_name": self.pipeline_name, "$repo_id": repo_id})

        assert ret.status_code == 201, "创建流水线操作失败"

        pipeline_id = ret.json()['uuid']

        # get pipeline list
        ret = self.pipeline_tool.get_pipeline_list()

        assert ret.status_code == 200, "获取流水线列表失败"

        assert self.pipeline_name in ret.text, "新创建的流水线不在流水线列表中"

        # get pipeline detail
        ret = self.pipeline_tool.get_pipeline_detail(pipeline_id)

        assert ret.status_code == 200, "获取流水线详情失败"

        contents = ret.json()
        tasks = contents['stages'][0]['tasks']

        stages_id = self.pipeline_tool.get_value(contents, 'stages.0.uuid')
        task_1_id = self.pipeline_tool.get_uuid_accord_name(tasks, {"name": "task-1"}, 'uuid')
        task_2_id = self.pipeline_tool.get_uuid_accord_name(tasks, {"name": "task-2"}, 'uuid')
        task_3_id = self.pipeline_tool.get_uuid_accord_name(tasks, {"name": "task-3"}, 'uuid')
        task_4_id = self.pipeline_tool.get_uuid_accord_name(tasks, {"name": "task-4"}, 'uuid')

        # update pipeline
        ret = self.pipeline_tool.update_pipeline(pipeline_id, './test_data/pipeline/update_pipeline.yaml',
                                                 {"$registry_id": self.registry_id, "$stages_id": stages_id,
                                                  "$task_1_id": task_1_id, "$timeout": self.time_out,
                                                  "$triggerImage": triggerImage, "$task_2_id": task_2_id,
                                                  "$share_path": share_path, "$task_3_id": task_3_id,
                                                  "$task_4_id": task_4_id, "$pipeline_name": self.pipeline_name,
                                                  "$description": self.description, "$repo_id": repo_id,
                                                  "$pipeline_id": pipeline_id})

        assert ret.status_code == 204, "更新流水线操作失败"

        # get pipeline detail
        ret = self.pipeline_tool.get_pipeline_detail(pipeline_id)

        assert ret.status_code == 200, "获取流水线详情失败"

        assert self.pipeline_tool.get_value(ret.json(), 'description') == self.description, "更新流水线失败"

        # get app detail
        ret = self.app_tool.get_app_detail(self.app_id)

        assert ret.status_code == 200, "获取应用详情失败"

        image_tag = self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image'
                                            ).split(":")[-1]

        logger.info("app image tag before update: {}".format(image_tag))

        # get image tag
        ret = self.image_tool.get_repo_tag(self.repo_name)
        assert ret.status_code == 200, "获取镜像版本失败"

        contents = ret.json()['results']

        assert len(contents) > 0, "镜像版本为空"

        repo_tag = contents[0]['tag_name']

        logger.info("choice repo tag: {}".format(repo_tag))

        # start pipeline
        ret = self.pipeline_tool.start_pipeline(pipeline_id, './test_data/pipeline/start_pipeline.yaml',
                                                {"$pipeline_id": pipeline_id, "$registry_uuid": self.registry_id,
                                                 "$image_tag": repo_tag, "$repo_id": repo_id})

        assert ret.status_code == 200, "启动流水线失败"

        history_id = ret.json()['uuid']

        # get pipeline history status
        ret = self.pipeline_tool.get_pipeline_history_detail(pipeline_id, history_id, 'status', 'completed')

        assert ret, "流水线运行失败"

        # get pipeline task id
        ret = self.pipeline_tool.get_pipeline_task_id(pipeline_id, history_id)
        assert ret.status_code == 200, "获取流水线子任务信息失败"

        contents = ret.json()['stages'][0]['tasks']

        task_1_id = self.pipeline_tool.get_uuid_accord_name(contents, {"name": "task-1"}, "uuid")
        task_2_id = self.pipeline_tool.get_uuid_accord_name(contents, {"name": "task-2"}, "uuid")
        task_3_id = self.pipeline_tool.get_uuid_accord_name(contents, {"name": "task-3"}, "uuid")

        # get pipeline logs
        ret = self.pipeline_tool.get_pipeline_logs(pipeline_id, history_id)

        result = self.pipeline_tool.update_result(result, ret is True, "获取流水线运行历史基本信息的日志失败")

        ret = self.pipeline_tool.get_pipeline_task_logs(pipeline_id, history_id, task_1_id, "logglogloglog")

        result = self.pipeline_tool.update_result(result, ret is True, "获取流水线运行历史task 1的日志失败")

        ret = self.pipeline_tool.get_pipeline_task_logs(pipeline_id, history_id, task_2_id, "Upload successfully")

        result = self.pipeline_tool.update_result(result, ret is True, "获取流水线运行历史task 2的日志失败")

        ret = self.pipeline_tool.get_pipeline_task_logs(pipeline_id, history_id, task_3_id, "Download successfully")

        result = self.pipeline_tool.update_result(result, ret is True, "获取流水线运行历史task 3的日志失败")

        # get service image tag
        ret = self.app_tool.get_app_detail(self.app_id)

        assert ret.status_code == 200, "获取应用详情失败"

        new_tag = self.app_tool.get_value(ret.json(), 'kubernetes.0.spec.template.spec.containers.0.image'
                                          ).split(":")[-1]

        logger.info("app image tag after update: {}".format(new_tag))

        assert new_tag == repo_tag, "更新应用失败"

        # get pipeline history list
        ret = self.pipeline_tool.get_history_list()

        assert ret.status_code == 200, "获取流水线运行历史列表失败"

        assert history_id in ret.text, "流水线运行历史列表中不包含本次运行的历史记录"

        # get image artifacts
        ret = self.image_tool.get_artifacts(self.repo_name, repo_tag)

        assert ret.status_code == 200, "获取镜像版本的产出物操作失败"

        contents = ret.json()

        # if contents['build_id'] and len(contents['artifacts']) > 0:
        #     # get upload artifacts result
        #     ret = self.pipeline_tool.get_upload_artifacts_result(contents['build_id'])
        #
        #     assert ret.status_code == 200, "获取上传产出物失败"
        #
        #     artifact = contents['artifacts'][0]['key']
        #     logger.info("artifact: {}".format(artifact))
        #
        #     assert artifact in ret.text, "上传产出物失败"
        #
        #     # get download artifacts result
        #     ret = self.pipeline_tool.get_download_artifacts_result(pipeline_id, history_id)
        #
        #     assert ret.status_code == 200, "获取下载产出物失败"
        #
        #     assert artifact in ret.text, "下载产出物失败"

        # delete pipeline history
        ret = self.pipeline_tool.delete_pipeline_history(pipeline_id, history_id)

        assert ret.status_code == 204, "删除流水线历史操作失败"

        ret = self.pipeline_tool.check_pipeline_history_exist(pipeline_id, history_id, 404)

        assert ret, "删除流水线历史失败"

        # delete pipeline
        ret = self.pipeline_tool.delete_pipeline(pipeline_id)

        assert ret.status_code == 204, "删除流水线操作失败"

        ret = self.pipeline_tool.check_pipeline_exist(pipeline_id, 404)
        assert ret, "删除流水线失败"

        assert result['flag'], result
