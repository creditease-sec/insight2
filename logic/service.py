#!encoding=utf-8
import pymysql
from redis import Redis
from json import dumps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from logic.util import conv_object

mq = Redis(host = __conf__.REDIS_HOST, port = __conf__.REDIS_PORT, \
            password = __conf__.REDIS_PASS, db = __conf__.REDIS_DB)

def send_pack(cmd, data):
    data = conv_object(data)
    pack = dumps(dict(cmd = cmd, data = data))
    mq.rpush(__conf__.REDIS_CHANNEL, pack)

def service_email(data):
    """
        data:{
            msg:
        }
    """
    try:
        db = pymysql.connect(host = __conf__.DB_HOST, port = __conf__.DB_PORT,
                user = __conf__.DB_USER, password = __conf__.DB_PASS,
                database = __conf__.DB_NAME)
        cursor = db.cursor()
        cursor.execute("select smtp_host, smtp_port, smtp_user, smtp_pass, smtp_head, smtp_sign, smtp_auth_type, mail_list from systemsettings")
        system_setting = cursor.fetchall()
        cursor.close()
        db.close()

        if not system_setting:
            #send_pack("service_email", data)
            return False, "未配置"

        smtp_host, smtp_port, smtp_user, smtp_pass, smtp_head, smtp_sign, smtp_auth_type, mail_list = system_setting[0]
        smtp_port = int(smtp_port or 25)
        title = data.get('title')

        if title:
            smtp_head = title

        if mail_list:
            mail_list = mail_list.split(",")
        else:
            mail_list = []

        if data.get('to'):
            to = list(set(data.get('to')))
            mail_list.extend(to)

        mail_list = ",".join(mail_list)

        if not mail_list: return False, "无收件人"

        main_msg = MIMEMultipart()
        main_msg['From'] = smtp_user
        main_msg['To'] = mail_list
        main_msg['Subject'] = Header(smtp_head, 'utf-8').encode()

        msg = MIMEText(data.get("msg"), 'html', 'utf-8')
        main_msg.attach(msg)

        #html_msg = MIMEText(smtp_sign, _subtype='html', _charset='utf-8')
        #main_msg.attach(html_msg)


        if smtp_auth_type == 'ssl':
            email_sender = smtplib.SMTP_SSL(smtp_host, smtp_port)
        elif smtp_auth_type == 'tls':
            email_sender = smtplib.SMTP(smtp_host, smtp_port)
            email_sender.starttls()
        else:
            email_sender = smtplib.SMTP(smtp_host, smtp_port)

        email_sender.login(smtp_user, smtp_pass)
        email_sender.sendmail(smtp_user,mail_list.split(','), main_msg.as_string())
        email_sender.close()
        return True, ""
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)

if __name__ == "__main__":
    service_email({"msg": "xx"})

