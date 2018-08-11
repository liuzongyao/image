# coding=utf-8
import requests
from common.log import logger
from common import settings


class AlaudaRequest(object):
    def __init__(self):
        self.endpoint = settings.API_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        self.params = {"project_name": settings.PROJECT_NAME}
        self.account = settings.ACCOUNT
        self.sub_account = settings.SUB_ACCOUNT
        self.region_name = settings.REGION_NAME
        self.password = settings.PASSWORD
        self.registry_name = settings.REGISTRY_NAME
        self.global_info_path = settings.GLOBAL_INFO_FILE
        if self.sub_account:
            self.auth = ("{}/{}".format(self.account, self.sub_account), self.password)
        else:
            self.auth = (self.account, self.password)

    def send(self, method, path, auth=None, **content):
        """
        使用和原生的requests.request一致，只是对url和auth params做了些特殊处理
        :param method:
        :param path:
        :param auth:
        :param content:
        :return:
        """
        url = self._get_url(path)
        if auth:
            content["auth"] = auth
        else:
            content["auth"] = self.auth

        if "headers" in content:
            content["headers"].update(self.headers)
        else:
            content["headers"] = self.headers

        # if content.get("data") is not None and content["headers"]["Content-Type"] == "application/json":
        #     content["json"] = content["data"]
        #     content.pop("data")
        if "params" in content:
            content["params"].update(self.params)
        else:
            content["params"] = self.params

        logger.info("Requesting url={}, method={}, args={}".format(url, method, content))
        response = requests.request(method, url, **content)
        if response.status_code < 200 or response.status_code > 300:
            logger.error("response code={}, text={}".format(response.status_code, response.text))
        else:
            logger.info("response code={}".format(response.status_code))

        return response

    def _get_url(self, path):
        return "{}/{}".format(self.endpoint, path)
