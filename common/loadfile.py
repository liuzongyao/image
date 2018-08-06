import json
import yaml
import io
import os
from common.exceptions import FileNotExist


def get_file_path():
    """
    get the path of file's
    """
    path_list = [os.path.join(os.path.dirname(os.getcwd()), "test_data"), os.path.join(os.getcwd(), "test_data")]

    for path in path_list:
        if os.path.exists(path):
            return path


file_path = get_file_path()


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
    def search_file(file, dir_name=None):
        for dirpath, dirname, filenames in os.walk(file_path):
            if dir_name:
                dist = dirpath.split('/')[-1]
                if dir_name == dist and file in filenames:
                    return '{}/{}'.format(dirpath, file)
            elif file in filenames:
                return '{}/{}'.format(dirpath, file)
        return False

    @staticmethod
    def load_file(file, dir_name=None):
        file_name = FileUtils().search_file(file, dir_name=dir_name)
        if file_name:
            file_suffix = os.path.splitext(file_name)[1]
            if file_suffix == '.yaml' or file_suffix == '.yml':
                return FileUtils._load_yaml_file(file_name)
            if file_suffix == '.json':
                return FileUtils._load_json_file(file_name)
        else:
            raise FileNotExist("{} not exist".format(file))
