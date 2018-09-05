from common.base_request import Common


class Jenkins(Common):
    def common_credentials_url(self, jenkins_integration_id=None):
        return jenkins_integration_id and "/v1/jenkins_pipelines/{}/credentials?jenkins_integration_id={}" \
            .format(self.account, jenkins_integration_id) or "/v1/jenkins_pipelines/{}/credentials" \
            .format(self.account)

    def common_pipelines_url(self, pipeline_uuid=None):
        return pipeline_uuid and "/v1/jenkins_pipelines/{}/pipelines/{}".format(self.account, pipeline_uuid) or \
               "/v1/jenkins_pipelines/{}/pipelines".format(self.account)

    def common_history_url(self, history_uuid=None):
        return history_uuid and "/v1/jenkins_pipelines/{}/history/{}".format(self.account, history_uuid) or \
               "/v1/jenkins_pipelines/{}/history".format(self.account)

    def get_webhook_url(self, webhook_code):
        return "/v1/jenkins_pipelines/{}/history/auto/{}".format(self.account, webhook_code)

    def get_history_record_url(self, jenkins_integration_id):
        return "/v1/jenkins_pipelines/{}/history?jenkins_integration_id={}".format(self.account, jenkins_integration_id)

    def get_history_log_url(self, history_uuid, pipeline_uuid):
        return "/v1/jenkins_pipelines/{}/history/{}/logs?pipeline_uuid={}".format(self.account,
                                                                                  history_uuid, pipeline_uuid)

    def get_history_stage_url(self, history_uuid, pipeline_uuid):
        return "/v1/jenkins_pipelines/{}/history/{}/stages?pipeline_uuid={}".format(self.account, history_uuid,
                                                                                    pipeline_uuid)

    def get_history_stage_step_url(self, history_uuid, stage_id, pipeline_uuid):
        return "/v1/jenkins_pipelines/{}/history/{}/stages/{}/steps?pipeline_uuid={}".format(self.account, history_uuid,
                                                                                             stage_id, pipeline_uuid)

    def get_history_stage_step_log_url(self, history_uuid, stage_id, step_id, pipeline_uuid):
        return "/v1/jenkins_pipelines/{}/history/{}/stages/{}/steps/{}/logs?pipeline_uuid={}" \
            .format(self.account, history_uuid, stage_id, step_id, pipeline_uuid)

    def get_history_stage_step_proceed_url(self, history_uuid, stage_id, step_id, pipeline_uuid):
        return "/v1/jenkins_pipelines/{}/history/{}/stages/{}/steps/{}/proceed?pipeline_uuid={}"\
            .format(self.account, history_uuid, stage_id, step_id, pipeline_uuid)

    def get_history_stage_step_abort_url(self, history_uuid, stage_id, step_id, pipeline_uuid):
        return "/v1/jenkins_pipelines/{}/history/{}/stages/{}/steps/{}/abort?pipeline_uuid={}"\
            .format(self.account, history_uuid, stage_id, step_id, pipeline_uuid)

    def get_template_url(self, official=True):
        return "/v1/jenkins_pipelines/{}/templates?official={}".format(self.account, official)

    def get_pipeline_status_url(self, history_id, pipeline_id):
        return "/v1/jenkins_pipelines/{}/history/{}?pipeline_uuid={}".format(self.account, history_id, pipeline_id)

    def get_cancel_pipeline_url(self, pipeline_id, history_id):
        return "/v1/jenkins_pipelines/{}/history/{}/cancel?pipeline_uuid={}".format(self.account, history_id,
                                                                                    pipeline_id)

    def get_replay_pipeline_url(self):
        return "/v1/jenkins_pipelines/{}/history".format(self.account)

    def get_qualitygates_url(self, sonar_integration_id):
        return "/v1/jenkins_pipelines_integrations/{}/sonar_integration/{}/qualitygates" \
            .format(self.account, sonar_integration_id)

    def get_languages_url(self, sonar_integration_id):
        return "/v1/jenkins_pipelines_integrations/{}/sonar_integration/{}/languages" \
            .format(self.account, sonar_integration_id)

    def common_template_source_url(self, template_source_id=''):
        return template_source_id and "/v1/jenkins_pipelines/{}/template_sources/{}" \
            .format(self.account, template_source_id) or "/v1/jenkins_pipelines/{}/template_sources" \
            .format(self.account)

    def get_template_list_url(self, template_resource_id='', official=True):
        return '/v1/jenkins_pipelines/{}/templates?official={}&source_uuids={}' \
            .format(self.account, official, template_resource_id)

    def get_refresh_template_source_url(self, template_source_id):
        return "/v1/jenkins_pipelines/{}/template_sources/{}/refresh".format(self.account, template_source_id)

    def get_credentials_list(self, jenkins_integration_id):
        path = self.common_credentials_url(jenkins_integration_id=jenkins_integration_id)
        return self.send(method='get', path=path)

    def create_credential(self, file, data):
        path = self.common_credentials_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_credential(self, jenkins_integration_id, credential_name):
        response = self.get_credentials_list(jenkins_integration_id)
        if response.status_code == 200:
            contents = response.json()
            for index, content in enumerate(contents):
                if content['name'] == credential_name:
                    return True
        return False

    def create_pipeline(self, file, data):
        path = self.common_pipelines_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_pipeline_list(self):
        path = self.common_pipelines_url()
        return self.send(method='get', path=path)

    def get_pipeline_detail(self, pipeline_uuid):
        path = self.common_pipelines_url(pipeline_uuid=pipeline_uuid)
        return self.send(method='get', path=path)

    def update_pipeline(self, pipeline_uuid, file, data):
        path = self.common_pipelines_url(pipeline_uuid=pipeline_uuid)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data)

    def get_pipeline_id(self, pipeline_name):
        response = self.get_pipeline_list()
        name = "{}-{}".format(pipeline_name, self.global_info.get("$SPACE_NAME"))
        if response.status_code == 200:
            contents = response.json()['results']
            return self.get_uuid_accord_name(contents, {"name": name}, 'uuid')
        return ''

    def delete_pipeline(self, pipeline_uuid):
        path = self.common_pipelines_url(pipeline_uuid=pipeline_uuid)
        return self.send(method='delete', path=path)

    def execute_pipeline(self, file, data):
        path = self.common_history_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_pipeline_status(self, history_id, pipeline_id, key, expect_value):
        path = self.get_pipeline_status_url(history_id, pipeline_id)
        return self.get_status(path, key, expect_value)

    def get_pipeline_log(self, history_uuid, pipeline_uuid, expect_value="Finished: SUCCESS"):
        path = self.get_history_log_url(history_uuid=history_uuid, pipeline_uuid=pipeline_uuid)
        return self.get_logs(path, expect_value=expect_value)

    def get_pipeline_history_list(self, jenkins_integration_id):
        path = self.get_history_record_url(jenkins_integration_id)
        return self.send(method='get', path=path)

    def get_pipeline_history_detail(self, history_id, pipeline_id):
        path = self.get_pipeline_status_url(history_id, pipeline_id)
        return self.send(method='get', path=path)

    def get_sys_template_list(self):
        path = self.get_template_url()
        return self.send(method='get', path=path)

    def get_sys_template_id(self, name, uuid_key):
        response = self.get_sys_template_list()
        if response.status_code == 200:
            contents = response.json()['results']
            return self.get_uuid_accord_name(contents, {"name": name}, uuid_key=uuid_key)
        return ''

    def pipeline_cancel(self, pipeline_id, history_id):
        path = self.get_cancel_pipeline_url(pipeline_id, history_id)
        return self.send(method='put', path=path)

    def pipeline_replay(self, file, data):
        path = self.get_replay_pipeline_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def check_pipeline_history_exist(self, history_id, pipeline_id, expect_status):
        path = self.get_pipeline_status_url(history_id, pipeline_id)
        return self.check_exists(path, expect_status)

    def check_pipeline_exist(self, pipeline_id, expect_status):
        path = self.common_pipelines_url(pipeline_id)
        return self.check_exists(path, expect_status)

    def delete_pipeline_history(self, history_id, pipeline_id):
        path = self.get_pipeline_status_url(history_id, pipeline_id)
        return self.send(method='delete', path=path)

    def get_sonar_qualitygates(self, sonar_integration_id):
        path = self.get_qualitygates_url(sonar_integration_id)
        return self.send(method='get', path=path)

    def get_languages(self, sonar_integration_id):
        path = self.get_languages_url(sonar_integration_id)
        return self.send(method='get', path=path)

    def get_template_list(self, template_resource_id='', official=True):
        path = self.get_template_list_url(template_resource_id=template_resource_id, official=official)
        return self.send(method='get', path=path)

    def get_template_source_list(self):
        path = self.common_template_source_url()
        return self.send(method='get', path=path)

    def refresh_template_source(self, template_source_id):
        path = self.get_refresh_template_source_url(template_source_id)
        return self.send(method='put', path=path)

    def get_template_source_detail(self, template_source_id):
        path = self.common_template_source_url(template_source_id)
        return self.send(method='get', path=path)

    def get_refresh_template_source_status(self, template_source_id, key, expect_value):
        path = self.common_template_source_url(template_source_id)
        return self.get_status(path, key, expect_value)
