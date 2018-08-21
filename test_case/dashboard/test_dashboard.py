from test_case.dashboard.dashboard import Dashboard
import pytest


@pytest.mark.BAT
class TestDashboard(object):
    def setup_class(self):
        self.dashboard = Dashboard()
        self.dashboard_name = "alauda-dashboard-{}".format(self.dashboard.region_name).replace('_', '-')
        self.chart_name = "alauda-chart-{}".format(self.dashboard.region_name).replace('_', '-')
        self.teardown_class(self)

    def teardown_class(self):
        dashboard_id = self.dashboard.get_dashboard_id(self.dashboard_name)
        self.dashboard.delete_dashboard(dashboard_id)

    def test_dashboard(self):
        final_result = {"flag": True}
        create_ret = self.dashboard.create_dashboard("./test_data/dashboard/create_dashboard.json",
                                                     {"$dashboard_name": self.dashboard_name})
        assert create_ret.status_code == 200, create_ret.text

        list_ret = self.dashboard.get_dashboard_list()
        self.dashboard.update_result(final_result, list_ret.status_code == 200, list_ret.text)
        self.dashboard.update_result(final_result, self.dashboard_name in list_ret.text, "新建的面板不在列表内")

        dashboard_id = self.dashboard.get_dashboard_id(self.dashboard_name)
        update_ret = self.dashboard.update_dashboard(dashboard_id, "./test_data/dashboard/create_dashboard.json",
                                                     {"$dashboard_name": self.dashboard_name})
        self.dashboard.update_result(final_result, update_ret.status_code == 200, update_ret.text)

        # node metrcis
        chart_data = {
            "metrics": [{
                "$metric": "node.cpu.system",
                "$group_by": "host",
                "$aggregator": "avg"
            }],
            "$chart_name": self.chart_name
        }
        create_ret = self.dashboard.create_chart(dashboard_id, "./test_data/dashboard/create_chart.json", chart_data)
        assert create_ret.status_code == 200, create_ret.text

        query_string = "avg:node.cpu.system{region_name=" + self.dashboard.region_name + "}by{host}"
        metrics_ret = self.dashboard.get_chart(params={"q": query_string})
        self.dashboard.update_result(final_result, metrics_ret.status_code == 200, metrics_ret.text)
        self.dashboard.update_result(final_result, len(self.dashboard.get_value(metrics_ret.json(), "0.dps")) > 0,
                                     metrics_ret.text)

        # comp metrics
        chart_data = {
            "metrics": [{
                "$metric": "comp.dd_agent.status",
                "$group_by": "host",
                "$aggregator": "min"
            }],
            "$chart_name": self.chart_name
        }
        create_ret = self.dashboard.create_chart(dashboard_id, "./test_data/dashboard/create_chart.json", chart_data)
        assert create_ret.status_code == 200, create_ret.text

        query_string = "min:comp.dd_agent.status{region_name=" + self.dashboard.region_name + "}by{host}"
        metrics_ret = self.dashboard.get_chart(params={"q": query_string})
        self.dashboard.update_result(final_result, metrics_ret.status_code == 200, metrics_ret.text)
        self.dashboard.update_result(final_result, len(self.dashboard.get_value(metrics_ret.json(), "0.dps")) > 0,
                                     metrics_ret.text)

        # service metrics
        chart_data = {
            "metrics": [{
                "$metric": "service.cpu.system",
                "$group_by": "region_name, service_name",
                "$aggregator": "max"
            }],
            "$chart_name": self.chart_name
        }
        create_ret = self.dashboard.create_chart(dashboard_id, "./test_data/dashboard/create_chart.json", chart_data)
        assert create_ret.status_code == 200, create_ret.text

        query_string = "max:service.cpu.system{region_name=" + self.dashboard.region_name + "}by{host}"
        metrics_ret = self.dashboard.get_chart(params={"q": query_string})
        self.dashboard.update_result(final_result, metrics_ret.status_code == 200, metrics_ret.text)
        self.dashboard.update_result(final_result, len(self.dashboard.get_value(metrics_ret.json(), "0.dps")) > 0,
                                     metrics_ret.text)

        chart_id = self.dashboard.get_value(create_ret.json(), "data.uuid")

        detail_ret = self.dashboard.get_dashboard(dashboard_id)
        self.dashboard.update_result(final_result, detail_ret.status_code == 200, detail_ret.text)
        self.dashboard.update_result(final_result, len(self.dashboard.get_value(detail_ret.json(), "data.charts")) == 3,
                                     "面板内图标数量应该为3个，结果却不是")

        del_ret = self.dashboard.delete_chart(dashboard_id, chart_id)
        self.dashboard.update_result(final_result, del_ret.status_code == 204, del_ret.text)

        del_ret = self.dashboard.delete_dashboard(dashboard_id)
        assert del_ret.status_code == 204, del_ret.text

        check_flag = self.dashboard.check_exists(self.dashboard.get_dashboard_url(dashboard_id), 404)
        assert check_flag, "delete dashboard failed"

        # 校验非block结果
        assert final_result.get("flag"), final_result
