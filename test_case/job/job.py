from common import settings
from common.base_request import Common
from common.log import logger


class Job(Common):
    def get_job_config_url(self, config_id=None):
        return config_id and "v1/job_configs/{}/{}".format(self.account, config_id) or \
               "v1/job_configs/{}/".format(self.account)

    def get_job_url(self, job_id=None):
        return job_id and "v1/jobs/{}/{}".format(self.account, job_id) or \
               "v1/jobs/{}".format(self.account)

    def get_job_event_url(self, namespace):
        return "v1/events/{}/{}?pageno=1&size=20".format(self.account, namespace)

    def create_job_config(self, file, data):
        url = self.get_job_config_url()
        data = self.generate_data(file, data)
        return self.send(method="POST", path=url, data=data)

    def get_job_events(self, job_id, operation, namespace):
        url = self.get_job_event_url(namespace)
        return self.get_events(url, job_id, operation)

    def get_job_config(self, config_id):
        url = self.get_job_config_url(config_id)
        return self.send(method="GET", path=url)

    def update_job_config(self, file, data):
        url = self.get_job_config_url()
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
        return self.send(method="POST", path=url, json=data, params=params)

    def get_job_status(self, job_id, key, expect_status):
        url = self.get_job_url(job_id=job_id)
        return self.get_status(url, key, expect_status)

    def get_job_log(self, job_id):
        logger.info("************************** get job log ********************************")
        url = self.get_job_url(job_id=job_id) + '/logs'
        return self.get_logs(url, "hello")

    def delete_job(self, job_name):
        job_id = self.get_job_id(job_name)
        url = self.get_job_url(job_id)
        return self.send(method="DELETE", path=url)

    def get_job_id(self, job_name):
        url = self.get_job_url()
        params = {"page": 1, "page_size": 20}
        response = self.send(method="GET", path=url, params=params)
        assert response.status_code == 200, "get job list fail"
        return self.get_uuid_accord_name(response.json().get("results"), {"name": job_name}, "config_uuid")

    def get_config_id(self, job_name):
        url = self.get_job_config_url()
        params = {"page": 1, "page_size": 20}
        response = self.send(method="GET", path=url, params=params)
        assert response.status_code == 200, "get job_config list failed"
        return self.get_uuid_accord_name(response.json().get("results"), {"config_name": job_name}, "config_uuid")
