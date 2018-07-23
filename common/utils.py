from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from common.settings import SMTP
import smtplib


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
                except Exception as ex:
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
        print("发送邮件成功")
    except Exception as e:
        # don't fatal if email was not send
        print("发送邮件失败，错误原因：{}".format(e))
    finally:
        if server:
            server.quit()
