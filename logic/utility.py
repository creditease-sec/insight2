#-*- coding:utf-8 -*-
import sys
import time
import json
import copy
import uuid
import hashlib
from datetime import datetime

import tornado.web
from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.define import *

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    def options(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')


    def get(self, *args, **kwargs):
        self.send_error(404)


    def get_sessionid(self):
        __session__ = self.get_secure_cookie("__S__")
        if not __session__:
            __session__ = hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()
            self.set_secure_cookie("__S__", __session__)
        return __session__


    def prepare(self):
        if db.is_closed():
            db.connect()

        username = getattr(self, "username") if hasattr(self, "username") else ""

        if self.request.uri.startswith("{}/auditing".format(__conf__.API_VERSION)) or \
                self.request.uri.startswith("{}/vul".format(__conf__.API_VERSION)):
            vul_id = self.get_argument("id", 0)
            if vul_id:
                msg = self.get_argument('msg', '')
                content = self.get_argument('content', '') + " " + msg
                action = ""
                if self.__doc__:
                    action = [item.strip() for item in self.__doc__.split("\n") if item.strip()][0]

                title = ""
                vul = Vul.get_or_none(Vul._id == vul_id)
                if vul:
                    title = vul.vul_name

                username = ""
                if self.uid:
                    user = User.get_or_none(User.id == int(self.uid))
                    username = user.nickname or user.username

                VulLog(vul_id = vul.id, user_id = self.uid, title = title, username = username, action = action, content = content).save()

        if True:
            __session__ = self.get_sessionid()
            print(datetime.now(), self.get_status(),
                    self.request.method,
                    round(self.request.request_time(), 4),
                    self.request.uri,
                    self.request.remote_ip,
                    username,
                    self.request.host
                )
            sys.stdout.flush()

    def on_finish(self):
        """
            REQUEST FINISH HOOK
        """

        if not db.is_closed():
            db.close()

    def send_error(self, status_code, msg = "无权限", **kwargs):
        exc_info = kwargs.get("exc_info")
        if exc_info:
            a, b, c = exc_info
            if issubclass(a, DatabaseError):
                status_code = b.args[0]
                self.write(dict(status_code = status_code, msg = b.args[1]))
                self.finish()
            elif issubclass(a, tornado.web.MissingArgumentError):
                self.write(dict(status_code = 10001, msg = str(b)))
                self.finish()
            else:
                self.write(dict(status_code = 10002, msg = str(b)))
                self.finish()
        else:
            if status_code == 403:
                self.write(dict(status_code = status_code, msg = msg))
            else:
                self.write(dict(status_code = status_code, msg = msg))
            self.finish()

class LoginedRequestHandler(BaseHandler):
    uid = property(lambda self: self.get_uid())
    username = property(lambda self: (self.get_secure_cookie("__USERNAME__") or '').decode())

    def get_uid(self):
        token = self.get_argument("token", None)
        if token:
            user = User.get_or_none(User.token == token, User.token_enable == 1)
            if user:
                return user.id

        return (self.get_secure_cookie("__UID__") or b'').decode()

    def prepare(self):
        """
            REQUEST BEFORE HOOK
        """

        if not self.uid:
            self.send_error(403)
            return

        super(LoginedRequestHandler, self).prepare()

        User.update(active_time = time.time()).where(User.id == int(self.uid)).execute()
        self.check_url()

    def check_url(self):
        user = User.get_or_none(User.id == self.uid)
        if not user:
            self.clear_cookie("__UID__")
            self.clear_cookie("__USERNAME__")
            self.send_error(403)
            return

        uri = self.request.path.replace(__conf__.API_VERSION + "/", "/")
        uris = dict((item[0], item) for item in self.__class__.__urls__)

        # uri [uri, order, needcheck, category]
        if not uris.get(uri)[2]:
            return

        accesses = user.role.accesses
        access_name = "{}.{}".format(self.__class__.__module__, self.__class__.__name__)

        if access_name not in accesses.split(","):
            self.send_error(403)

    def check_role_level(self, level):
        """
            Check Role
        """
        user = User.get_or_none(User.id == self.uid)
        if level < user.role.level:
            # no have authorized
            self.send_error(403)

    def check_role_id(self, role_id):
        """
            Check Role
        """
        current_user = User.get_or_none(User.id == self.uid)
        current_user_level = current_user.role.level

        role = Role.get_or_none(Role.id == role_id)
        role_level = role.level

        if role_level < current_user_level:
            # not have authorized
            self.send_error(403)


def access_list(accesses = None, uid = None):
    _r = copy.deepcopy(ACL)
    result = {}
    for k, v in _r.items():
        result[k] = {}
        for p, h in v.items():
            doc = h.handler.__doc__ or h.handler.__name__
            result[k][p] = [item for item in doc.strip().split("\n")][0]

        if not result.get(k):
            result.pop(k)

    ret = []
    for k, role in result.items():
        data = dict(id = k, label = k, children = [])
        for obj, desc in role.items():
            if uid != '1' and accesses != None and obj not in accesses:
                continue
            data['children'].append(dict(id = obj, label = desc, relate = RELATE_ACCESS.get(obj, [])))

        if data.get('children'):
            ret.append(data)

    return ret


from inspect import isclass
def get_handlers():
    members = {}
    for d in __conf__.ACTION_DIR_NAME:
        members.update(get_members(d,
                       None,
                       lambda m: isclass(m) and issubclass(m, RequestHandler) and hasattr(m, "__urls__") and m.__urls__))

    return members
    #handlers = [(item[0], item[1], h) for h in members.values() for item in h.__urls__]

    #return handlers


import ldap
from ldap.controls import SimplePagedResultsControl
def auth_login(authinfo, username = None, password = None, test = False):
    auth_mode = authinfo.get('mode')

    config = json.loads(authinfo.get('config'))
    if auth_mode == "LDAP":
        host = config.get('host')
        port = config.get('port')
        Server = "ldap://{}:{}".format(host, port)
        baseDN = config.get('basedn')

        ldapuser = config.get('account') or ""
        ldappass = config.get('password') or ""

        dn = ""
        try:
            conn = ldap.initialize(Server)

            #conn.set_option(ldap.OPT_REFERRALS, 0)
            retrieveAttributes = None
            conn.protocol_version = ldap.VERSION3

            conn.simple_bind_s(ldapuser, ldappass)

            if test:
                return True, ""

            searchScope  = ldap.SCOPE_SUBTREE
            searchFiltername = config.get("loginname_property") or "sAMAccountName"
            searchFilter = '(' + searchFiltername + "=" + username +')'

            ldap_result_id = conn.search(baseDN, searchScope, searchFilter, retrieveAttributes)
            result_type, result_data = conn.result(ldap_result_id,1)
            if(not len(result_data) == 0):
                r_a,r_b = result_data[0]
                dn = r_b["distinguishedName"][0].decode()
            else:
                return False, "获取用户DN 失败, 请配置LDAP服务用户名密码"

        except Exception as e:
            return False, str(e)

        if not dn:
            return False, "获取用户Dn失败，请联系管理员检查ldap配置"

        try:
            conn.simple_bind_s(dn, password)
        except Exception as e:
            return False, "用户名密码错误"

        return True, ""

def ldap_search(username):
    auth_info = AuthMode.get_or_none(AuthMode.mode == "LDAP")
    if not auth_info:
        return

    auth_info = model_to_dict(auth_info)

    config = json.loads(auth_info.get('config'))
    host = config.get('host')
    port = config.get('port')
    Server = "ldap://{}:{}".format(host, port)
    baseDN = config.get('basedn')

    ldapuser = config.get('account') or ""
    ldappass = config.get('password') or ""

    dn = ""
    try:
        conn = ldap.initialize(Server)
        retrieveAttributes = ['name', 'sAMAccountName', 'searchFiltername', 'mail']
        conn.protocol_version = ldap.VERSION3
        conn.simple_bind_s(ldapuser, ldappass)

        searchScope  = ldap.SCOPE_SUBTREE
        searchFiltername = config.get("loginname_property") or "sAMAccountName"
        searchFilter = '{}=*{}*'.format(searchFiltername, username)

        pg_ctrl = SimplePagedResultsControl(True, size=20, cookie="")
        ldap_result = conn.search_ext_s(baseDN, searchScope, searchFilter, retrieveAttributes, serverctrls=[pg_ctrl])

        r1 = []
        pg_ctrl = SimplePagedResultsControl(True, size=20, cookie="")
        searchFilter = 'name=*{}*'.format(username)
        r1 = conn.search_ext_s(baseDN, searchScope, searchFilter, retrieveAttributes, serverctrls=[pg_ctrl])

        return True, list(ldap_result) + list(r1)

    except Exception as e:
        return False, str(e)

    return True, []

def getHonorTitle(v):
    if v == 0:
        return "初出茅庐"
    elif v >= 1 and v <= 1000:
        return "小试牛刀"
    elif v >= 1001 and v <= 5000:
        return "初露锋芒";
    elif v >= 5001 and v <= 10000:
        return "小有名气";
    elif v >= 10001 and v <= 20000:
        return "名动一方";
    elif v >= 20001 and v <= 30000:
        return "技冠群雄";
    elif v >= 30001 and v <= 40000:
        return "名震江湖";
    elif v >= 40001 and v <= 50000:
        return "一统千秋";
    elif v >= 50001:
        return "一代宗师";
    else:
        return ""

def get_vul_relate_users(vul_id):
    result = {}
    vul = Vul.get_or_none(Vul._id == vul_id)

    # 漏洞所有者
    user = User.get_or_none(User.id == vul.user_id)
    if user:
        result['user'] = model_to_dict(user)

    app = App.get_or_none(App.id == vul.app_id)

    if app:
        # 漏洞->应用 所属组创建者
        result['groupowner'] = model_to_dict(app.group.owner)

        # 漏洞->应用 所属组成员
        groupusers = GroupUser.select().where(GroupUser.group_id == app.group.id)
        result['groupusers'] = [model_to_dict(item.user) for item in groupusers]

        # 漏洞->应用 安全官
        sec_owner = User.get_or_none(User.id == app.sec_owner)
        if sec_owner:
            result['sec_owner'] = model_to_dict(sec_owner)

    return result

def get_vul_relate_users2(vul_id):
    users = []
    result = get_vul_relate_users(vul_id)

    if result.get("user"):
        users.extend([result["user"]])

    if result.get("groupowner"):
        users.extend([result["groupowner"]])

    if result.get("groupusers"):
        users.extend(result["groupusers"])

    if result.get("groupowner"):
        users.extend([result["groupowner"]])

    return users

