# coding=utf-8
import os
import json
from requests.structures import CaseInsensitiveDict
from common.api_requests import AlaudaRequest
from common import settings
from common.log import logger
from time import sleep, time
from common.exceptions import ResponseError, ParseResponseError


class Common(AlaudaRequest):
    def __init__(self):
        super(Common, self).__init__()
        print(self.region_name)
        self.region_data = {}
        self.build_endpointid = ''
        self.region_id = ''

        self.final_status = ["S", "F", "Running", "Error"]

    @staticmethod
    def get_value(json_content, query, delimiter='.'):
        """ Do an xpath-like query with json_content.
        @param (json_content) json_content
            json_content = {
                "ids": [1, 2, 3, 4],
                "person": {
                    "name": {
                        "first_name": "Leo",
                        "last_name": "Lee",
                    },
                    "age": 29,
                    "cities": ["Guangzhou", "Shenzhen"]
                }
            }
        @param (str) query
            "person.name.first_name"  =>  "Leo"
            "person.cities.0"         =>  "Guangzhou"
        @return queried result
        """
        if json_content == "":
            raise ResponseError("response content is empty!")

        try:
            for key in query.split(delimiter):
                if isinstance(json_content, list):
                    json_content = json_content[int(key)]
                elif isinstance(json_content, (dict, CaseInsensitiveDict)):
                    json_content = json_content[key]
                else:
                    raise ParseResponseError(
                        "response content is in text format! failed to query key {}!".format(key))
        except (KeyError, ValueError, IndexError):
            raise ParseResponseError("failed to query json when extracting response! response: {}".format(json_content))

        return json_content

    @staticmethod
    def get_value_list(data, keys):
        """
        get value from dict or list
        :param data: 需要被解析的数据
        :param keys: 通过这些keys来解析数据,如果字典传key，如果数据传下标
        :example data = {"key1":{"key2":[{"key3":"key4"},{"key3":"key5"}]}}
        期望获取到key4的值 keys = ["key1","key2", 0, "key3"]
        """
        if len(keys) > 1:
            flag, value = Common.get_value(data, keys[0:-1])
            assert flag, value
            list_data = value
        else:
            list_data = data
        ret_list = []
        for data in list_data:
            if keys[-1] in data:
                ret_list.append(data[keys[-1]])
        return ret_list

    def generate_time_params(self):
        current_time = int(time())
        return {"start_time": current_time - 1800, "end_time": current_time}

    def get_status(self, url, key, expect_value):
        """
        :param url: 获取服务或者构建详情的url
        :param key: 获取状态的key 需要是个string，传入层级的key
        :param expect_value:最终判断状态
        :return: true or false
        """
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            response = self.send(method="GET", path=url)
            assert response.status_code == 200, "get status failed"
            value = self.get_value(response.json(), key)
            if value == expect_value:
                flag = True
                break
            if value in self.final_status:
                break
            sleep(5)
        return flag

    def get_logs(self, url, expect_value):
        cnt = 0
        flag = False
        while cnt < 30 and not flag:
            cnt += 1
            params = self.generate_time_params()
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code == 200, "get log failed"
            if expect_value in response.text:
                flag = True
                break
            sleep(5)
        return flag

    def get_uuid_accord_name(self, contents, name, uuid_key):
        """
        方法丑陋 欢迎指正
        :param contents: 通过返回体获取到的列表数组 [{"key":""value"...},{"key":""value"...}...]
        :param name: 资源名称的一个字典:{"name": "resource_name"}
        :param uuid_key: 资源uuid的key
        :return: 资源的uuid
        """
        for content in contents:
            for key, value in name.items():
                if content[key] == value:
                    return content[uuid_key]
        return ""

    def update_result(self, result, flag, case_name):
        """
        如果是非block的验证点，先将结果更新到result内，在最后判断case的执行结果
        :param result: 最终用来判断case执行成功与失败的集合 :{"flag":True/False, case_name: "failed"}
        :param flag: True/False
        :param error_name: case的名称
        :return: result
        """
        if not flag:
            result['flag'] = False
            result.update({case_name: "failed"})
        return result

    def get_events(self, resource_id, operation):
        for i in range(0, 40):
            end_time = round(time(), 6)
            start_time = end_time - 3600

            url = "/v1/events/{}/?start_time={}&end_time={}&pageno=1&size=100&namespace={}&project_name={}".format(
                settings.ACCOUNT, start_time, end_time, settings.NAMESPACE, settings.PROJECT_NAME)

            logger.debug("request event url: {}".format(url))
            r = self.send(method='get', path=url)
            if r.status_code != 200:
                return False
            content = json.loads(r.text).get("results", [])
            # logger.debug("Requesting the api of events, got content{}".format(content))

            for j in range(0, len(content)):
                if content[j].get("resource_id") == resource_id and content[j].get("detail", {}).get(
                        "operation") == operation:
                    return True
            sleep(3)
        return False