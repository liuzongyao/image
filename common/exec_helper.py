#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
This runs a command on a remote host using SSH. At the prompts enter hostname,
user, password and the command.
"""
import pexpect
import yaml
import os
import re
from common import Common


class Exec_helper:

    def __init__(self, env_file):
        self.env_file = env_file
        f = open(self.env_file)
        env = yaml.load(f)
        self._username = env['username']
        self._password = env['password']
        self._master = env['master']
        self._namespace = env['namespace']
        self._prompt = '#'


    def _connect_container(self, resource_id, index, version='v1'):
        Common.start_time = Common.get_start_time()

        if version == 'v1':
            cmd = 'ssh -p 4022 -t ' + self._namespace + '/' + self._username + '@' + self._master + ' ' + self._namespace + '/' + resource_id + '.' + str(index) + ' ' + '/bin/sh'
            print cmd
            child = pexpect.spawn(cmd)
            i = child.expect([pexpect.TIMEOUT, pexpect.EOF, 'password:'])
            # 如果登录超时，打印出错信息，并退出.
            if i == 0:  # Timeout
                print 'ERROR!'
                print 'SSH could not login. Here is what SSH said:'
                print child.before, child.after
                return None
            elif i == 1:
                pass  # 其中 EOF 通常代表子程序的退出
            # 输入密码.
            else:
                child.sendline(self._password)
            i = child.expect([pexpect.TIMEOUT, pexpect.EOF, self._prompt])
            if i == 0:  # Timeout
                print 'ERROR! timeout'
                print 'SSH could not login. Here is what SSH said:'
                print child.before
                return None
            elif i == 1:
                print "ERROR! EOF"
                print child.before
                return None
            else:
                return child
        elif version == "v2":
            pass

    def _connect_host(self, host, username, password):
        cmd = 'ssh -i alaudastaging.pem ' + username + '@' + host
        print cmd
        try:
            child = pexpect.spawn(cmd)
            res = child.expect(['Are you sure you want to continue connecting (yes/no)?', 'password:'])
            if res == 0:
                child.sendline('yes')
                child.expect('password:')
            child.sendline(password)
            # print child.before
            # print child.after
            child.expect('\$')
            if username == 'root':
                pass
            else:
                child.sendline('sudo su')
                # print child.before
                # print child.after
                child.expect(self._prompt)
        except pexpect.EOF, pexpect.TIMEOUT:
            print "timeout"
        return child

    def write_to_host(self, host, username, password, file_name, text):
        child = self._connect_host(host, username, password)
        child.sendline('touch ' + file_name)
        child.expect(self._prompt)
        child.sendline('echo ' + text + ' > ' + file_name)
        child.expect(self._prompt)

    def read_from_host(self, host, username, password, file_name):
        child = self._connect_host(host, username, password)
        child.sendline('cat ' + file_name)
        child.expect(self._prompt)
        return child.before

    def write_to_container(self, resource_id, file_name, text, index=0, version='v1'):
        child = self._connect_container(resource_id, index, version)
        child.sendline('echo ' + text + ' > ' + file_name)
        child.expect(self._prompt)

    def read_from_container(self, resource_id, file_name, index=0, version='v1'):
        child = self._connect_container(resource_id, index, version)
        child.sendline('cat ' + file_name)
        child.expect(self._prompt)
        return child.before

    def get_expect_string(self, resource_id, cmd, expect, index=0, version='v1'):
        child = self._connect_container(resource_id, index, version)
        child.sendline(cmd)
        child.expect(self._prompt)
        if expect in child.before:
            return True
        else:
            return False

    def get_content(self, resource_id, cmd, index=0, version='v1'):
        child = self._connect_container(resource_id, index, version)
        child.sendline(cmd)
        child.expect([self._prompt])
        return re.split(r'\r\n', child.before, maxsplit=1)[1]

    def exist_dir(self, resource_id, dir_name, index=0, version='v1'):
        child = self._connect_container(resource_id, index, version)
        child.sendline('cd ' + dir_name)
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, self._prompt, "cd: can't cd to"])
        if i == 2:
            return True
        elif i == 3:
            return False
        else:
            return "Error"

    def exist_file(self, resource_id, file_name, index=0):
        child = self._connect_container(resource_id, index)
        child.sendline('cat ' + file_name)
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, self._prompt, "No such file or directory"])
        print i
        if i == 2:
            return True
        elif i == 3:
            return False
        else:
            return "Error"


file_path = os.path.dirname(__file__)
env_dist = os.environ
if 'env_file' in env_dist.keys():
    env_file = os.getenv("env_key")
else:
    env_file = file_path + '/../config/env_staging.yaml'

exec_helper = Exec_helper(env_file)


if __name__ == '__main__':

    exec_helper.exist_file('4a898eb0-975b-4f89-8298-7a688ea0cd5d', '/demo')
    exec_helper.get_expect_string('5beeae6b-cd25-4260-b42a-7045df62833d', 'export', "A=1")
    exec_helper.write_to_host('23.99.107.41', 'alauda', 'v0dkIGW*7u0&U19', '/demo/123.txt', '12312345')
    content1 = exec_helper.read_from_host('23.99.107.41', 'alauda', 'v0dkIGW*7u0&U19', '/demo/123.txt')
    content2 = exec_helper.read_from_container('4a898eb0-975b-4f89-8298-7a688ea0cd5d', '/demo/123.txt')
    print content1
    print content2






    # s=pexpect.spawn("ssh -p 4022 -t testorg001/liuzongyao@23.99.114.240 testorg001/2018f7af-6aeb-4b14-ae49-cb26b22affb5.0 /bin/sh")
    # s.logfile_send = sys.stdout
    # s.expect("password:")
    # s.sendline("liuzongyao")
    # s.expect("#")
    # s.sendline("export")
    # s.expect("#")
    # print type(s.before)
    # print s.before
    # if "C='5'" in s.before:
    #     print "zhaodao"
    # else:
    #     print "no"