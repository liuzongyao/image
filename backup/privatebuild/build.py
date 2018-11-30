from common.base_request import Common


class PrivateBuild(Common):
    def get_build_config_url(self, config_id=None):
        return config_id and "v1/private-build-configs/{}/{}".format(self.account, config_id) or \
               "v1/private-build-configs/{}/".format(self.account)

    def get_build_history_url(self, history_id=None):
        return history_id and "v1/private-builds/{}/{}".format(self.account, history_id) or \
               "v1/private-builds/{}".format(self.account)

    def get_dockerfile_url(self, dockerfile_name=''):
        return "v1/dockerfile/{}/{}".format(self.account, dockerfile_name)

    def create_build(self, file, data):
        url = self.get_build_config_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=url, data=data)

    def get_build(self, config_id):
        url = self.get_build_config_url(config_id)
        return self.send(method="GET", path=url)

    def get_build_list(self):
        path = self.get_build_config_url()
        params = {"project_name": self.project_name, "page_size": 20}
        return self.send(method="GET", path=path, params=params)

    def delete_build(self, build_name):
        config_id = self.get_build_id(build_name)
        url = self.get_build_config_url(config_id)
        return self.send(method="DELETE", path=url)

    def trigger_build(self, config_id):
        url = self.get_build_history_url()
        data = {"build_config_name": config_id}
        params = {"namespace": self.account}
        params.update({"project_name": self.project_name})
        return self.send(method="POST", path=url, json=data, params=params)

    def get_build_status(self, history_id):
        url = self.get_build_history_url(history_id=history_id)
        return self.get_status(url, 'status', 'S')

    def get_build_log(self, history_id):
        url = self.get_build_history_url(history_id=history_id) + '/logs'
        return self.get_logs(url, "Removing the temp dir")

    def get_build_id(self, build_name):
        url = self.get_build_config_url()
        params = {"project_name": self.project_name, "page": 1, "page_size": 20}
        respoonse = self.send(method="GET", path=url, params=params)
        if respoonse.status_code == 200:
            return self.get_uuid_accord_name(respoonse.json().get("results"), {"name": build_name}, "uuid")
        return ""

    def get_ci_image(self):
        path = "v1/ci-envs-catalog"
        return self.send(method='get', path=path)

    def get_ci_yaml(self, file):
        path = "v1/private-build-configs/{}/alaudaci-yaml".format(self.account)
        data = self.generate_data(file_path=file)
        return self.send(method="POST", path=path, data=data)

    def upload_dockerfile(self, data, files):
        path = self.get_dockerfile_url()
        return self.send(method="POST", path=path, data=data, files=files, headers={})

    def get_dockerfile_list(self):
        path = self.get_dockerfile_url()
        return self.send(method="GET", path=path)

    def update_dockerfile(self, dockerfile_name, data, files):
        path = self.get_dockerfile_url(dockerfile_name)
        return self.send(method="PUT", path=path, data=data, files=files, headers={})

    def delete_dockerfile(self, dockerfile_name):
        path = self.get_dockerfile_url(dockerfile_name)
        return self.send(method="DELETE", path=path)

    def get_build_event(self, resource_id, operation):
        path = "v1/events/{}".format(self.account)
        return self.get_events(url=path, resource_id=resource_id, operation=operation)
