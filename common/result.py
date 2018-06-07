#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from common import common


class Results:

    def __init__(self):
        self.sender = common.env['smtp']['sender']
        self.host = common.env['smtp']['host']
        self.port = common.env['smtp']['port']
        self.debug_level = common.env['smtp']['debug_level']
        self.username = common.env['smtp']['username']
        self.password = common.env['smtp']['password']
        self.receiver = common.env['smtp']['receiver']
        self.results = []

    def is_pass(self, condition):
        return True if condition else False

    def update_check_point(self, case_name, is_pass, message):
        results = {'case_name': case_name, 'is_pass': is_pass, 'message': message}
        if len(self.results) == 0:
            self.results.append(results)
        elif case_name == self.results[-1]['case_name']:
            self.results[-1].update(results)
        else:
            self.results.append(results)

        assert results['message'] == message

    def update_results(self):

        total = len(self.results)
        succeed = 0
        for i in range(total):
            if self.results[i]['is_pass']:
                succeed = succeed + 1
        fail = total - succeed
        summary = "Run {} cases, Pass {} cases, Fail {} cases, ".format(total, succeed, fail)
        html = '<html>\n<body>\n<h1>\n' + summary + '</h1>\n'
        html = html + '<table border="1">\n' \
                      '<thead>\n' \
                      '<tr>\n' \
                      '<td>Case name</td>\n' \
                      '<td>Case flag</td>\n' \
                      '<td>Case details</td>' \
                      '\n</tr>\n' \
                      '</thead>\n' \
                      '<tbody>'

        for i in range(total):
            if self.results[i]['is_pass']:
                html = html + '\n<tr>\n<td>{}</td>'.format(self.results[i]['case_name']) + \
                       '\n<td style="color:green;">{}</td>'.format(self.results[i]['is_pass']) + \
                       '\n<td style="color:green;">{}</td>'.format(self.results[i]['message']) + '\n</tr>'
            else:
                html = html + '\n<tr>\n<td>{}</td>'.format(self.results[i]['case_name']) + \
                       '\n<td style="color:red;">{}</td>'.format(self.results[i]['is_pass']) + \
                       '\n<td style="color:red;">{}</td>'.format(self.results[i]['message']) + '\n</tr>'

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
# result.results = [{'case_name': 'test', 'is_passed': False, 'message': 'right'}]
# response = result.update_results()
# print response
# result.send_email("test123", response)


