from common.base_request import Common


class SyncRegistryHistory(Common):
    def __init__(self):
        super(SyncRegistryHistory, self).__init__()

    def common_url(self, history_id=None):
        return history_id and "/v1/sync-registry/{}/histories/{}".format(self.account, history_id) or\
               "/v1/sync-registry/{}/histories".format(self.account)

    def get_history_log_url(self, history_id):
        return "/v1/sync-registry/{}/histories/{}/logs".format(self.account, history_id)

    def get_sync_history_list(self):
        path = self.common_url()
        return self.send(method='get', path=path)

    def create_sync_history_task(self, file, data):
        path = self.common_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_sync_registry_history_detail(self, history_id):
        path = self.common_url(history_id=history_id)
        return self.send(method='get', path=path)

    def get_sync_registry_task_status(self, history_id, key, expect_value):
        path = self.common_url(history_id)
        return self.get_status(path, key, expect_value)

    def delete_sync_registry_history(self, history_id):
        path = self.common_url(history_id=history_id)
        return self.send(method='delete', path=path)

    def get_sync_registry_history_log(self, history_id):
        path = self.get_history_log_url(history_id=history_id)
        return self.send(method='get', path=path)
