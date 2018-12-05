import random
from common.base_request import Common


class Plugin(Common):
    def get_plugin_list_url(self, region_uuid, is_new_k8s=True):
        return "/v1/plugin-types/{}/?region_uuid={}&is_new_k8s={}".format(self.account, region_uuid, is_new_k8s)

    def get_plugin_detail_url(self, plugin_type):
        return "/v1/plugin-types/{}/{}".format(self.account, plugin_type)

    def get_running_plugin_url(self, plugin_type, region_uuid):
        return "/v1/plugin-types/{}/{}/plugins?region_uuid={}".format(self.account, plugin_type, region_uuid)

    def get_install_plugin_url(self, plugin_type):
        return "/v1/plugin-types/{}/{}/plugins".format(self.account, plugin_type)

    def get_install_plugin_detail_url(self, plugin_type, plugin_uuid):
        return "/v1/plugin-types/{}/{}/plugins/{}?is_new_k8s=true".format(self.account, plugin_type, plugin_uuid)

    def get_plugin_list(self, region_uuid):
        path = self.get_plugin_list_url(region_uuid)
        return self.send(method='get', path=path)

    def get_plugin_detail(self, plugin_type):
        path = self.get_plugin_detail_url(plugin_type)
        return self.send(method='get', path=path)

    def get_running_plugin(self, plugin_type, region_uuid):
        path = self.get_running_plugin_url(plugin_type, region_uuid)
        return self.send(method='get', path=path)

    def install_plugin(self, plugin_type, file, data):
        path = self.get_install_plugin_url(plugin_type)
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_install_plugin_detail(self, plugin_type, plugin_uuid):
        path = self.get_install_plugin_detail_url(plugin_type, plugin_uuid)
        return self.send(method='get', path=path)

    def get_install_plugin_status(self, plugin_type, plugin_uuid, key, expect_value):
        path = self.get_install_plugin_detail_url(plugin_type, plugin_uuid)
        return self.get_status(path, key, expect_value)

    def randstring(self):
        source = 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(random.sample(source, 5))
