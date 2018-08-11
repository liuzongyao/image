# coding=utf-8
import json
import yaml
import io
import os
from common.exceptions import FileNotExist


class FileUtils(object):
    @staticmethod
    def _load_yaml_file(file):
        with io.open(file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.load(f)
            return yaml_content

    @staticmethod
    def _load_json_file(file):
        with io.open(file, 'r', encoding='utf-8') as f:
            json_content = json.load(f)
            return json_content

    @staticmethod
    def load_file(file_path):
        """
        用来获取文件中的数据，支持yaml/yaml(yaml格式)和json(json格式)结尾的文件
        :param file_path: 文件路径
        :return:返回字典类型数据
        """
        if file_path:
            file_suffix = os.path.splitext(file_path)[1]
            if file_suffix == '.yaml' or file_suffix == '.yml':
                return FileUtils._load_yaml_file(file_path)
            if file_suffix == '.json':
                return FileUtils._load_json_file(file_path)
        else:
            raise FileNotExist("{} not exist".format(file_path))
