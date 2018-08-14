import pytest

from test_case.application.app import Application


@pytest.mark.region
@pytest.mark.new_k8s_app
class TestApplicationSuite(object):
    def setup_class(self):
        self.tool = Application()
        self.app_name = 'e2e-app-{}'.format(self.tool.region_name).replace('_', '-')
        self.app_describe = "e2e-app-describe"

    def teardown_class(self):
        self.tool.delete_app(self.app_name)

    def test_newk8s_app(self):
        result = {"flag": True}
        self.tool.delete_app(self.app_name)
        create_app = self.tool.create_app('./test_data/application/create_app.yml',
                                          {"$app_name": self.app_name, "$description": self.app_describe})
        assert create_app.status_code == 201, create_app.text

        content = create_app.json()
        app_uuid = self.tool.get_value(content, 'resource.uuid')
        service_uuid = self.tool.get_value(content, 'services.0.resource.uuid')

        # get app status
        app_status = self.tool.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "app: {} is not running".format(self.app_name)

        # exec
        pod_instance = self.tool.get_service_instance(service_uuid)
        exec_result = self.tool.exec_container(service_uuid, pod_instance, self.app_name, 'ls')
        result = self.tool.update_result(result, exec_result, "exec")

        # get logs
        log_result = self.tool.get_service_log(service_uuid, 'logglogloglog')
        result = self.tool.update_result(result, log_result, "get service log")

        # get app event
        event_result = self.tool.get_app_events(app_uuid, 'create', self.tool.global_info['$NAMESPACE'])
        result = self.tool.update_result(result, event_result, 'get app event')

        # get monitor
        monitor_result = self.tool.get_app_monitor(app_uuid)
        result = self.tool.update_result(result, monitor_result, "get app monitor")

        # access service
        service_url = self.tool.get_service_url(service_uuid)
        access_result = self.tool.access_service(service_url, "Hello")
        result = self.tool.update_result(result, access_result, "access service")

        # update service
        update_result = self.tool.update_app(app_uuid, './test_data/application/update_app.yml',
                                             {"$app_name": self.app_name,
                                              "$description": self.app_describe})
        # update action success or not
        assert update_result.status_code == 200, update_result.text
        # app is running or not
        app_status = self.tool.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "app: {} is not running".format(self.app_name)
        # update result
        app_describe = self.tool.get_app_status(app_uuid, 'resource.description', self.app_describe)
        assert app_describe, "update app {} failed".format(self.app_name)

        # stop app
        stop_result = self.tool.stop_app(app_uuid)
        assert stop_result.status_code == 200, stop_result.text
        app_status = self.tool.get_app_status(app_uuid, 'resource.status', 'Stopped')
        assert app_status, "app: {} stop failed".format(self.app_name)

        # start app
        start_result = self.tool.start_app(app_uuid)
        assert start_result.status_code == 200, start_result.text
        app_status = self.tool.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "app: {} start failed".format(self.app_name)

        # delete app
        delete_app = self.tool.delete_app(self.app_name)
        assert delete_app.status_code == 204, delete_app.text

        assert result['flag'], result