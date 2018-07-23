# coding=utf-8
from common.api_requests import AlaudaRequest
from common.logging import Logging
from common import settings
import os
from time import sleep, time
from common.utils import retry

logger = Logging.get_logger()


class Common(AlaudaRequest):
    def __init__(self):
        super().__init__()
        print(self.region_name)
        self.tmp_dir = "./temp_data/"
        self.region_data = {}
        self.build_endpointid = ''
        self.region_id = ''
        self.get_region_data()
        self.get_build_endpontid()
        self.common_data = {
            "$NAMESPACE": self.account,
            "$REGION_ID": self.region_id,
            "$BUILD_ENDPOINT_ID": self.build_endpointid,
            "$SVN_REPO_PASSWORD": settings.SVN_REPO_PASSWORD,
            "$SVN_REPO_USERNAME": settings.SVN_REPO_USERNAME,
            "$SVN_REPO": settings.SVN_REPO,
            "$REGISTRY": self.registry_name,
            "$REPO_NAME": settings.REPO_NAME,
            "$SPACE_NAME": settings.SPACE_NAME
        }
        self.generate_all_data("./test_data/", self.common_data)
        self.final_status = ["S", "F", "Running", "Error"]

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        response = self.send(method="GET", path="regions/{}/{}/".format(self.account, self.region_name))
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        flag, self.region_id = self.get_value(self.region_data, ["id"])
        assert flag, self.region_id

    @retry()
    def get_build_endpontid(self):
        """
        :return: 给self.build_endpoint赋值构建的集群ID
        """
        response = self.send(method="GET", path="private-build-endpoints/{}".format(self.account))
        assert response.status_code == 200, response.text
        for content in response.json():
            if content['region_id'] == self.region_id:
                self.build_endpointid = content['endpoint_id']
                break

    def get_node_info(self):
        """
        get region all node tag and private ip
        """
        return

    @staticmethod
    def get_value(data, keys):
        """
        get value from dict or list
        :param data: 需要被解析的数据
        :param keys: 通过这些keys来解析数据,如果字典传key，如果数据传下标
        :example data = {"key1":{"key2":[{"key3":"key4"},{"key3":"key5"}]}}
        期望获取到key4的值 keys = ["key1","key2", 0, "key3"]
        """
        value = data
        msg = "use keys: {} to get data: {}  value,but failed".format(keys, data)
        result = False, msg
        if not len(keys):
            return result
        for key in keys:
            if not value:
                return False, "value is {}".format(value)
            if isinstance(key, str) and isinstance(value, dict) and key not in value:
                return False, "key :{} is not in data:{}".format(key, value)
            if isinstance(key, int) and isinstance(value, list) and len(value) < key + 1:
                return False, "list:{} len is {}, but index is {}".format(value, len(value), key)
            value = value[key]
            logger.debug("get value is {}".format(value))
        return True, value

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

    def generate_all_data(self, path, data):
        """
        通过遍历测试数据的目录，生成临时的测试数据，替换掉一些公共的数据，如region region_id等等
        :param path: 指定测试数据的目录
        :param data: 需要替换的数据，传入字典类型，key为文件中被替换的内容，value为替换的字符串
        :return: 生成临时数据
        """
        filenames = []
        tmp_dir = self.tmp_dir
        for root, dirs, files in os.walk(path):
            for file in files:
                filenames.append(os.path.join(root, file))
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        for filename in filenames:
            to_file = os.path.join(tmp_dir, file.split("/")[-1])
            with open(filename, "r") as fp:
                content = fp.read()
            for key in data:
                content = content.replace(key, data[key])
            with open(to_file, "w") as fp:
                fp.write(content)

    def generate_data(self, file, data):
        """
        对指定文件替换数据，生成最终测试数据
        :param file: 指定测试文件路径
        :param data: 需要替换的数据，传入字典类型，key为文件中被替换的内容，value为替换的字符串
        :return: 最终测试数据
        """
        tmp_dir = self.tmp_dir
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        file = os.path.join(tmp_dir, file)
        with open(file, "r") as fp:
            content = fp.read()
        for key in data:
            content = content.replace(key, data[key])
        with open(file, "w") as fp:
            fp.write(content)
        return eval(content)

    def generate_time_params(self):
        current_time = int(time())
        return {"start_time": current_time - 1800, "end_time": current_time}

    def get_status(self, url, key, expect_value):
        """
        :param url: 获取服务或者构建详情的url
        :param key: 获取状态的key 需要是个数组，传入层级的key
        :param expect_value:最终判断状态
        :return: true or false
        """
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            response = self.send(method="GET", path=url)
            assert response.status_code == 200, "get status failed"
            code, value = self.get_value(response.json(), [key])
            assert code, value
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
            for key in name.keys():
                if name[key] == content[key]:
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
