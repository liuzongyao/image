from common.base_request import Common


class PrivateBuild(Common):
    def __init__(self):
        super().__init__()

    def get_build_config_url(self, config_id=None):
        return config_id and "private-build-configs/{}/{}".format(self.account, config_id) or \
               "private-build-configs/{}/".format(self.account)

    def get_build_history_url(self, history_id=None):
        return history_id and "private-builds/{}/{}".format(self.account, history_id) or \
               "private-builds/{}".format(self.account)

    def create_build(self, file, data):
        url = self.get_build_config_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=url, data=data)

    def get_build(self, config_id):
        url = self.get_build_config_url(config_id)
        return self.send(method="GET", path=url)

    def delete_build(self, build_name):
        config_id = self.get_build_id(build_name)
        url = self.get_build_config_url(config_id)
        return self.send(method="DELETE", path=url)

    def trigger_build(self, config_id):
        url = self.get_build_history_url()
        data = {"build_config_name": config_id}
        params = {"namespace": self.account}
        return self.send(method="POST", path=url, data=data, params=params)

    def get_build_status(self, history_id):
        url = self.get_build_history_url(history_id=history_id)
        return self.get_status(url, 'status', 'S')

    def get_build_log(self, history_id):
        url = self.get_build_history_url(history_id=history_id) + '/logs'
        return self.get_logs(url, "Removing the temp dir")

    def get_build_id(self, build_name):
        url = self.get_build_config_url()
        respoonse = self.send(method="GET", path=url)
        assert respoonse.status_code == 200, "get build list failed"
        return self.get_uuid_accord_name(respoonse.json(), {"name": build_name}, "uuid")
