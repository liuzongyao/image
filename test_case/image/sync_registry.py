from common.base_request import Common


class SyncRegistry(Common):
    def __init__(self):
        super(SyncRegistry, self).__init__()

    def get_registry_list_url(self):
        return "/v1/registries/{}/".format(self.account)

    def common_url(self, config_id=None):
        return config_id and "/v1/sync-registry/{}/configs/{}".format(self.account, config_id) or \
               "/v1/sync-registry/{}/configs".format(self.account)

    def get_registry_list(self):
        path = self.get_registry_list_url()
        response = self.send(method='get', path=path)
        if response.status_code == 200:
            return response.json()
        return []

    def get_registry_uuid(self, registry_name=None, is_public=None):
        """
        Get the registry name and uuid
        :param: string(registry_name)
        :return: bool(is_public)
        """
        contents = self.get_registry_list()
        length = len(contents)
        for i in range(length):
            if contents[i]['name'] == registry_name:
                return contents[i]['name'], contents[i]['uuid'], contents[i]['endpoint']
            if contents[i]['is_public'] == is_public:
                return contents[i]['name'], contents[i]['uuid'], contents[i]['endpoint']

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