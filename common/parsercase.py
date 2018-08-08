import os
import re
from common.loadfile import FileUtils


variable_regexp = r"\$([\w_]+)"


def extract_variables(content):
    """ extract all variable names from content, which is in format $variable
    @param (str) content
    @return (list) variable name list
    e.g. $variable => ["variable"]
         /blog/$postid => ["postid"]
         /$var1/$var2 => ["var1", "var2"]
         abc => []
    """
    try:
        return re.findall(variable_regexp, content)
    except TypeError:
        return []


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
        self.dir_name = dir_name
        self.variables = variables
        self.data = data_value()
        print(self.data)

    def parameterize(self, file, dir_name=None):
        contents = FileUtils.load_file(file, dir_name=dir_name)
        return contents

    def parser_file(self, content):
        if isinstance(content, dict):
            for key, value in content.items():
                content[key] = self.parser_file(value)
        if isinstance(content, str):
            if content.endswith((".yaml", ".yml", ".json")):
                content = self.parameterize(content)
        if isinstance(content, list):
            for index, con in enumerate(content):
                content[index] = self.parser_file(con)
        return content

    def generate_case(self, file, dir_name=None):
        content = self.parameterize(file, dir_name=dir_name)
        content = self.parser_file(content)

        variables = {}

        if 'variables' in content:
            variables = content.pop('variables')

        if self.variables:
            variables.update(self.variables)

        if variables:
            self.replace_varible(variables, content)

        self.replace_varible(self.data, content)
        return content

    def replace_varible(self, sources, content):
        """
        replace variable
        :param sources: dict
        :param content: dict
        :return:
        """
        if isinstance(content, dict):
            for key, value in content.items():
                content[key] = self.replace_varible(sources, value)
        if isinstance(content, str):
            variable_list = extract_variables(content)
            for index, variable in enumerate(variable_list):
                if variable in sources:
                    variable_new = '$' + variable
                    content = content.replace(variable_new, sources[variable])
        if isinstance(content, list):
            for index, cont in enumerate(content):
                content[index] = self.replace_varible(sources, cont)
        return content

    def parser_case(self):
        return self.generate_case(self.file, dir_name=self.dir_name)
