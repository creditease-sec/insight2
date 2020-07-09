#!encoding=utf-8
import time
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from tornado import template

from logic.model import *
from logic.util import *
from logic.service import send_pack as service_async
from logic.utility import *

loader = template.Loader("template")

def check_vul():
    settings = SystemSettings.get_or_none()
    global_setting = json.loads(settings.global_setting)
    vuls = Vul.select().where(Vul.vul_status.in_([40, 50, 55]))
    for vul in vuls:
        app = App.get_or_none(App.id == vul.app_id)
        if app:
            app = model_to_dict(app)
            risk_score, repair_time = get_risk_score_and_end_date(vul.real_rank, app)

            start_date = datetime.fromtimestamp(vul.audit_time)

            remaining_time = (start_date - datetime.now()).days + repair_time + vul.delay_days
            print (vul.id, vul.vul_name, vul.audit_time, vul.notice_time, remaining_time)

            if remaining_time > 0:
                status = '未逾期, 剩余处理时间 <p style="font-size:20px;color:green;display:inline-block;">{}</p> 天'.format(remaining_time)
            else:
                status = '已逾期 <p style="font-size:20px;color:green;display:inline-block;">{}</p>  天'.format(abs(remaining_time))

            data = {"vul_name": vul.vul_name, \
                    "url": "{}/#/n_viewvulndetail?id={}".format(global_setting.get("domian") or "", vul._id),
                    "username": "", "email": "", "status": status}

            to = []
            relate_users = get_vul_relate_users(vul._id)
            to.append(relate_users.get("user", {}).get("email"))
            to.append(relate_users.get("groupowner", {}).get("email"))
            for guser in relate_users.get("groupusers", []):
                to.append(guser.get("email"))
            to.append(relate_users.get("sec_owner", {}).get("email"))
            to = [item for item in to if item]

            sec_owner = relate_users.get("sec_owner", {})
            if sec_owner:
                data["username"] = sec_owner.get("nickname") or sec_owner.get("username")
                data["email"] = sec_owner.get("email")

            if not to:
                continue

            to = list(set(to))
            text = loader.load("alert.html").generate(data = data)
            if not isinstance(text, str): text = text.decode()

            time.sleep(6)
            service_async("service_email", {"title": "漏洞提醒", "msg": text, "to": to})

            ExtensionLog(name = "漏洞逾期检查", title = "漏洞逾期检查", content = "{} {} 发送到{}".format(vul.vul_name, status, ",".join(to)), is_auto=2).save()


