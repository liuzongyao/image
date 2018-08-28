from common.base_request import Common


class Project(Common):
    def get_project_config_url(self, project_name=None):
        return project_name and "v1/projects/{}/{}".format(self.account, project_name) or \
               "v1/projects/{}/".format(self.account)

    def get_project_role_url(self):
        return "/v1/roles/{}/".format(self.account)

    def delete_project_role_url(self, role_name):
        return "/v1/roles/{}/{}/".format(self.account, role_name)

    def get_project_role(self, project_name):
        if self.get_project(project_name).status_code != 200:
            return []
        path = self.get_project_role_url()
        response = self.send(method='get', path=path, params={"project_name": project_name})
        role_list = []
        assert response.status_code == 200, response.text
        contents = response.json()['results']
        for i in range(len(contents)):
            role_list.append(contents[i]['name'])
        return role_list

    def get_project(self, project_name):
        path = self.get_project_config_url(project_name=project_name)
        return self.send(method='get', path=path)

    def get_project_list(self):
        path = self.get_project_config_url()
        return self.send(method='get', path=path)

    def update_project(self, project_name, data):
        path = self.get_project_config_url(project_name)
        return self.send(method='put', path=path, json=data)

    def create_project(self, file, data):
        path = self.get_project_config_url()
        data = self.generate_data(file, data)
        return self.send(method='POST', path=path, data=data)

    def delete_project_role(self, project_name):
        ret = self.get_project_role(project_name)
        for i in range(len(ret)):
            path = self.delete_project_role_url(ret[i])
            self.send(method='DELETE', path=path)

    def delete_project(self, project_name):
        path = self.get_project_config_url(project_name)
        return self.send(method='DELETE', path=path)
