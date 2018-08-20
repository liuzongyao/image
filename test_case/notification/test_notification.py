# coding=utf-8
from test_case.notification.notification import Notification
from common.log import logger
import pytest

class TestNotiSuite(object):
    def setup_class(self):
        self.noti = Notification()
        self.noti_name = 'alauda-noti-{}'.format(self.noti.region_name).replace('_', '-')
        # 跑之前先删除已经存在的通知
        noti_id = self.noti.get_noti_id_from_list(self.noti_name)
        self.noti.delete_noti(noti_id)

    def teardown_class(self):
        noti_id = self.noti.get_noti_id_from_list(self.noti_name)
        self.noti.delete_noti(noti_id)

    @pytest.mark.BAT
    def test_noti(self):
        final_result = {"flag": True}

        create_result = self.noti.create_noti('./test_data/notification/notification.json',
                                              {"$noti_name": self.noti_name, "$email": "test@alauda.io"})
        assert create_result.status_code == 201, create_result.text

        noti_id = create_result.json().get("uuid")

        list_result = self.noti.get_noti_list()
        self.noti.update_result(final_result, list_result.status_code==200, list_result.text)
        self.noti.update_result(final_result, self.noti_name in list_result.text, "创建的通知不在列表中")

        new_email = "testing@alauda.io"
        update_result = self.noti.update_noti(noti_id, './test_data/notification/notification.json',
                                              {"$email": new_email})
        self.noti.update_result(final_result, update_result.status_code == 200, list_result.text)

        get_detail_result = self.noti.get_noti_detail(noti_id)
        self.noti.update_result(final_result, get_detail_result.status_code == 200, get_detail_result.text)
        self.noti.update_result(final_result, new_email in get_detail_result.text, "更新后的通知内容不在通知详情页面")

        delete_result = self.noti.delete_noti(noti_id)
        assert delete_result.status_code == 204, delete_result.text

        #验证非block的结果
        assert final_result.get("flag"), final_result





