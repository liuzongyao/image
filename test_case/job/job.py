from common.base_request import Common
from common.log import logger


class Job(Common):
    def get_job_config_url(self, config_id=None):
        return config_id and "v1/job_configs/{}/{}".format(self.account, config_id) or \
               "v1/job_configs/{}/".format(self.account)

    def get_job_url(self, job_id=None):
        return job_id and "v1/jobs/{}/{}".format(self.account, job_id) or \
               "v1/jobs/{}".format(self.account)

    def get_job_list_url(self, config_id):
        return config_id and "v1/jobs/{}?config_name={}&page=1&page_size=20".format(self.account, config_id)

    def get_job_event_url(self, resource_type, resource_id):
        return "v1/events/{}/{}/{}?pageno=1&size=20".format(self.account, resource_type, resource_id)

    def get_job_events(self, job_id, operation, resource_type):
        url = self.get_job_event_url(resource_type, job_id)
        return self.get_events(url, job_id, operation)

    def create_job_config(self, file, data):
        url = self.get_job_config_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=url, data=data)

    def get_list_jobconfig(self):
        url = self.get_job_config_url("")
        return self.send(method='get', path=url)

    def get_job_config(self, config_id):
        url = self.get_job_config_url(config_id)
        return self.send(method="GET", path=url)

    def update_job_config(self, config_id, file, data):
        logger.info("************************** update job_config ********************************")
        url = self.get_job_config_url(config_id)
        data = self.generate_data(file, data)
        return self.send(method="PUT", path=url, data=data)

    def delete_job_config(self, job_name):
        config_id = self.get_config_id(job_name)
        url = self.get_job_config_url(config_id)
        return self.send(method="DELETE", path=url)

    def trigger_job_config(self, config_id):
        logger.info("************************** trigger job ********************************")
        url = self.get_job_url()
        data = {"config_name": config_id}
        params = {"namespaces": self.account}
        params.update({"project_name": self.project_name})
        return self.send(method="POST", path=url, json=data, params=params)

    def get_list_job(self):
        logger.info("************************** list job history ********************************")
        url = self.get_job_url("")
        return self.send(method='get', path=url)

    def get_job_status(self, job_id, key, expect_status):
        url = self.get_job_url(job_id=job_id)
        return self.get_status(url, key, expect_status)

    def get_job_log(self, job_id, expect_value):
        logger.info("************************** get job log ********************************")
        url = self.get_job_url(job_id=job_id) + '/logs'
        return self.get_logs(url, expect_value)

    def delete_job(self, job_id):
        url = self.get_job_url(job_id)
        return self.send(method="DELETE", path=url)

    def get_job_list(self, config_id, key, expect_value):
        logger.info("************************** get job list ********************************")
        url = self.get_job_list_url(config_id)
        return self.get_status(url, key, expect_value)

    def get_config_id(self, job_name):
        url = self.get_job_config_url()
        params = {"page": 1, "page_size": 20}
        params.update({"project_name": self.project_name})
        response = self.send(method="GET", path=url, params=params)
        assert response.status_code == 200, "get job_config list failed"
        return self.get_uuid_accord_name(response.json().get("results"), {"config_name": job_name}, "config_uuid")
