# coding=utf-8
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

from bs4 import BeautifulSoup

from common.match_case import casename
from common.settings import SMTP


def retry(times=3, sleep_secs=3):
    def retry_deco(func):
        def retry_deco_wrapper(*args, **kwargs):
            count = 0
            success = False
            data = None
            while not success and count < times:
                count += 1
                try:
                    data = func(*args, **kwargs)
                    success = True
                except Exception:
                    sleep(sleep_secs)
                    if count == times:
                        assert False, "get global info failed"
            return data

        return retry_deco_wrapper

    return retry_deco


def send_email(subject, body, recipients, file_path):
    """class method to send an email"""

    # if settings.EMAIL is None or settings.SMTP is None:
    #    logger.error("No email/smtp config, email not sent.")
    #    return

    if not isinstance(recipients, list):
        raise TypeError(
            "{} should be a list".format(recipients))

    # we only support one sender for now
    from_email = SMTP['sender']

    # build message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ','.join(recipients)
    msg['Subject'] = Header(subject, 'utf8')
    msg.attach(MIMEText(body, 'html', 'utf8'))
    # add report html
    att = MIMEText(open(file_path, 'rb').read(), 'base64', 'gb2312')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment; filename="report.tar"'
    msg.attach(att)

    server = None
    try:
        server = smtplib.SMTP_SSL(host=SMTP['host'], port=SMTP['port'])
        server.set_debuglevel(SMTP['debug_level'])
        server.login(SMTP['username'], SMTP['password'])
        server.sendmail(from_email, recipients, msg.as_string())
        print("send email successfully")
    except Exception as e:
        # don't fatal if email was not send
        print("send email failed，the reason is：{}".format(e))
    finally:
        if server:
            server.quit()


def read_result():
    with open("./report/pytest.html", "r") as fp:
        report = BeautifulSoup(fp, "html.parser")
        tbodys = report.select("tbody")
        html = '<table border="1">\n' \
               '<thead>\n' \
               '<tr>\n' \
               '<td>Case name</td>\n' \
               '<td>Case flag</td>\n' \
               '<td>Case details</td>' \
               '\n</tr>\n' \
               '</thead>\n' \
               '<tbody>'
        not_run_count = 0
        pass_count = 0
        failed_count = 0
        rerun_count = 0
        result_flag = 'Success'
        for tbody in tbodys:
            tds = tbody.select("td")
            case_name = casename().get(tds[1].text.split("::")[-1], tds[1].text.split("::")[-1])
            if tds[0].text == "Passed" and tds[2].text == "0.00":
                html = html + '\n<tr>\n<td>{}</td>'.format(case_name) + \
                       '\n<td style="color:orange;">{}</td>'.format("未运行") + \
                       '\n<td style="color:orange;">{}</td>'.format(tds[2].text) + '\n</tr>'
                not_run_count += 1
            elif tds[0].text == "Passed" and tds[2].text != "0.00":
                html = html + '\n<tr>\n<td>{}</td>'.format(case_name) + '\n<td style="color:green;">{}</td>'.format(
                    tds[0].text) + '\n<td style="color:green;">{}</td>'.format(tds[2].text) + '\n</tr>'
                pass_count += 1
            elif tds[0].text == "Failed":
                error_message = "{},失败请单独执行case:{}".format(tbody.select("span")[0].text, tds[1].text)
                html = html + '\n<tr>\n<td>{}</td>'.format(case_name) + '\n<td style="color:red;">{}</td>'.format(
                    tds[0].text) + '\n<td style="color:red;">{}</td>'.format(error_message) + '\n</tr>'
                failed_count += 1
                result_flag = 'Failed'
            elif tds[0].text == "Rerun":
                html = html + '\n<tr>\n<td>{}</td>'.format(case_name) + \
                       '\n<td style="color:orange;">{}</td>'.format(tds[0].text) + \
                       '\n<td style="color:orange;">{}</td>'.format(tbody.select("span")[0].text) + '\n</tr>'
                rerun_count += 1
            else:
                pass
        html_header = "{}, Pass {} cases,  {} cases not run, Fail {} cases, Rerun {} cases".format(
            report.select("p")[1].text, pass_count, not_run_count, failed_count, rerun_count)
        html = html_header + html + '\n</tbody>\n</table>'

        return result_flag, html
