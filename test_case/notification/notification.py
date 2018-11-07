# coding=utf-8
from common.base_request import Common


class Notification(Common):
    # 获取通知URL
    def get_noti_url(self, noti_id=None):
        return noti_id and "v1/notifications/{}/{}".format(self.account, noti_id) or \
               "v1/notifications/{}/".format(self.account)

    # 创建通知
    def create_noti(self, file_path, data):
        url = self.get_noti_url()
        data = self.generate_data(file_path, data)
        return self.send(method="post", path=url, data=data, params={})

    # 根据通知列表获取通知id
    def get_noti_id_from_list(self, noti_name):
        r = self.get_noti_list().json()
        return self.get_uuid_accord_name(r, {"name": noti_name}, "uuid")

    # 获取通知详情
    def get_noti_detail(self, noti_id):
        url = self.get_noti_url(noti_id)
        return self.send(method="get", path=url, params={})

    # 获取通知列表
    def get_noti_list(self):
        url = self.get_noti_url()
        return self.send(method="get", path=url, params={})

    # 更新通知
    def update_noti(self, noti_id, file_path, data):
        url = self.get_noti_url(noti_id)
        data = self.generate_data(file_path, data)
        return self.send(method="put", path=url, data=data, params={})

    # 删除通知
    def delete_noti(self, noti_id):
        url = self.get_noti_url(noti_id)
        return self.send(method="delete", path=url, params={})
