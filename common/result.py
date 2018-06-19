#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from common import Common
import os
import re


class Results(Common):

    def __init__(self):
        Common.__init__(self)
        self.sender = self.env['smtp']['sender']
        self.host = self.env['smtp']['host']
        self.port = self.env['smtp']['port']
        self.debug_level = self.env['smtp']['debug_level']
        self.username = self.env['smtp']['username']
        self.password = self.env['smtp']['password']
        self.receiver = self.env['smtp']['receiver']
        self.test_flag = True
        self.results = {}

    def assert_check1_point(self, is_pass, is_block, message):
        if is_pass:
            pass
        else:
            if is_block:
                message = {message.keys()[0] + '失败': message.values()[0]}
                self.results.update(message)
                assert False, self.results
            else:
                self.test_flag = False
                message = {message.keys()[0] + '失败': message.values()[0]}
                self.results.update(message)
        assert self.test_flag, self.results

    def assert_check_point(self, is_pass, message):
        if not is_pass:
            self.test_flag = False
            message = {message.keys()[0] + '失败': message.values()[0]}
            self.results.update(message)
        assert self.test_flag, self.results

    @staticmethod
    def get_each_case_duration():
        file_path = os.path.dirname(__file__)
        pytest_report = file_path + '/../report/pytest.html'
        html = open(pytest_report).read()
        total = re.search(r'<h2>Summary</h2>\s+<p>(.*)</p>', html).group(1)
        case_name = re.findall(r'<td class="col-name">(.*)?</td>', html)
        case_flag = re.findall(r'<td class="col-result">(.*)?</td>', html)
        case_duration = re.findall(r'<td class="col-duration">(.*)?</td>', html)
        case_details = re.findall(r'<div class=".*?log">(.*)?</div>', html)
        for i in range(len(case_details)):
            print case_details[i]
            if case_details[i] == 'No log output captured.':
                pass
            else:
                error_message = re.search(r'<span class="error">(.*)?</span>', case_details[i], re.M | re.I).group(1)
                case_details[i] = error_message
        print total
        print case_name
        print case_flag
        print case_duration
        print case_details
        return total, case_name, case_flag,case_duration, case_details

    def update_results(self):
        total_time, case_name, case_flag, case_duration, case_detail = self.get_each_case_duration()
        total = len(case_name)
        succeed = 0
        fail = 0
        ignore = 0
        for i in range(total):
            if case_flag[i] == 'Passed' and case_duration[i] == "0.00":
                ignore = ignore + 1
            else:
                if case_flag[i] == 'Passed':
                    succeed = succeed + 1
                else:
                    fail = fail + 1
        summary = "Run {} cases, Pass {}, Fail {}, Ignore {}, {} ".format(total, succeed, fail, ignore, total_time)
        html = '<html>\n<body>\n<h1>\n' + summary + '</h1>\n'
        html = html + '<table border="1">\n' \
                      '<thead>\n' \
                      '<tr>\n' \
                      '<td>Case name</td>\n' \
                      '<td>Case flag</td>\n' \
                      '<td>Case detail</td>\n' \
                      '<td>Case duration</td>' \
                      '\n</tr>\n' \
                      '</thead>\n' \
                      '<tbody>'

        for i in range(total):
            if case_flag[i] == 'Passed' and case_duration[i] == "0.00":
                html = html + '\n<tr>\n<td style="color:green;">{}</td>'.format(case_name[i]) + \
                       '\n<td style="color:green;">{}</td>'.format(case_flag[i]) + \
                       '\n<td style="color:green;">{}</td>'.format('ingore') + \
                       '\n<td style="color:green;">{}</td>'.format(case_duration[i]) + '\n</tr>'
            else:
                if case_flag[i] == 'Passed':
                    html = html + '\n<tr>\n<td style="color:green;">{}</td>'.format(case_name[i]) + \
                           '\n<td style="color:green;">{}</td>'.format(case_flag[i]) + \
                           '\n<td style="color:green;">{}</td>'.format('测试通过') + \
                           '\n<td style="color:green;">{}</td>'.format(case_duration[i]) + '\n</tr>'
                else:
                    html = html + '\n<tr>\n<td style="color:red;">{}</td>'.format(case_name[i]) + \
                           '\n<td style="color:red;">{}</td>'.format(case_flag[i]) + \
                           '\n<td style="color:red;">{}</td>'.format(case_detail[i]) + \
                           '\n<td style="color:red;">{}</td>'.format(case_duration[i]) + '\n</tr>'

        html = html + '\n</tbody>\n</table>\n</body>\n</html>'
        return html

    def send_email(self, subject, body):
        msg = MIMEText(body, 'html', 'utf-8')
        msg['From'] = self.sender
        msg['To'] = ";".join(self.receiver)
        msg['Subject'] = Header(subject, 'utf8')
        try:
            s = smtplib.SMTP_SSL()
            s.connect(self.host)
            s.login(self.username, self.password)
            s.sendmail(self.sender, self.receiver, msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            print("发送邮件失败，错误原因：{}".format(e))


result = Results()
