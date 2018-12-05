from common.base_request import Common


class Resources(Common):
    def common_url(self):
        return "/v1/spaces/{}".format(self.account)

    def get_resources_quota_type_url(self):
        return "/v1/spaces/{}/config".format(self.account)

    def space_common_url(self, space_name):
        return "/v1/spaces/{}/space/{}".format(self.account, space_name)

    def get_services_list_url(self, space_name, quota_name):
        return "/v1/spaces/{}/space/{}/quota/{}".format(self.account, space_name, quota_name)

    def get_resources_list_url(self, space_name):
        return "/v1/spaces/{}/space/{}/resources".format(self.account, space_name)

    def get_service_usage_url(self):
        return "/v1/usage/{}".format(self.account)

    def get_export_url(self):
        return "/v1/usage/{}/file-data".format(self.account)

    def get_space_list(self):
        path = self.common_url()
        return self.send(method='get', path=path)

    def create_space(self, file, data):
        path = self.common_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def update_space(self, space_name, file, data):
        path = self.space_common_url(space_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data)

    def delete_space(self, space_name):
        path = self.space_common_url(space_name)
        return self.send(method='delete', path=path)

    def get_space_detail(self, space_name):
        path = self.space_common_url(space_name)
        return self.send(method='get', path=path)

    def get_resources_usage(self, space_name, quota_name):
        path = self.get_services_list_url(space_name, quota_name)
        return self.send(method='get', path=path)

    def get_resources_list(self, space_name):
        path = self.get_resources_list_url(space_name)
        return self.send(method='get', path=path)

    def get_services_usage(self):
        path = self.get_service_usage_url()
        return self.send(method='get', path=path)

    def export_excel(self):
        path = self.get_export_url()
        return self.send(method='get', path=path)

    def check_space_exist(self, space_name, expect_status):
        path = self.space_common_url(space_name)
        return self.check_exists(path, expect_status=expect_status)
