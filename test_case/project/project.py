from common.base_request import Common


class Project(Common):
    def get_project_config_url(self, project_name=None):
        return project_name and "v1/projects/{}/{}".format(self.account, project_name) or \
               "v1/projects/{}/".format(self.account)

    def get_project_resources(self, project_name):
        path = self.get_project_config_url(project_name)
        return self.send(method='get', path=path)

    def create_project(self, file, data):
        path = self.get_project_config_url()
        data = self.generate_data(file, data)
        return self.send(method='POST', path=path, data=data)

    def delete_project(self, project_name):
        path = self.get_project_config_url(project_name)
        return self.send(method='DELETE', path=path)
