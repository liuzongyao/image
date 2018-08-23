from common.base_request import Common


class Integrations(Common):
    def common_url(self, integration_id=None):
        return integration_id and "/v1/integrations/{}/{}".format(self.account, integration_id) or \
               "/v1/integrations/{}/".format(self.account)

    def get_integration_list_url(self):
        return "/v1/integrations/{}/?page=1&page_size=200".format(self.account)

    def create_integration(self, file, data):
        path = self.common_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_integration_detail(self, integration_id):
        path = self.common_url(integration_id=integration_id)
        return self.send(method='get', path=path)

    def update_integration(self, integration_id, file, data):
        path = self.common_url(integration_id=integration_id)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data)

    def stop_integration(self, integration_id, file, data):
        path = self.common_url(integration_id=integration_id)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data)

    def delete_integration(self, integration_id):
        path = self.common_url(integration_id=integration_id)
        return self.send(method='delete', path=path)

    def get_integration_id(self, integration_name):
        path = self.get_integration_list_url()
        response = self.send(method='get', path=path)
        if response.status_code == 200:
            contents = response.json()['results']
            return self.get_uuid_accord_name(contents, {"name": integration_name}, 'id')
        return ''
