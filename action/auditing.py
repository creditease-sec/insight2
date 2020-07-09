#!coding=utf-8
import json
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornado import template
loader = template.Loader("template")

from tornadoweb import *
from logic.model import *
from logic.utility import *
from logic.groupuser import group_user

from logic.service import send_pack as service_async

def email_notify_to(vul_id, title = "", content = "", uid = ""):
    settings = SystemSettings.get_or_none()
    global_setting = json.loads(settings.global_setting)
    isSendEmail = global_setting.get("isSendEmail")

    if isSendEmail != "1":
        return

    vul = Vul.get_or_none(Vul._id == vul_id)

    to = []
    relate_users = get_vul_relate_users(vul_id)
    to.append(relate_users.get("user", {}).get("email"))
    to.append(relate_users.get("groupowner", {}).get("email"))
    for guser in relate_users.get("groupusers", []):
        to.append(guser.get("email"))
    to.append(relate_users.get("sec_owner", {}).get("email"))
    to = [item for item in to if item]

    if to:
        data = {"vul_name": vul.vul_name, \
                "url": "{}/#/n_viewvulndetail?id={}".format(global_setting.get("domian"), vul._id), \
                "title": title, \
                "status": title, \
                "content": content}

        text = loader.load("alert.html").generate(data = data)
        service_async("service_email", {"msg": text, "to": to, "title": title})
        ExtensionLog(op_user_id = uid, name = title, title = "邮件发送", content = "{} 发送到{}".format(title, ",".join(to)), is_auto=2).save()

def notify_message(vul_id, title = "", content = "", uid = ""):
    vul = Vul.get_or_none(Vul._id == vul_id)
    vul_name = vul.vul_name
    #title = "{} {}".format(vul_name, title)

    relate_users = get_vul_relate_users2(vul._id)
    user_ids = list(set([user.get("id") for user in relate_users]))
    for user_id in user_ids:
        Message(title = title, content = content, to = user_id, message_type = "auditing").save()


@url(r"/auditing/ignore", category = "审核")
class AuditingIgnore(LoginedRequestHandler):
    """
        漏洞忽略

        id: 漏洞id
        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        Vul.update(vul_status = 20, fix_time = time.time()).where(Vul._id == _id).execute()

        email_notify_to(_id, title = "漏洞已忽略", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞已忽略", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))

@url(r"/auditing/reject", category = "审核")
class AuditingReject(LoginedRequestHandler):
    """
        漏洞驳回

        id: 漏洞id
        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        Vul.update(vul_status = 30, fix_time = time.time()).where(Vul._id == _id).execute()

        email_notify_to(_id, title = "漏洞已驳回", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞已驳回", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))

@url(r"/auditing/undo", category = "审核")
class AuditingUndo(LoginedRequestHandler):
    """
        漏洞暂不处理

        id: 漏洞id
        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        Vul.update(vul_status = 35, fix_time = time.time()).where(Vul._id == _id).execute()

        email_notify_to(_id, title = "漏洞暂不处理", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞暂不处理", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))


@url(r"/auditing/confirm", category = "审核")
class AuditingConfirm(LoginedRequestHandler):
    """
        漏洞确认

        id: 漏洞id
        app_id: 应用id
        real_rank: 真实rank
        stats: 40/60

        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        app_id = self.get_argument('app_id', 0)
        real_rank = int(self.get_argument('real_rank', 0))
        status = int(self.get_argument('status', 40))
        doc = dict(vul_status = status, audit_time = time.time())
        vul = Vul.get_or_none(Vul._id == _id)

        settings = SystemSettings.get_or_none()
        point_setting = {}
        if settings and settings.point_setting:
            point_setting = json.loads(settings.point_setting)

        ti_level_point = int(point_setting.get("ti_level_point") or 1)
        times_level_point = int(point_setting.get("times_level_point") or 1)

        app = App.get_or_none(App._id == app_id)
        if app:
            doc['app_id'] = app.id

        if real_rank:
            doc['real_rank'] = real_rank
            level_point = 1
            if app:
                sec_level = app.sec_level
                if sec_level == 10:
                    level_point = int(point_setting.get("one_level_point") or 1)
                elif sec_level == 20:
                    level_point = int(point_setting.get("two_level_point") or 1)
                elif sec_level == 30:
                    level_point = int(point_setting.get("three_level_point") or 1)
                elif sec_level == 40:
                    level_point = int(point_setting.get("other_level_point") or 1)

            #reward_points = "rank * 分级对应系数 * 倍数"
            if vul.vul_type == 70:
                reward_points = real_rank * level_point * ti_level_point * times_level_point
            else:
                reward_points = real_rank * level_point * times_level_point

            User.update(total_points = User.total_points + reward_points, available_points = User.available_points + reward_points).where(User.id == vul.user_id).execute()

        Vul.update(**doc).where(Vul._id == _id).execute()

        # TODO app -> group -> owner
        email_notify_to(_id, title = "漏洞已确认", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞已确认", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))

@url(r"/auditing/fixing", needcheck=False, category = "审核")
class AuditingFixing(LoginedRequestHandler):
    """
        漏洞已知悉(开始修复)

        id: 漏洞id
        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        Vul.update(vul_status = 50, notice_time = time.time()).where(Vul._id == _id).execute()

        email_notify_to(_id, title = "漏洞已知悉", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞已知悉", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))

@url(r"/auditing/retest", needcheck=False, category = "审核")
class AuditingRetest(LoginedRequestHandler):
    """
        漏洞申请复测

        id: 漏洞id
        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        Vul.update(vul_status = 55).where(Vul._id == _id).execute()

        email_notify_to(_id, title = "漏洞申请复测", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞申请复测", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))


@url(r"/auditing/fixed", category = "审核")
class AuditingFixed(LoginedRequestHandler):
    """
        漏洞完成

        id: 漏洞id
        status: 修复结果状态40/60
        response: {"status": True, "msg": ""}
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        msg = self.get_argument('msg', '')
        status = int(self.get_argument('status', 60))
        Vul.update(vul_status = status, fix_time = time.time()).where(Vul._id == _id).execute()

        email_notify_to(_id, title = "漏洞已修复", content = content, uid = self.uid)
        notify_message(_id, title = "漏洞已修复", content = content, uid = self.uid)

        self.write(dict(status = True, msg = "设置成功"))

