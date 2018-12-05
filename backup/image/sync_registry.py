from common.base_request import Common


class SyncRegistry(Common):
    def __init__(self):
        super(SyncRegistry, self).__init__()

    def common_url(self, config_id=None):
        return config_id and "/v1/sync-registry/{}/configs/{}".format(self.account, config_id) or \
               "/v1/sync-registry/{}/configs".format(self.account)

    def create_sync_config(self, file, data):
        path = self.common_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def update_sync_config(self, sync_config_name, file, data):
        path = self.common_url(sync_config_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data)

    def get_sync_config_detail(self, sync_config_name):
        path = self.common_url(sync_config_name)
        return self.send(method='get', path=path)

    def get_sync_config_list(self):
        path = self.common_url()
        return self.send(method='get', path=path)

    def delete_sync_config(self, sync_config_name):
        path = self.common_url(sync_config_name)
        return self.send(method='delete', path=path)
