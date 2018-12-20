from common.base_request import Common
from common.log import logger
import sys
import json
import time
import paramiko
import os
import yaml


class Image(Common):
    def __init__(self):
        super(Image, self).__init__()

    def get_feature_url(self, region_name):
        return "v2/regions/{}/{}/features".format(self.account, region_name)

    def create_repo_url(self, reg_project_name=None):
        if reg_project_name:
            path = "/v1/registries/{}/{}/projects/{}/repositories".format(self.account, self.registry_name,
                                                                          reg_project_name)
        else:
            path = "/v1/registries/{}/{}/repositories".format(self.account, self.registry_name)

        return path

    def common_url(self, repo_name, reg_project_name=None):
        if reg_project_name:
            path = "/v1/registries/{}/{}/projects/{}/repositories/{}".format(self.account, self.registry_name,
                                                                             reg_project_name, repo_name)
        else:
            path = "/v1/registries/{}/{}/repositories/{}".format(self.account, self.registry_name, repo_name)
        return path

    def create_reg_project_url(self):
        return "/v1/registries/{}/{}/projects".format(self.account, self.registry_name)

    def delete_reg_project_url(self, reg_project_name):
        return "/v1/registries/{}/{}/projects/{}".format(self.account, self.registry_name, reg_project_name)

    def get_repo_tag_url(self, repo_name, reg_project_name=None):
        if reg_project_name:
            path = "/v1/registries/{}/{}/projects/{}/repositories/{}/tags".format(self.account, self.registry_name,
                                                                                  reg_project_name, repo_name)
        else:
            path = "/v1/registries/{}/{}/repositories/{}/tags?view_type=detail&page_size=20".format(
                self.account, self.registry_name, repo_name)
        return path

    def get_delete_repo_tag_url(self, repo_name, tag_name, reg_project_name=None):
        if reg_project_name:
            path = "/v1/registries/{}/{}/projects/{}/repositories/{}/tags/{}"\
                .format(self.account, self.registry_name, reg_project_name, repo_name, tag_name)
        else:
            path = "/v1/registries/{}/{}/repositories/{}/tags/{}"\
                .format(self.account, self.registry_name, repo_name, tag_name)
        return path

    def get_reg_project_list_url(self):
        return "/v1/registries/{}/{}/projects".format(self.account, self.registry_name)

    def get_repo_list_url(self, reg_project_name=None):
        if reg_project_name:
            path = "/v1/registries/{}/{}/projects/{}/repositories?page=1&page_size=20&".format(self.account,
                                                                                               self.registry_name,
                                                                                               reg_project_name)
        else:
            path = "/v1/registries/{}/{}/repositories?page=1&page_size=20&".format(self.account, self.registry_name)
        return path

    def get_image_url(self, repo_name, repo_tag, reg_project=None):
        if reg_project:
            path = "/v1/registries/{}/{}/projects/{}/repositories/{}/tags/{}" \
                .format(self.account, self.registry_name, reg_project, repo_name, repo_tag)
        else:
            path = "/v1/registries/{}/{}/repositories/{}/tags/{}" \
                .format(self.account, self.registry_name, repo_name, repo_tag)

        return path

    def create_reg_project(self, file, data):
        logger.info("************************** create registry project ********************************")
        path = self.create_reg_project_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data, params={})

    def delete_reg_project(self, reg_project_name):
        logger.info("************************** delete registry project ********************************")
        path = self.delete_reg_project_url(reg_project_name)
        return self.send(method='delete', path=path, params={})

    def create_repo(self, file, data, reg_project_name=None):
        logger.info("************************** create repository ********************************")
        path = self.create_repo_url(reg_project_name=reg_project_name)
        data = self.generate_data(file, data)
        return self.send(method='post', path=path, data=data, params={})

    def update_repo(self, repo_name, file, data, reg_project_name=None):
        logger.info("************************** update repository ********************************")
        path = self.common_url(repo_name, reg_project_name=reg_project_name)
        data = self.generate_data(file, data)
        return self.send(method='put', path=path, data=data, params={})

    def delete_repo(self, repo_name, reg_project_name=None):
        logger.info("************************** delete repository ********************************")
        path = self.common_url(repo_name, reg_project_name=reg_project_name)
        return self.send(method='delete', path=path, params={})

    def get_repo_detail(self, repo_name, reg_project_name=None):
        path = self.common_url(repo_name, reg_project_name=reg_project_name)
        return self.send(method='get', path=path, params={})

    def get_repo_tag(self, repo_name, reg_project_name=None):
        path = self.get_repo_tag_url(repo_name, reg_project_name=reg_project_name)
        return self.send(method='get', path=path, params={})

    def delete_repo_tag(self, repo_name, tag_name, reg_project_name=None):
        path = self.get_delete_repo_tag_url(repo_name, tag_name, reg_project_name=reg_project_name)
        return self.send(method='delete', path=path, params={})

    def get_repo_list(self, reg_project_name=None):
        path = self.get_repo_list_url(reg_project_name=reg_project_name)
        return self.send(method='get', path=path, params={})

    def get_reg_project(self, reg_project_name):
        path = self.get_reg_project_list_url()
        response = self.send(method='get', path=path, params={})
        if response.status_code == 200:
            contents = response.json()
            for content in contents:
                if content['project_name'] == reg_project_name:
                    return True

            logger.error("Registry project: {} not in registry project list: {}".format(reg_project_name, contents))
            return False
        else:
            logger.error("Get registry project list failed, Error code: {}, Response: {}".format(response.status_code,
                                                                                                 response.text))
            return False

    def get_image_detail(self, repo_name, repo_tag, reg_project=None):
        path = self.get_image_url(repo_name, repo_tag, reg_project=reg_project)
        return self.send(method='get', path=path, params={})

    def get_feature_template(self, region_name, type):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_feature_url(region_name)
        response = self.send(method="get", path=url, params={})
        if response.status_code != 200:
            return {}
        templates = self.get_value(response.json(), "{}.template.versions".format(type))
        for template in templates:
            if template["is_active"]:
                content = template["values_yaml_content"]
                return {
                    "$values_yaml_content": yaml.load(content)
                }
        return {}

    def install_registry(self, region_name, registry_name, file):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        data = self.get_feature_template(region_name, "registry")
        data['$values_yaml_content']['environment']['name'] = registry_name
        data.update({"$values_yaml_content": yaml.dump(data["$values_yaml_content"])})
        url = "v2/regions/{}/{}/features/registry".format(self.account, region_name)
        data = self.generate_data(file, data).replace("\n", "\\n")
        return self.send(method="post", path=url, data=data, params={})

    def uninstall_registry(self, region_name):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = "v2/regions/{}/{}/features/registry".format(self.account, region_name)
        return self.send(method="delete", path=url, params={})

    def get_registry_running(self):
        path = self.get_feature_url(self.region_name)
        for i in range(1, 7):
            result = self.send(method="get", path=path, params={})
            status = result.json()['registry']['application_info']['status']
            if status == 'Running':
                break
            else:
                time.sleep(10)

    def get_regin_id(self):
        url = "v2/regions/{}/{}".format(self.account, self.region_name)
        result = self.send(method="get", path=url, params={})
        assert result.status_code == 200
        return result.json()['id']

    def get_registry_endpoint(self):
        path = "v1/registries/{}".format(self.account)
        result = self.send(method="get", path=path, params={})
        assert result.status_code == 200
        for i in range(len(result.json())):
            if result.json()[i]['region_id'] == self.get_regin_id():
                endpoint = result.json()[i]['endpoint']
                return endpoint

    def remote_exec_command(self, command, **kwargs):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**kwargs)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        ssh.close()
        return result

    def copy_from_local_to_jumper(self, file_name, host, port, username, path, password=None, key_filename=None):
        if key_filename:
            if port:
                cmd = 'scp -i ' + key_filename + ' -P ' + str(
                    port) + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                os.system(cmd)
            else:
                cmd = 'scp -i ' + key_filename + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                os.system(cmd)
        else:
            pass

    def copy_from_jumper_to_local(self, file_name, host, port, username, path,  password=None, key_filename=None):
        if key_filename:
            if port:
                cmd = 'scp -i ' + key_filename + ' -P ' + str(
                    port) + ' ' + username + '@' + host + ':' + file_name + ' ' + path
                logger.info(cmd)
                os.system(cmd)
            else:
                cmd = 'scp -i ' + key_filename + ' ' + username + '@' + host + ':' + file_name + ' ' + path
                logger.info(cmd)
                os.system(cmd)
        else:
            pass

    def copy_from_jumper_to_node(self, file_name, host, username, path, port=None, password=None, key_filename=None):
        if key_filename:
            if port:
                cmd = 'scp -i ' + key_filename + ' -P ' + str(
                    port) + ' ' + username + '@' + host + ':' + file_name + ' ' + path
                logger.info(cmd)
                return cmd
            else:
                cmd = 'scp -i ' + key_filename + ' ' + username + '@' + host + ':' + file_name + ' ' + path
                logger.info(cmd)
                return cmd
        elif password:
            if port:
                cmd = 'sshpass -p ' + password + 'scp -P ' + str(port) + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
            else:
                cmd = 'sshpass -p ' + password + 'scp ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
        else:
            if port:
                cmd = 'scp -P ' + str(port) + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
            else:
                cmd = 'scp ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd

    def copy_from_node_to_jumper(self, file_name, host, username, path, port=None, password=None, key_filename=None):
        if key_filename:
            if port:
                cmd = 'scp -i ' + key_filename + ' -P ' + str(
                    port) + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
            else:
                cmd = 'scp -i ' + key_filename + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
        elif password:
            if port:
                cmd = 'sshpass -p ' + password + 'scp -P ' + str(
                    port) + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
            else:
                cmd = 'sshpass -p ' + password + 'scp ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
        else:
            if port:
                cmd = 'scp -P ' + str(port) + ' ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd
            else:
                cmd = 'scp ' + file_name + ' ' + username + '@' + host + ':' + path
                logger.info(cmd)
                return cmd

    def change_secrets(self, secret_name):
        f = open('test_case/image/sa.json', encoding='utf-8')
        res = json.load(f)
        secrets = res['imagePullSecrets']
        new_secret = {'name': secret_name}
        secrets.append(new_secret)
        f.close()
        f1 = open('test_case/image/sa.json', mode='w', encoding='utf-8')
        json.dump(res, f1)
        f1.close()
