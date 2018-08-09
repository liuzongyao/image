import os
import json
from common.loadfile import FileUtils


def add_file(content):
    file_path = [os.path.join(os.getcwd(), 'temp_data'), os.path.join(os.path.dirname(os.getcwd()), 'temp_data')]
    for path in file_path:
        if os.path.exists(path):
            file = os.path.join(path, 'temporary.py')
            with open(file, 'a+') as f:
                f.writelines(content)


def data_value():
    file_path = [os.path.join(os.getcwd(), 'temp_data'), os.path.join(os.path.dirname(os.getcwd()), 'temp_data')]
    for path in file_path:
        if os.path.exists(path):
            file = os.path.join(path, 'temporary.py')
            data_dict = {}
            with open(file, 'r') as f:
                for line in f:
                    if '=' in line and 'SMTP' not in line:
                        data = line.split('=')
                        data_dict[data[0].strip()] = eval(data[1].strip())
            return data_dict


class ParserCase(object):
    def __init__(self, file, dir_name=None, variables={}):
        self.file = file
        self.content = {}
        self.dir_name = dir_name
        self.variables = variables
        self.data = data_value()

    def parameterize(self, file, dir_name=None):
        contents = FileUtils.load_file(file, dir_name=dir_name)
        return contents

    def generate_case(self, file, dir_name=None):
        content = self.parameterize(file, dir_name=dir_name)

        if self.variables:
            self.data.update(self.variables)

        return self.replace_varible(self.data, json.dumps(content))

    def replace_varible(self, sources, content):
        for key, value in sources.items():
            new_key = '{}{}'.format('$', key)
            if new_key in content:
                content = content.replace(new_key, value)
        self.content['data'] = content
        return self.content

    def parser_case(self):
        return self.generate_case(self.file, dir_name=self.dir_name)
