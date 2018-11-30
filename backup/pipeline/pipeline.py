from common.base_request import Common


class Pipeline(Common):
    def pipeline_common_url(self, pipeline_uuid=None):
        return pipeline_uuid and "/v1/pipelines/{}/config/{}".format(self.account, pipeline_uuid) or \
               "/v1/pipelines/{}/config".format(self.account)

    def pipeline_history_common_url(self, pipeline_id=None):
        return pipeline_id and "/v1/pipelines/{}/history/{}".format(self.account, pipeline_id) or \
               "/v1/pipelines/{}/history".format(self.account)

    def get_pipeline_history_list_url(self, pipeline_id):
        return "/v1/pipelines/{}/history?pipeline_uuid={}".format(self.account, pipeline_id)

    def get_pipeline_history_detail_or_delete_url(self, pipeline_id, history_id):
        return "/v1/pipelines/{}/history/{}/{}".format(self.account, pipeline_id, history_id)

    def get_stop_pipeline_url(self, pipelien_id, history_id):
        return "/v1/pipelines/{}/history/{}/{}/stop".format(self.account, pipelien_id, history_id)

    def get_pipeline_history_log_url(self, pipelien_id, history_id):
        return "/v1/pipelines/{}/history/{}/{}/logs".format(self.account, pipelien_id, history_id)

    def upload_artifacts_url(self, build_id):
        return "/v1/oss/{}/?prefix=build/{}".format(self.account, build_id)

    def download_artifacts_url(self, pipeline_id, history_id):
        return "/v1/oss/{}/?prefix=pipeline/{}/{}".format(self.account, pipeline_id, history_id)

    def get_pipeline_task_log_url(self, pipeline_id, history_id, task_id):
        return "/v1/pipelines/{}/history/{}/{}/tasks/{}/logs".format(self.account, pipeline_id, history_id, task_id)

    def get_pipeline_task_id_url(self, pipeline_id, history_id):
        return "/v1/pipelines/{}/history/{}/{}/tasks".format(self.account, pipeline_id, history_id)

    def create_pipeline(self, file, data):
        path = self.pipeline_common_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_pipeline_detail(self, pipeline_id):
        path = self.pipeline_common_url(pipeline_id)
        return self.send(method='get', path=path)

    def get_pipeline_list(self):
        path = self.pipeline_common_url()
        return self.send(method='get', path=path)

    def update_pipeline(self, pipeline_id, file, data):
        path = self.pipeline_common_url(pipeline_id)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data)

    def delete_pipeline(self, pipeline_id):
        path = self.pipeline_common_url(pipeline_id)
        return self.send(method='delete', path=path)

    def get_history_list(self):
        path = self.pipeline_history_common_url()
        return self.send(method='get', path=path)

    def get_pipeline_history_list(self, pipeline_id):
        path = self.pipeline_history_common_url(pipeline_id)
        return self.send(method='get', path=path)

    def start_pipeline(self, pipeline_id, file, data):
        path = self.pipeline_history_common_url(pipeline_id)
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data)

    def get_pipeline_history_detail(self, pipeline_id, history_id, key, expect_value):
        path = self.get_pipeline_history_detail_or_delete_url(pipeline_id, history_id)
        return self.get_status(path, key, expect_value)

    def delete_pipeline_history(self, pipeline_id, history_id):
        path = self.get_pipeline_history_detail_or_delete_url(pipeline_id, history_id)
        return self.send(method='delete', path=path)

    def stop_pipeline(self, pipeline_id, history_id):
        path = self.get_stop_pipeline_url(pipeline_id, history_id)
        return self.send(method='put', path=path)

    def get_pipeline_logs(self, pipeline_id, history_id, expect_value="Pipeline completed successfully"):
        path = self.get_pipeline_history_log_url(pipeline_id, history_id)
        return self.get_logs(path, expect_value)

    def get_pipeline_id(self, pipeline_name, uuid_key):
        response = self.get_pipeline_list()
        if response.status_code == 200:
            contents = response.json()['results']
            return self.get_uuid_accord_name(contents, {"name": pipeline_name}, uuid_key)
        return ""

    def check_pipeline_exist(self, pipeline_id, expect_status):
        path = self.pipeline_common_url(pipeline_id)
        return self.check_exists(path, expect_status)

    def check_pipeline_history_exist(self, pipeline_id, history_id, expect_status):
        path = self.get_pipeline_history_detail_or_delete_url(pipeline_id, history_id)
        return self.check_exists(path, expect_status)

    def get_upload_artifacts_result(self, build_id, params=''):
        path = self.upload_artifacts_url(build_id)
        return self.send(method='get', path=path, params=params)

    def get_download_artifacts_result(self, pipeline_id, history_id, params=''):
        path = self.download_artifacts_url(pipeline_id, history_id)
        return self.send(method='get', path=path, params=params)

    def get_pipeline_task_logs(self, pipeline_id, history_id, task_id, expect_value=""):
        path = self.get_pipeline_task_log_url(pipeline_id, history_id, task_id)
        return self.get_logs(path, expect_value)

    def get_pipeline_task_id(self, pipeline_id, history_id):
        path = self.get_pipeline_task_id_url(pipeline_id, history_id)
        return self.send(method='get', path=path)
