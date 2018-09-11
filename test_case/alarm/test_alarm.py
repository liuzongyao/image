import pytest

from common.log import logger
from test_case.alarm.alarm import Alarm
from test_case.application.app import Application
from test_case.log.log import Log


class TestAlarmSuite(object):
    def setup_class(self):
        self.alarm = Alarm()
        self.metric_alarm_name = 'alauda-metric-alarm-{}'.format(self.alarm.region_name).replace('_', '-')
        self.slaveips = self.alarm.global_info["$SLAVEIPS"].split(",")
        self.application = Application()
        self.log_name = 'alauda-searchforalarm-{}'.format(self.alarm.region_name).replace('_', '-')
        self.log_alarm_name = 'alauda-log-alarm-{}'.format(self.alarm.region_name).replace('_', '-')
        self.log = Log()
        self.teardown_class(self)

    def teardown_class(self):
        uuid = self.alarm.get_alarm_uuid(self.metric_alarm_name)
        self.alarm.delete_alarm(uuid)
        uuid = self.alarm.get_log_alarm_uuid(self.log_alarm_name)
        self.alarm.delete_log_alarm(uuid)
        uuid = self.log.get_saved_search_uuid(self.log_name)
        self.log.delete_saved_search(uuid)

    @pytest.mark.BAT
    def test_metric_alarm(self):
        '''
        创建指标警报-获取警报详情-验证扩容-发送确认-更新指标警报-验证缩容-获取警报列表-删除警报
        :return:
        '''
        result = {"flag": True}
        # get service instance
        svcinstance_before = self.application.get_service_instances(self.alarm.global_info['$GLOBAL_SERVICE_ID'])
        before = 0
        for instance in svcinstance_before.json():
            if self.application.get_value(instance, 'status.phase') == 'Running':
                before += 1
        logger.info(before)
        # create alarm
        create_result = self.alarm.create_alarm('./test_data/alarm/alarm.json', {'$alarm_name': self.metric_alarm_name})
        assert create_result.status_code == 201, "创建指标警报失败 {}".format(create_result.text)
        alarm_id = self.alarm.get_value(create_result.json(), 'uuid')
        # get alarm detail
        detail_result = self.alarm.get_alarm_detail(alarm_id)
        result = self.alarm.update_result(result, detail_result.status_code == 200, '获取指标警报详情失败')
        result = self.alarm.update_result(result,
                                          self.alarm.get_value(detail_result.json(), 'severity_level') == 'minor',
                                          '获取指标警报详情失败:告警级别不是minor')
        alarm_status = self.alarm.get_status(self.alarm.get_alarm_url(alarm_id), 'status', 'ALARM')
        result = self.alarm.update_result(result, alarm_status, '获取指标警报详情失败:状态不是alarm')
        children = self.alarm.get_value(detail_result.json(), 'children')
        result = self.alarm.update_result(result, len(children) >= len(self.slaveips), '获取指标警报详情失败:子警报个数不正确')
        # get service instance
        flag = self.application.get_app_status(self.alarm.global_info['$GLOBAL_APP_ID'], 'resource.status', 'Deploying')
        result = self.alarm.update_result(result, flag, "未触发扩容操作")
        flag = self.application.get_app_status(self.alarm.global_info['$GLOBAL_APP_ID'], 'resource.status', 'Running')
        result = self.alarm.update_result(result, flag, "服务扩容失败")
        svcinstance_after = self.application.get_service_instances(self.alarm.global_info['$GLOBAL_SERVICE_ID'])
        after = 0
        for instance in svcinstance_after.json():
            if self.application.get_value(instance, 'status.phase') == 'Running':
                after += 1
        logger.info(after)
        result = self.alarm.update_result(result, after > before, '服务扩容失败')
        # ack alarm
        data = []
        for c in children:
            data.append({"type": "ack", "alert_key": c.get('alert_key_uuid')})
        ack_result = self.alarm.ack_alarm(alarm_id, data)
        assert ack_result.status_code == 204, "发送确认失败 {}".format(ack_result.text)
        detail_result = self.alarm.get_alarm_detail(alarm_id)
        result = self.alarm.update_result(result,
                                          self.alarm.get_value(detail_result.json(),
                                                               'children.0.actions.ack.status'), '子警报未确认')
        # update alarm
        update_alarm = self.alarm.update_alarm(alarm_id, './test_data/alarm/update_alarm.json',
                                               {'$alarm_name': self.metric_alarm_name,
                                                '$description': self.metric_alarm_name})
        assert update_alarm.status_code == 200, "更新指标警报 {}".format(update_alarm.text)
        alarm_status = self.alarm.get_status(self.alarm.get_alarm_url(alarm_id), 'status', 'ALARM')
        result = self.alarm.update_result(result, alarm_status, '更新指标警报后:状态不是alarm')
        result = self.alarm.update_result(result,
                                          self.alarm.get_status(self.alarm.get_alarm_url(alarm_id), 'severity_level',
                                                                'major'),
                                          '更新指标警报后:告警级别不是major')
        # get service instance
        flag = self.application.get_app_status(self.alarm.global_info['$GLOBAL_APP_ID'], 'resource.status', 'Deploying')
        result = self.alarm.update_result(result, flag, "未触发缩容操作")
        flag = self.application.get_app_status(self.alarm.global_info['$GLOBAL_APP_ID'], 'resource.status', 'Running')
        result = self.alarm.update_result(result, flag, "服务缩容操作")
        svcinstance_final = self.application.get_service_instances(self.alarm.global_info['$GLOBAL_SERVICE_ID'])
        final = 0
        for instance in svcinstance_final.json():
            if self.application.get_value(instance, 'status.phase') == 'Running':
                final += 1
        logger.info(final)
        result = self.alarm.update_result(result, after > final, '服务缩容失败')
        auto_ack = self.alarm.get_status(self.alarm.get_alarm_url(alarm_id), 'children.0.actions.ack.status', True)
        result = self.alarm.update_result(result, auto_ack, '无报警间隔，自动确认失败')
        # list alarm
        list_result = self.alarm.list_alarm()
        result = self.alarm.update_result(result, list_result.status_code == 200,

                                          '获取指标警报列表失败 {}'.format(list_result.text))
        result = self.alarm.update_result(result, self.metric_alarm_name in list_result.text, '获取指标警报列表失败:新建警报不在列表中')
        # delete alarm
        delete_result = self.alarm.delete_alarm(alarm_id)
        assert delete_result.status_code == 204, "删除指标警报失败 {}".format(delete_result.text)
        delete_flag = self.alarm.check_exists(self.alarm.get_alarm_url(alarm_id), 404)
        assert delete_flag, "删除指标警报失败"
        assert result['flag'], result

    @pytest.mark.BAT
    def test_log_alarm(self):
        '''
        创建日志警报-获取警报详情-更新日志警报-获取警报列表-删除警报
        :return:
        '''
        result = {"flag": True}
        # create saved_search
        create_result = self.log.create_saved_search('./test_data/log/log.json', {'$log_name': self.log_name})
        assert create_result.status_code == 200, "创建日志查询条件失败 {}".format(create_result.text)
        saved_search_uuid = self.log.get_value(create_result.json(), 'uuid')

        # create log alarm
        create_result = self.alarm.create_log_alarm('./test_data/alarm/log_alarm.json',
                                                    {'$alarm_name': self.log_alarm_name,
                                                     '$saved_search_uuid': saved_search_uuid})
        assert create_result.status_code == 200, "创建日志警报失败 {}".format(create_result.text)
        alarm_id = self.alarm.get_value(create_result.json(), 'uuid')
        # get alarm detail
        detail_result = self.alarm.get_log_alarm_detail(alarm_id)
        result = self.alarm.update_result(result, detail_result.status_code == 200, '获取日志警报详情失败')
        alarm_status = self.alarm.get_status(self.alarm.get_log_alarm_url(alarm_id), 'status', 'ALARM')
        result = self.alarm.update_result(result, alarm_status, '获取日志警报详情失败:状态不是alarm')
        result = self.alarm.update_result(result, len(
            self.alarm.get_value(detail_result.json(), 'alarm_actions.notifications')) == 1, '获取日志警报详情失败:通知不对')
        # update alarm
        update_alarm = self.alarm.update_log_alarm(alarm_id, './test_data/alarm/update_log_alarm.json',
                                                   {'$alarm_name': self.log_alarm_name,
                                                    '$description': self.metric_alarm_name,
                                                    '$saved_search_uuid': saved_search_uuid})
        assert update_alarm.status_code == 200, "更新日志警报 {}".format(update_alarm.text)
        alarm_status = self.alarm.get_status(self.alarm.get_log_alarm_url(alarm_id), 'status', 'ALARM')
        result = self.alarm.update_result(result, alarm_status, '更新日志警报后:状态不是alarm')
        detail_result = self.alarm.get_log_alarm_detail(alarm_id)
        result = self.alarm.update_result(result, len(
            self.alarm.get_value(detail_result.json(), 'alarm_actions.notifications')) == 0, '更新后获取日志警报详情失败:通知不对')
        # list alarm
        list_result = self.alarm.list_log_alarm()
        result = self.alarm.update_result(result, list_result.status_code == 200,
                                          '获取日志警报列表失败 {}'.format(list_result.text))
        result = self.alarm.update_result(result, self.log_alarm_name in list_result.text, '获取日志警报列表失败:新建警报不在列表中')
        # delete alarm
        delete_result = self.alarm.delete_log_alarm(alarm_id)
        assert delete_result.status_code == 204, "删除日志警报失败 {}".format(delete_result.text)
        delete_flag = self.alarm.check_exists(self.alarm.get_log_alarm_url(alarm_id), 404)
        assert delete_flag, "删除日志警报失败"
        assert result['flag'], result
