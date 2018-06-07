#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
This runs a command on a remote host using SSH. At the prompts enter hostname,
user, password and the command.
"""
import pexpect
import re
from common import common


class Exec_helper:

    def __init__(self):
        self._username = common.env['username']
        self._password = common.env['password']
        self._region = common.env['region_name']
        self._namespace = common.env['namespace']
        self._prompt = '#'

    def _connect_container(self, resource_id, index, version='v1'):
        if version == 'v1':
            cmd = 'ssh -p 4022 -t ' + self._namespace + '/' + self._username + '@' + common.master + ' ' + self._namespace + '/' + resource_id + '.' + str(index) + ' ' + '/bin/sh'
            print cmd
            child = pexpect.spawn(cmd)
            i = child.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'password:'])
            # 如果登录超时，打印出错信息，并退出.
            if i == 0:  # Timeout
                print 'ERROR!'
                print 'SSH could not login. Here is what SSH said:'
                print child.before, child.after
                return None
            elif i == 1:
                pass  # 其中 EOF 通常代表子程序的退出
            elif i == 2:
                child.sendline('yes')
                i = child.expect([pexpect.TIMEOUT, pexpect.EOF, 'password:'])
                if i == 0:  # Timeout
                    print 'ERROR!'
                    print 'SSH could not login. Here is what SSH said:'
                    return None
                elif i == 1:
                    pass  # 其中 EOF 通常代表子程序的退出
                else:
                    child.sendline(self._password)
                    i = child.expect([pexpect.TIMEOUT, pexpect.EOF, self._prompt])
                    if i == 0:  # Timeout
                        print 'ERROR! timeout'
                        print 'SSH could not login. Here is what SSH said:'
                        return None
                    elif i == 1:
                        print "ERROR! EOF"
                        print child.before
                        return None
                    else:
                        return child
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
            child.expect('\$')
            if username == 'root':
                pass
            else:
                child.sendline('sudo su')
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
        common.start_time = common.get_start_time()
        try:
            child = self._connect_container(resource_id, index, version)
            child.sendline(cmd)
            child.expect(self._prompt)
            if expect in child.before:
                return "测试通过",True
            else:
                return child.before, False
        finally:
            common.end_time = common.get_end_time()

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
            return "测试通过", True
        elif i == 3:
            return '不存在这个目录{}'.format(dir_name),False
        else:
            return "Error", False

    def exist_file(self, resource_id, file_name, index=0):
        child = self._connect_container(resource_id, index)
        child.sendline('cat ' + file_name)
        i = child.expect([pexpect.TIMEOUT, pexpect.EOF, self._prompt, "No such file or directory"])
        print i
        if i == 2:
            return "测试通过", True
        elif i == 3:
            return '不存在这个文件{}'.format(file_name),False
        else:
            return "Error", False


exec_helper = Exec_helper()
