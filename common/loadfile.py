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
    def load_file(file_name):
        if file_name:
            file_suffix = os.path.splitext(file_name)[1]
            if file_suffix == '.yaml' or file_suffix == '.yml':
                return FileUtils._load_yaml_file(file_name)
            if file_suffix == '.json':
                return FileUtils._load_json_file(file_name)
        else:
            raise FileNotExist("{} not exist".format(file_name))
