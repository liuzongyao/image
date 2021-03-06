# coding=utf-8
import json
import sys
from time import sleep, time

import pexpect
import requests

from common import settings
from common.api_requests import AlaudaRequest
from common.exceptions import ResponseError, ParseResponseError
from common.loadfile import FileUtils
from common.log import logger


class Common(AlaudaRequest):
    def __init__(self):
        super(Common, self).__init__()
        self.global_info = FileUtils.load_file(self.global_info_path)
        self.final_status = ["S", "F", "Running", "Error", "FAILURE", "failed", "FAIL", "Failed",
                             "CreateError", "StartError"]
        self.region_id = self.global_info.get("$REGION_ID", None)

    def generate_data(self, file_path, data={}):
        """
        对指定文件替换数据，生成最终测试数据
        :param file_path: 指定测试文件路径
        :param data: 需要替换的数据，传入字典类型，key为文件中被替换的内容，value为替换的字符串
        :return: 最终测试数据 类型是字符串
        """
        self.global_info.update(data)
        content = json.dumps(FileUtils.load_file(file_path))
        for key in self.global_info:
            if isinstance(self.global_info[key], str):
                content = content.replace(key, self.global_info[key])
        return content

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
        if json_content == "" or json_content == []:
            raise ResponseError("response content is {}!".format(json_content))

        try:
            for key in query.split(delimiter):
                if isinstance(json_content, list):
                    json_content = json_content[int(key)]
                elif isinstance(json_content, dict):
                    json_content = json_content[key]
                else:
                    raise ParseResponseError(
                        "response content is in text format! failed to query key {}!".format(key))
        except (KeyError, ValueError, IndexError):
            raise ParseResponseError("failed to query json when extracting response! response: {}".format(json_content))

        return json_content

    @staticmethod
    def get_value_list(data, query, delimiter='.'):
        """
        get value from dict or list
        :param data: 需要被解析的数据
        :param keys: 通过这些keys来解析数据,如果字典传key，如果数据传下标
        :example data = {"key1":{"key2":[{"key3":"key4"},{"key3":"key5"}]}}
        期望获取到key4的值 keys = ["key1","key2", 0, "key3"]
        """
        keys = query.split(delimiter)
        if len(keys) > 1:
            value = Common.get_value(data, delimiter.join(keys[0:-1]))
            list_data = value
        else:
            list_data = data
        ret_list = []
        for data in list_data:
            if keys[-1] in data:
                ret_list.append(data[keys[-1]])
        return ret_list

    @staticmethod
    def generate_time_params():
        current_time = int(time())
        return {"start_time": current_time - 1800, "end_time": current_time}

    def get_status(self, url, key, expect_value, delimiter='.', params={"project_name": settings.PROJECT_NAME}):
        """
        :param url: 获取服务或者构建详情的url
        :param key: 获取状态的key 需要是个string，传入层级的key
        :param expect_value:最终判断状态
        :return: true or false
        """
        cnt = 0
        fail_cnt = 0
        flag = False
        while cnt < 120 and not flag:
            cnt += 1
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code == 200, "get status failed"
            value = self.get_value(response.json(), key, delimiter)
            logger.info(value)
            if value == expect_value:
                flag = True
                break
            if value in self.final_status:
                fail_cnt += 1
                if fail_cnt > 2:
                    break
            sleep(5)
        return flag

    def get_logs(self, url, expect_value):
        cnt = 0
        flag = False
        while cnt < 30 and not flag:
            cnt += 1
            params = Common.generate_time_params()
            params.update({"project_name": self.project_name})
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code == 200, "get log failed"
            logger.info("log: {}".format(response.text))
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

    def get_events(self, url, resource_id, operation):
        for i in range(0, 40):
            params = Common.generate_time_params()
            params.update({"project_name": self.project_name, "size": 20, "pageno": 1})
            repsponse = self.send(method='get', path=url, params=params)
            if repsponse.status_code != 200:
                return False
            content = repsponse.json().get("results", [])
            # logger.error("Requesting the api of events, got content{}".format(content))

            for j in range(0, len(content)):
                if content[j].get("resource_id") == resource_id and content[j].get("detail", {}).get(
                        "operation") == operation:
                    return True
            sleep(3)
        return False

    def get_monitor(self, url):
        count = 0
        while count < 40:
            count += 1
            params = Common.generate_time_params()
            params.update({"project_name": self.project_name})
            response = self.send(method='get', path=url, params=params)
            code = response.status_code
            content = response.json()
            if code != 200:
                logger.error("Get monitor failed")
                return False
            if content:
                return True
            sleep(3)
        logger.warning("No monitor were obtained within two minutes, please manually check")
        return False

    def commands(self, ip, service_uuid, pod_instance, app_name):
        if self.sub_account:
            cmd = 'ssh -p 4022 -t {}/{}@{} {}/{}/{}/{} /bin/sh'.format(self.account, self.sub_account, ip,
                                                                       self.account, service_uuid, pod_instance,
                                                                       app_name)
        else:
            cmd = 'ssh -p 4022 -t {}@{} {}/{}/{}/{} /bin/sh'.format(self.account, ip, self.account, service_uuid,
                                                                    pod_instance, app_name)
        return cmd

    def login_container(self, ip, service_uuid, pod_instance, app_name):
        cmd = self.commands(ip, service_uuid, pod_instance, app_name)
        logger.debug("exec command: {}".format(cmd))
        child = pexpect.spawn(cmd)
        ret = child.expect([pexpect.EOF, pexpect.TIMEOUT, 'yes/no', 'password:'])
        if ret == 0:
            logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
            return
        elif ret == 1:
            logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
            return
        elif ret == 2:
            child.sendline('yes')
            rev = child.expect([pexpect.EOF, pexpect.TIMEOUT, 'password:'])
            if rev == 0:
                logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
                return
            elif rev == 1:
                logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                return
            elif rev == 2:
                child.sendline(self.password)
                r = child.expect([pexpect.EOF, pexpect.TIMEOUT, '#'])
                if r == 0:
                    logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
                    return
                elif r == 1:
                    logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                    return
                elif r == 2:
                    return child
        elif ret == 3:
            child.sendline(self.password)
            r = child.expect([pexpect.EOF, pexpect.TIMEOUT, '#'])
            if r == 0:
                logger.error('ssh connect terminated: {}'.format(pexpect.EOF))
                return
            elif r == 1:
                logger.error('ssh connect timeout: {}'.format(pexpect.TIMEOUT))
                return
            elif r == 2:
                return child

    def send_command(self, service_uuid, pod_instance, app_name, command):
        ip = self.global_info['$HAPROXY_IP']
        child = self.login_container(ip, service_uuid, pod_instance, app_name)
        if child:
            child.sendline(command)
            ret = child.expect('#')
            logger.info(child.before)
            return ret

    def check_exists(self, url, expect_status, params={"project_name": settings.PROJECT_NAME}):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            response = self.send(method="GET", path=url, params=params)
            if response.status_code == expect_status:
                flag = True
            sleep(5)
        return flag

    def check_value_in_response(self, url, value, params={"project_name": settings.PROJECT_NAME}):
        '''
        主要用于判断创建后的资源是否在资源列表中，
            个别资源创建后会延时出现在列表中，需要循环获取
        :param url: 获取资源列表的url
        :param value: 资源名称
        :return:
        '''
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            response = self.send(method="GET", path=url, params=params)
            assert response.status_code == 200, "get list failed"
            if value in response.text:
                flag = True
                break
            sleep(5)
        return flag

    def access_jenkins(self):
        jenkins_address = self.global_info.get("$JENKINS_ENDPOINT")
        jenkins_user = self.global_info.get("$JENKINS_USER")
        jenkins_token = self.global_info.get("$JENKINS_TOKEN")
        logger.info("Jenkins url: {}".format(jenkins_address))
        try:
            response = requests.request(method='get', url=jenkins_address, auth=(jenkins_user, jenkins_token))
            if response.status_code == 200:
                return True
        except Exception as e:
            logger.debug(e)
            return False
        return False

    def access_sonar(self):
        sonar_address = self.global_info.get("$SONAR_ENDPOINT")
        logger.info("sonar address: {}".format(sonar_address))

        try:
            response = requests.get(sonar_address)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            return False
        return False

    def access_service(self, service_url, query):
        logger.info("************************** access service ********************************")
        try:
            ret = requests.get(service_url)
            logger.info(ret.text)
            if ret.status_code == 200 and query in ret.text:
                return True
        except Exception as e:
            logger.error("access service failed: {}".format(e))
        return False

    @staticmethod
    def log_info(func: object) -> object:
        def wrapper(*args, **kwargs):
            logger.info(func.__name__.center(50, '*'))
            return func(*args, **kwargs)
        return wrapper
    # def is_weblab_open(self, weblab_name):
    #     weblabs = self.global_info.get("$weblabs")
    #     if isinstance(weblabs, dict) and weblab_name in weblabs.keys() and weblabs[weblab_name]:
    #         return True
    #     else:
    #         return False
