from common.base_request import Common


class PrivateBuild(Common):
    def __init__(self):
        super().__init__()

    def get_build_config_url(self, config_id=None):
        return config_id and "private-build-configs/{}/{}".format(self.namespace, config_id) or \
               "private-build-configs/{}/".format(self.namespace)

    def get_build_history_url(self, history_id=None):
        return history_id and "private-builds/{}/{}".format(self.namespace, history_id) or \
               "private-builds/{}".format(self.namespace)

    def create_build(self, file, data):
        url = self.get_build_config_url()
        data = self.generate_data(file, data)
        return self.send(url, method="POST", data=data)

    def get_build(self, config_id):
        url = self.get_build_config_url(config_id)
        return self.send(url, method="GET")

    def delete_build(self, config_id):
        url = self.get_build_config_url(config_id)
        return self.send(url, method="DELETE")

    def trigger_build(self, config_id):
        url = self.get_build_history_url()
        data = {"build_config_name": config_id}
        params = {"namespace": self.namespace}
        return self.send(url, method="POST", data=data, params=params)

    def get_build_status(self, history_id):
        url = self.get_build_history_url(history_id=history_id)
        return self.get_status(url, 'status', 'S')