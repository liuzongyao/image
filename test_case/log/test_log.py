import pytest

from backup.application.app import Application
from test_case.log.log import Log


class TestLogSuite(object):
    def setup_class(self):
        self.log = Log()
        self.log_name = 'alauda-log-{}'.format(self.log.region_name).replace('_', '-')
        self.application = Application()
        self.teardown_class(self)

    def teardown_class(self):
        uuid = self.log.get_saved_search_uuid(self.log_name)
        self.log.delete_saved_search(uuid)

    @pytest.mark.BAT
    def test_log(self):
        '''
        获取日志源-获取查询类型-获取时间统计-日志查询
        创建查询条件-获取条件详情-搜索查询条件-获取查询条件列表-删除查询条件
        :return:
        '''
        result = {"flag": True}
        # get logsource
        logsource_result = self.log.get_logsource()
        result = self.log.update_result(result, logsource_result.status_code == 200, '获取数据源失败')
        # result = self.log.update_result(result, 'default' in logsource_result.text, '获取数据源失败:default不在列表中')
        # get types
        types_result = self.log.get_type()
        result = self.log.update_result(result, types_result.status_code == 200, '获取查询类型失败')
        result = self.log.update_result(result, 'clusters' in types_result.json().keys(), '获取查询类型失败:clusters不在列表中')
        # get aggregations
        aggregation_result = self.log.get_aggregations()
        result = self.log.update_result(result, aggregation_result.status_code == 200, '获取日志统计失败')
        result = self.log.update_result(result, len(aggregation_result.json().get('buckets')) > 0, '获取日志统计失败:数据为空')
        # search log
        self.application.get_service_log(self.log.global_info['$GLOBAL_SERVICE_ID'], 'logglogloglog')
        search_result = self.log.search_log(self.log.global_info['$GLOBAL_SERVICE_ID'])
        result = self.log.update_result(result, search_result.status_code == 200, '按服务查询日志失败')
        result = self.log.update_result(result, search_result.json().get('total_items') > 0, '按服务查询日志失败:日志为空')
        # create saved_search
        create_result = self.log.create_saved_search('./test_data/log/log.json', {'$log_name': self.log_name})
        assert create_result.status_code == 200, "创建日志查询条件失败 {}".format(create_result.text)
        log_id = self.log.get_value(create_result.json(), 'uuid')
        # get saved_search detail
        detail_result = self.log.get_saved_search_detail(log_id)
        result = self.log.update_result(result, detail_result.status_code == 200, '获取日志查询条件详情失败')
        result = self.log.update_result(result, len(detail_result.json().get('query_conditions')) == 3,
                                        '获取日志查询条件详情失败:查询条件个数不是3')
        # search  saved_search
        search_saved = self.log.list_saved_search(self.log_name)
        result = self.log.update_result(result, search_saved.status_code == 200,
                                        '按名称查询日志查询条件失败 {}'.format(search_saved.text))
        result = self.log.update_result(result, len(search_saved.json()) == 1, '按名称查询日志查询条件失败:结果为空')
        # list saved_search
        list_result = self.log.list_saved_search()
        result = self.log.update_result(result, list_result.status_code == 200,
                                        '获取日志查询条件列表失败 {}'.format(list_result.text))
        result = self.log.update_result(result, self.log_name in list_result.text, '获取日志查询条件列表失败:新建日志查询条件不在列表中')
        # delete saved_search
        delete_result = self.log.delete_saved_search(log_id)
        assert delete_result.status_code == 204, "删除日志查询条件失败 {}".format(delete_result.text)
        delete_flag = self.log.check_exists(self.log.get_common_saved_search_url(log_id), 404)
        assert delete_flag, "删除日志查询条件失败"
        assert result['flag'], result
