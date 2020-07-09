#!coding=utf-8
import json
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.define import *
from logic.utility import LoginedRequestHandler

from logic.service import service_email

@url(r"/static/config", needcheck = False, category = "系统")
class StaticConfig(BaseHandler):
    """
        静态配置

        type: [ALL, VUL_TYPE, VUL_LEVEL, VUL_STATUS, VUL_SOURCE, ASSET_LEVEL, AUTH_MODE]
    """
    def get(self):
        _type = self.get_argument("type", "ALL")

        from logic import define
        keys = dir(define)
        ALL = {}
        for key in keys:
            if not key.startswith("__"):
                ALL[key] = getattr(define, key)

        ret = {}
        if _type == "ALL":
            ret = ALL
        else:
            _type = _type.split(",")
            for k, v in ALL.items():
                if k in _type:
                    ret[k] = v

        ret.pop('OrderedDict', None)
        ret['VUL_ACTION'] = ret['VUL_ACTION']
        self.write(ret)


@url(r"/system/config/get", category = "系统")
class SystemConfigGet(LoginedRequestHandler):
    """
    系统配置获取 配置
    """
    def get(self):
        settings = SystemSettings().get_or_none()
        if settings:
            settings = model_to_dict(settings)
            settings['smtp_pass'] = '88888888'

            if settings.get('global_setting'):
                settings['global_setting'] = json.loads(settings['global_setting'])
            if settings.get('point_setting'):
                settings['point_setting'] = json.loads(settings['point_setting'])
            if settings.get('admin_op'):
                settings['admin_op'] = json.loads(settings['admin_op'])
            if settings.get('vul_setting'):
                settings['vul_setting'] = settings['vul_setting'].split(",")

            settings['email_setting'] = dict(
                    smtp_host = settings.pop('smtp_host'),
                    smtp_port = settings.pop('smtp_port'),
                    smtp_user = settings.pop('smtp_user'),
                    smtp_pass = settings.pop('smtp_pass'),
                    smtp_head = settings.pop('smtp_head'),
                    smtp_sign = settings.pop('smtp_sign'),
                    smtp_auth_type = settings.pop('smtp_auth_type'),
                    mail_list = settings.pop('mail_list')
            )

        else:
            settings = {}

        self.write(dict(status = True, result = settings))

@url(r"/system/config", category = "系统")
class SystemConfig(LoginedRequestHandler):
    """
    配置

    type: 类型(全局配置，积分配置...)
    """

    def post(self):
        kwargs = dict((k, v[-1].decode()) for k, v in self.request.arguments.items())

        _type = kwargs.pop("type")
        doc = {_type: json.dumps(kwargs)}

        SystemSettings.update(**doc).execute()

        self.write(dict(status = True, msg = "设置成功"))



@url(r"/system/mailconfig", category = "系统")
class SystemMailConfig(LoginedRequestHandler):
    """
    邮件配置

    smtp_host: 邮箱HOST
    smtp_port: 端口
    smtp_user: 用户
    smtp_pass: 密码
    smtp_head: 邮箱头
    smtp_sign: 邮箱签名
    smtp_auth_type: pure, tls, ttl
    """

    def post(self):
        kwargs = dict((k, v[-1]) for k, v in self.request.arguments.items())
        smtp_pass = kwargs.pop('smtp_pass', '88888888').decode()

        if smtp_pass != '88888888':
            kwargs['smtp_pass'] = smtp_pass

        settings = SystemSettings.get_or_none()
        if not settings:
            SystemSettings(**kwargs).save()
        else:
            SystemSettings.update(**kwargs).execute()

        self.write(dict(status = True))

@url(r"/system/mailtest", needcheck = False, category = "系统")
class SystemTestConfig(LoginedRequestHandler):
    """
    邮件测试
    """

    def post(self):
        status, msg = service_email({"msg": "test"})
        self.write(dict(status = status, msg = msg))

@url(r"/system/vulconfig", category = "系统")
class SystemVulConfig(LoginedRequestHandler):
    """
    漏洞流程配置

    """
    def post(self):
        _id = self.get_arguments("id")
        _id = sorted(_id)
        _id = ",".join(_id)

        settings = SystemSettings.get_or_none()
        if not settings:
            SystemSettings(vul_setting = _id).save()
        else:
            SystemSettings.update(vul_setting = _id).execute()

        self.write(dict(status = True, msg = "设置成功"))


