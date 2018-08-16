import pytest

from test_case.image.sync_registry import SyncRegistry
from test_case.image.image import Image
from test_case.image.sync_registry_history import SyncRegistryHistory


@pytest.mark.region
@pytest.mark.sync_registry
class TestSyncRegistrySuite(object):
    def setup_class(self):
        self.sync_tool = SyncRegistry()
        self.image_tool = Image()
        self.history_tool = SyncRegistryHistory()

        self.repo_name = self.sync_tool.global_info.get('$REPO_NAME')
        self.sync_config_name = "alauda-sync-config-{}".format(self.sync_tool.registry_name)

        self.memory = '256'

        self.sync_tool.delete_sync_config(self.sync_config_name)

    def teardown_class(self):
        self.sync_tool.delete_sync_config(self.sync_config_name)

    def test_sync_public_registry(self):
        result = {"flag": True}
        get_publick_registry = self.sync_tool.get_registry_uuid(is_public=True)
        if not get_publick_registry:
            assert result['flag'], "no public registry, no need to run"
            return
        else:
            # create sync config
            create_ret = self.sync_tool.create_sync_config('./test_data/image/create_sync_config.yaml',
                                                           {"$INTERNAL_ID": get_publick_registry[1],
                                                            "$CONFIG_NAME": self.sync_config_name})
            assert create_ret.status_code == 201, "create sync config: {} failed, Error code: {}, response: {}".format(
                self.sync_config_name, create_ret.status_code, create_ret.text)

            # get sync config detail
            get_detail = self.sync_tool.get_sync_config_detail(self.sync_config_name)
            assert get_detail.status_code == 200, "get sync config:{} detail failed,Error code: {},response: {}".format(
                self.sync_config_name, get_detail.status_code, get_detail.text)

            config_id = get_detail.json()['config_id']
            dest_id = self.sync_tool.get_value(get_detail.json(), 'dest.0.dest_id')

            # update sync config
            update_result = self.sync_tool.update_sync_config(self.sync_config_name,
                                                              './test_data/image/update_sync_config.yaml',
                                                              {"$CONFIG_ID": config_id,
                                                               "$ENDPOINT": get_publick_registry[2],
                                                               "$INTERNAL_ID": get_publick_registry[1],
                                                               "$DEST_ID": dest_id,
                                                               "$CONFIG_NAME": self.sync_config_name,
                                                               "$PROJECT_NAME": self.sync_tool.params.get('project_name'
                                                                                                          ),
                                                               "$MEMORY": self.memory})

            assert update_result.status_code == 200, "update sync config: {} failed, Error code: {}, response: {}"\
                .format(self.sync_config_name, update_result.status_code, update_result.text)

            # verify the update info
            get_detail = self.sync_tool.get_sync_config_detail(self.sync_config_name)

            assert get_detail.status_code == 200, "get sync config:{} detail failed,Error code: {},response: {}".format(
                self.sync_config_name, get_detail.status_code, get_detail.text)

            memory = str(get_detail.json()['memory'])
            dest_id = self.sync_tool.get_value(get_detail.json(), 'dest.0.dest_id')

            assert memory == self.memory, "update sync config failed, the value of memory should be {}, but still {}"\
                .format(self.memory, memory)

            # get repo tag
            get_repo_tag_ret = self.image_tool.get_repo_tag(self.repo_name)

            assert get_repo_tag_ret.status_code == 200, "get {} tag failed, Error code: {}, Response: {}".format(
                self.repo_name, get_repo_tag_ret.status_code, get_repo_tag_ret.text)

            repo_tag = self.sync_tool.get_value(get_repo_tag_ret.json(), 'results.0.tag_name')

            assert len(repo_tag) > 0, "the tag of repo: {} is null".format(self.repo_name)

            # create sync registry task
            create_task_result = self.history_tool.create_sync_history_task(
                './test_data/image/create_sync_registry_task.yaml', {"$CONFIG_ID": config_id,
                                                                     "$TAG": repo_tag,
                                                                     "$DEST_ID": dest_id})

            assert create_task_result.status_code == 201, "create sync registry task failed, Error code:{}, Response: "\
                "{}".format(create_task_result.status_code, create_task_result.text)

            # get sync history id
            history_id = create_task_result.json()[0]

            task_ret = self.history_tool.get_sync_registry_task_status(history_id, 'status', 'S')
            assert task_ret, 'sync registry failed'

            # get sync history log
            get_log_ret = self.history_tool.get_sync_registry_history_log(history_id)

            assert "stopping docker deamon" in get_log_ret.text, "get sync history log failed, code: {},response: {}"\
                .format(get_log_ret.status_code,get_log_ret.text)

            # delete sync config
            delete_result = self.sync_tool.delete_sync_config(self.sync_config_name)
            assert delete_result.status_code == 204, "delete sync config failed, error code: {}, response: {}"\
                .format(delete_result.status_code, delete_result.text)
