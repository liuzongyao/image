from time import sleep

import pytest

from test_case.application.app import Application


@pytest.mark.region
@pytest.mark.new_k8s_app
class TestApplicationSuite(object):
    def setup_class(self):
        self.application = Application()
        self.app_name = 'e2e-app-{}'.format(self.application.region_name).replace('_', '-')
        self.app_describe = "e2e-app-describe"

    def teardown_class(self):
        self.application.delete_app(self.app_name)

    def test_newk8s_app(self):
        result = {"flag": True}
        self.application.delete_app(self.app_name)
        create_app = self.application.create_app('./test_data/application/create_app.yml', {"$app_name": self.app_name})
        assert create_app.status_code == 201, create_app.text

        content = create_app.json()
        app_uuid = self.application.get_value(content, 'resource.uuid')
        service_uuid = self.application.get_value(content, 'services.0.resource.uuid')

        # get app status
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "app: {} is not running".format(self.app_name)

        # get app detail
        detail_result = self.application.get_app_detail(app_uuid)
        result = self.application.update_result(result, detail_result.status_code == 200, 'get app detail failed')
        app_describe = self.application.get_app_status(app_uuid, 'resource.description', "$description")
        result = self.application.update_result(result, app_describe, 'get app detail  error')

        # list app
        list_result = self.application.list_app()
        result = self.application.update_result(result, list_result.status_code == 200, 'list app failed')
        result = self.application.update_result(result, self.app_name in list_result.text, 'list app error')

        # get app yaml
        appyaml_result = self.application.get_app_yaml(app_uuid)
        result = self.application.update_result(result, appyaml_result.status_code == 200, 'get app yaml failed')
        result = self.application.update_result(result, "Deployment" in appyaml_result.text, 'get app yaml error')

        # get app event
        event_result = self.application.get_app_events(app_uuid, 'create', self.application.global_info['$NAMESPACE'])
        result = self.application.update_result(result, event_result, 'get app event')

        # get app monitor
        monitor_result = self.application.get_app_monitor(app_uuid)
        result = self.application.update_result(result, monitor_result, "get app monitor")

        # exec
        pod_instance = self.application.get_service_instance(service_uuid)
        exec_result = self.application.exec_container(service_uuid, pod_instance, self.app_name, 'ls')
        result = self.application.update_result(result, exec_result, "exec")

        # get logs
        log_result = self.application.get_service_log(service_uuid, 'logglogloglog')
        result = self.application.update_result(result, log_result, "get service log")

        # get service  monitor
        monitorsvc_result = self.application.get_service_monitor(service_uuid)
        result = self.application.update_result(result, monitorsvc_result, "get service monitor")

        # access service
        service_url = self.application.get_service_url(service_uuid)
        access_result = self.application.access_service(service_url, "Hello")
        result = self.application.update_result(result, access_result, "access service")

        # get service instances
        svcinstance_result = self.application.get_service_instances(service_uuid)
        assert svcinstance_result.status_code == 200, svcinstance_result.text
        assert len(svcinstance_result.json()) == 1, "get service instances"

        # pod rebuild
        rebuild_result = self.application.rebuild_pod(self.application.global_info["$REGION_ID"],
                                                      self.application.global_info['$K8S_NAMESPACE'],
                                                      pod_instance)
        assert rebuild_result.status_code == 204, rebuild_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "service: {} rebuild failed".format(self.app_name)

        # update service
        updatesvc_result = self.application.update_service(service_uuid, './test_data/application/update_service.yml',
                                                           {"$app_name": self.app_name})
        assert updatesvc_result.status_code == 200, updatesvc_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "service: {} update failed".format(self.app_name)

        # get service yaml
        svcyaml_result = self.application.get_service_yaml(service_uuid)
        result = self.application.update_result(result, svcyaml_result.status_code == 200, "get service yaml failed")
        result = self.application.update_result(result, "updateservice" in svcyaml_result.text, "get svc yaml error")
        result = self.application.update_result(result, "livenessProbe" in svcyaml_result.text, "get svc yaml error")

        # get service log source
        service_log_source = self.application.get_service_log_source(service_uuid)
        service_log_source_result = True if "hehe.txt" in service_log_source.json() else False
        result = self.application.update_result(result, service_log_source_result, "get service log source")

        # stop service
        stopsvc_result = self.application.stop_service(service_uuid)
        assert stopsvc_result.status_code == 200, stopsvc_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Stopped')
        assert app_status, "app: {} stop failed".format(self.app_name)

        # start service
        startsvc_result = self.application.start_service(service_uuid)
        assert startsvc_result.status_code == 200, startsvc_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "service: {} start failed".format(self.app_name)

        # rollbackto1
        roll1_result = self.application.rollback_service_toversion(service_uuid)
        assert roll1_result.status_code == 204, roll1_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "service: {} rollbacktoversion failed".format(self.app_name)
        sleep(5)
        svcyaml_result = self.application.get_service_yaml(service_uuid)
        result = self.application.update_result(result, svcyaml_result.status_code == 200,
                                                "after rollback,get yaml failed")
        result = self.application.update_result(result, "updateservice" not in svcyaml_result.text,
                                                "after rollback ,get service yaml error")

        # rollback
        roll_result = self.application.rollback_service(service_uuid)
        assert roll_result.status_code == 204, roll_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "service: {} rollback failed".format(self.app_name)

        # stop app
        stop_result = self.application.stop_app(app_uuid)
        assert stop_result.status_code == 200, stop_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Stopped')
        assert app_status, "app: {} stop failed".format(self.app_name)

        # start app
        start_result = self.application.start_app(app_uuid)
        assert start_result.status_code == 200, start_result.text
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "app: {} start failed".format(self.app_name)

        # update app
        update_result = self.application.update_app(app_uuid, './test_data/application/update_app.yml',
                                                    {"$app_name": self.app_name,
                                                     "$description": self.app_describe})
        # update action success or not
        assert update_result.status_code == 200, update_result.text
        # app is running or not
        app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
        assert app_status, "app: {} is not running".format(self.app_name)
        # update result
        app_describe = self.application.get_app_status(app_uuid, 'resource.description', self.app_describe)
        assert app_describe, "update app {} failed".format(self.app_name)

        # delete service
        deletesvc_result = self.application.delete_service(service_uuid)
        assert deletesvc_result.status_code == 204, deletesvc_result.text
        delete_flag = self.application.check_exists(self.application.get_common_service_url(service_uuid), 404)
        assert delete_flag, "delete service failed"

        # antiaffinity
        slaveips = self.application.global_info["$SLAVEIPS"].split(",")
        if len(slaveips) > 1:
            update_result = self.application.update_app(app_uuid, './test_data/application/update_app_affinity.yml',
                                                        {"$app_name": self.app_name,
                                                         "$description": self.app_describe})
            assert update_result.status_code == 200, update_result.text
            app_status = self.application.get_app_status(app_uuid, 'resource.status', 'Running')
            assert app_status, "app: {} is not running".format(self.app_name)

            svc1_id = self.application.get_service_uuid(app_uuid)
            svc1instance_result = self.application.get_service_instances(svc1_id)
            assert svc1instance_result.status_code == 200, svc1instance_result.text
            svc1_ip = svc1instance_result.json()[0].get("status").get("hostIP")

            svc2_id = self.application.get_service_uuid(app_uuid, key='services.1.resource.uuid')
            svc2instance_result = self.application.get_service_instances(svc2_id)
            assert svc2instance_result.status_code == 200, svc2instance_result.text
            svc2_ip = svc2instance_result.json()[0].get("status").get("hostIP")
            assert svc1_ip != svc2_ip, "app antiaffinity failed"

        # delete app
        delete_app = self.application.delete_app(self.app_name)
        assert delete_app.status_code == 204, delete_app.text
        delete_flag = self.application.check_exists(self.application.app_common_url(app_uuid), 404)
        assert delete_flag, "delete app failed"

        assert result['flag'], result
