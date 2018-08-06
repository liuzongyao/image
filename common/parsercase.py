import re
from common.loadfile import FileUtils
from common.import_variable import search_conf_item

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


class ParserCase(object):
    def __init__(self, file, dir_name=None, variables={}):
        self.file = file
        self.dir_name = dir_name
        self.variables = variables

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

    def parser_variable(self, content):
        """
        get all the variables in the case and parser variable
        :param content: dict
        :return:
        e.g.
            {
                "url": "$API_URL/v1/regions/$NAMESPACE/" ,
                "method": "get" ,
                "headers":  {
                    "content-type": "application/json" ,
                    "Authorization": "Token ${token()}"
                }
                "kubernetes": [
                    {
                         "name": "$NAMESPACE"
                    }
                ]
            }

            => {
                    "API_URL": "http://23.100.93.31:20081",
                    "NAMESPACE": "alauda"
                }
        """
        variables = {}
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    variable_list = extract_variables(value)
                    if variable_list:
                        for variable in variable_list:
                            variable_value = search_conf_item('variable', variable)
                            variables[variable] = variable_value
                if isinstance(value, dict):
                    ret = self.parser_variable(value)
                    variables.update(ret)
                if isinstance(value, (list, dict)):
                    for index, v in enumerate(value):
                        if isinstance(v, dict):
                            ret = self.parser_variable(v)
                            variables.update(ret)
        return variables

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

        module_variable = self.parser_variable(content)
        self.replace_varible(module_variable, content)
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
