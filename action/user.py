#!coding=utf-8
import os
import uuid
import time
import base64
from hashlib import md5

import requests

from tornadoweb import *
from logic.model import *
from logic.utility import *
from logic.util import gen_code, password_md5
from logic.service import mq


def get_default_role():
    role = Role.get_or_none(Role.default == 1)
    role_id = None
    if role:
        role_id = role.id
    else:
        roles = Role.select().where(Role.type == 0)
        roles = [model_to_dict(item) for item in roles]
        if roles:
            role_id = roles[-1].get('id')
    return role_id


@url(r"/login", needcheck = False, category = "用户")
class Login(BaseHandler):
    """
        用户登陆

        username*: 用户名
        password*: 密码
        auth_from: 登陆类型[LOCAL(default), 1, 2, 3, ...]
    """
    def get(self):
        """
        GET DOC
        """
        self.post()

    def post(self):
        username = self.get_argument('username').strip()
        password = self.get_argument('password')

        if not username or not password:
            self.write(dict(status = False, msg = "用户名密码不能为空"))
            return

        code = self.get_argument('code', '')
        auth_from = self.get_argument('type', 'LOCAL')

        if not code:
            self.write(dict(status = False, msg = "请输入验证码"))
            return

        __session__ = self.get_sessionid()
        store_code = mq.get(__session__)
        if not store_code:
            mq.delete(__session__)
            self.write(dict(status = False, msg = "验证码过期,重新生成", refresh = 1))
            return

        if code.lower() != store_code.decode().lower():
            mq.delete(__session__)
            self.write(dict(status = False, msg = "验证码错误,重新生成", refresh = 1))
            return

        def get_role(role_id):
            role = Role.get_or_none(Role.id == role_id)
            if role:
                return model_to_dict(role)

            return {}

        if "@" in username:
            username = username.split("@")[0]

        if auth_from == "LOCAL":
            password = password_md5(password)
            user = User.get_or_none(User.username == username, \
                                    User.password == password)

            if not user:
                mq.delete(__session__)
                self.write(dict(status = False, msg = "用户名或密码错误", refresh = 1))
            elif user.enable == 0:
                self.write(dict(status = False, msg = "用户无法正常登陆，请联系管理员!"))
            elif user.enable == -1:
                self.write(dict(status = False, msg = "用户认证成功，未激活，请联系管理员!"))
            else:
                self.set_secure_cookie("__UID__", str(user.id), expires_days = __conf__.COOKIE_EXPIRES_DAYS)
                self.set_secure_cookie("__AUTHFROM__", "LOCAL")
                User.update(login_time = time.time(), auth_from = "LOCAL").where(User.id == user.id).execute()
                role = model_to_dict(user.role)
                role["id"] = role.pop("_id")
                self.write(dict(status = True, msg = "登陆成功", role = role))
        elif auth_from:
            authinfo = AuthMode.get_or_none(AuthMode.id == auth_from)
            status, msg = auth_login(model_to_dict(authinfo), username, password)
            if not status:
                mq.delete(__session__)
                self.write(dict(status = False, msg = "用户名或密码错误", refresh = 1))
                return
            user = User.get_or_none(User.username == username)
            if not user:
                role_id = get_default_role()
                User(username = username, role_id = role_id, auth_from = auth_from, enable = -1).save()
                self.write(dict(status = False, msg = "用户认证成功，未激活，请联系管理员!"))
            elif user.enable == 0:
                self.write(dict(status = False, msg = "用户无法正常登陆，请联系管理员!"))
            elif user.enable == -1:
                self.write(dict(status = False, msg = "用户认证成功，未激活，请联系管理员!"))
            else:
                self.set_secure_cookie("__UID__", str(user.id), expires_days = __conf__.COOKIE_EXPIRES_DAYS)
                self.set_secure_cookie("__AUTHFROM__", authinfo.mode)
                User.update(auth_from = authinfo.mode, login_time = time.time(), is_del = 0).where(User.id == user.id).execute()
                role = model_to_dict(user.role)
                role["id"] = role.pop("_id")
                self.write(dict(status = True, msg = "登陆成功", role = role))

        mq.delete(__session__)


@url(r"/gencode", needcheck = False, category = "用户")
class Gencode(BaseHandler):
    """
        获取验证码
    """
    def get(self):
        __session__ = self.get_sessionid()
        code, p = gen_code()
        mq.setex(__session__, 60 * 3, code)
        with open(p, "rb") as f:
            data = 'data:image/png;base64,{}'.format(base64.b64encode(f.read()).decode())

        os.remove(p)
        self.write(dict(status = True, image = data))


@url(r"/logout", needcheck = False, category = "用户")
class Logout(BaseHandler):
    """
        用户登出
    """
    def get(self):
        self.clear_cookie("__UID__")
        self.clear_cookie("__AUTHFROM__")
        self.clear_cookie("__S__")

        status = 1
        logout_url = ""

        self.write(dict(msg="登出成功", status = status, logout_url = logout_url))

@url(r"/user/add", category = "用户")
class UserAdd(LoginedRequestHandler):
    """
        用户设置

        id: 用户id
        username*:用户名
        nickname:昵称
        email:邮箱
        password: 用户密码
        role_id: 角色id
        enable: 状态
    """
    def post(self):
        _id = self.get_argument('id', '')
        username = self.get_argument('username')
        email = self.get_argument('email', "")
        nickname = self.get_argument('nickname', '')
        password = self.get_argument('password', '')
        role_id = self.get_argument('role_id', '')
        enable = int(self.get_argument('enable', 1))

        if not role_id:
            role_id = get_default_role()
        else:
            role_id = Role.get_or_none(Role._id == role_id).id

        doc = dict(role_id = role_id, enable = enable, nickname = nickname)
        if password:
            doc['password'] = password_md5(password)

        if email:
            doc['email'] = email

        if _id:
            User.update(update_time = time.time(), **doc). \
                            where(User._id == _id). \
                            execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            user = User.get_or_none(User.username == username)
            if user:
                self.write(dict(status = False, msg = "用户已注册"))
            else:
                user = User(username = username, **doc)
                user.save()
                self.write(dict(status = True, msg = '添加成功', user_id = user._id))


@url(r"/user/setting", needcheck = False, category = "用户")
class UserSetting(LoginedRequestHandler):
    """
        用户个人信息设置

        id: 用户id
        nickname:用户昵称
        avatar: 用户头像
    """
    def post(self):
        _id = self.get_argument('id', '')
        if not _id:
            user = User.get_or_none(User.id == self.uid)
            _id = user._id

        email = self.get_argument('email', "")
        nickname = self.get_argument('nickname', '')
        avatar = self.get_argument('avatar', '')

        doc = {"update_time": time.time()}

        if nickname:
            doc['nickname'] = nickname

        if avatar:
            doc['avatar'] = avatar

        if email:
            doc['email'] = email

        User.update(**doc).where(User._id == _id).execute()

        self.write(dict(status = True, msg = '编辑成功'))


@url(r"/user/password", needcheck = False, category = "用户")
class UserPassword(LoginedRequestHandler):
    """
        密码设置

        old_password*: 旧密码
        new_password*: 新密码
        re_password*: 重复新密码
    """
    def post(self):
        old_password = self.get_argument('old_password', '')
        new_password = self.get_argument('new_password')
        re_password = self.get_argument('re_password')

        if new_password != re_password:
            self.write(dict(status = False, msg = "新密码输入不一致"))
            return

        from logic.password_judge import passwd_judge
        advice = passwd_judge(new_password)
        if advice:
            self.write(dict(status = False, msg = advice))
            return

        user = User.get_or_none(User.id == self.uid)
        if user.password != password_md5(old_password):
            self.write(dict(status = False, msg = "密码错误"))
            return

        User.update(password = password_md5(new_password)).where(User.id == int(self.uid)).execute()
        self.write(dict(status = True, msg = "设置成功"))

@url(r"/user/apikey/get", needcheck = False, category = "用户")
class UserTokenGet(LoginedRequestHandler):
    """
        Token获取

        response: {"status": True, "apikey": "token", "enable": 1}
    """
    def get(self):
        user = User.get_or_none(User.id == int(self.uid))
        self.write(dict(status = True, apikey = user.token, enable = user.token_enable, host = self.request.host))

@url(r"/user/apikey/gen", needcheck = False, category = "用户")
class UserTokenGen(LoginedRequestHandler):
    """
        Token生成

        response: {"status": True, "apikey": "token"}
    """

    def post(self):
        token = password_md5(str(uuid.uuid1()))
        User.update(token = token).where(User.id == int(self.uid)).execute()
        self.write(dict(status = True, apikey = token))

@url(r"/user/apikey/enable", needcheck = False, category = "用户")
class UserTokenEnable(LoginedRequestHandler):
    """
        Token 禁用启用
        enable: 禁用0, 启用1

        response: {"status": True}
    """

    def post(self):
        enable = int(self.get_argument("enable", 1))
        User.update(token_enable = enable).where(User.id == int(self.uid)).execute()
        self.write(dict(status = True))

@url(r"/user/apikey/test", needcheck = False, category = "用户")
class UserTokenTest(LoginedRequestHandler):
    """
        Token 测试

        response: {"status": True}
    """

    def get(self):
        self.write(dict(status = True))


@url(r"/user/del", category = "用户")
class UserDel(LoginedRequestHandler):
    """
        用户删除

        id: 用户id[]
    """
    def post(self):
        _id = self.get_arguments('id')

        users = User.select().where(User._id.in_(_id))
        ids = [user.id for user in users]

        if 1 in ids:
            self.write(dict(status = False, msg = '不能删除admin'))
            return

        if int(self.uid) in ids:
            self.write(dict(status = False, msg = '不能删除自己'))
            return

        Message.delete().where(Message.to.in_(ids)).execute()
        User.delete().where(User._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))


@url(r"/user/list", category = "用户")
class UserList(LoginedRequestHandler):
    """
        用户列表

        search: 查询条件
        role_id: 筛选条件
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向
        group_id: 组id

        response: [{'id': '用户id', 'username': '用户名', 'role': {'id': '角色id', 'name': '角色名'}}]
    """
    def get(self):
        search = self.get_argument('search', None)
        role_id = self.get_argument('role_id', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))
        group_id = self.get_argument('group_id', None)

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = [User.is_del == 0]
        if role_id:
            cond.append(User.role_id == role_id)

        if search:
            cond.append(User.username.contains(search))

        if group_id:
            group = Group.get_or_none(Group._id == group_id)
            # 有父组需要从父组中取用户
            if group.parent:
                groupusers = GroupUser.select().where(GroupUser.group_id == group.parent)
                
                group_usernames = []
                for gu in groupusers:
                    group_usernames.append(gu.user.username)

                cond.append(User.username.in_(group_usernames))

        if not cond:
            cond = (None, )

        if sort:
            if sort == 'role_name':
                sort = 'role_id'

            sort = getattr(User, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()

        total = User.select().where(*cond).count()
        users = User.select().where(*cond). \
                        order_by(sort).\
                        paginate(page_index, page_size)

        result = [dict(id = user._id, username = user.username, \
                        email = user.email, \
                        enable = user.enable, \
                        ldap_online = user.ldap_online, \
                        auth_from = user.auth_from, \
                        create_time = user.create_time, \
                        update_time = user.update_time, \
                        active_time = user.active_time, \
                        login_time = user.login_time, \
                        role_id = user.role._id, \
                        role_name = user.role.name, \
                        total_points = user.total_points, \
                        frozen_points = user.frozen_points, \
                        hornor = getHonorTitle(user.total_points), \
                        ) for user in users]

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = result))

@url(r"/ldap/search", category = "用户")
class LdapSearch(LoginedRequestHandler):
    """
        LDAP搜索用户

        search: 查询条件
    """
    def get(self):
        search = self.get_argument('search', None)
        b, result = ldap_search(search)
        data = []
        for item in result:
            print (item)
            username = item[1].get('sAMAccountName', [b''])[0].decode()
            nickname = item[1].get('name', [b''])[0].decode()
            email = item[1].get('mail', [b''])[0].decode().lower()
            data.append(dict(username = username, nickname = nickname, email = email))

        self.write(dict(status = True, result = data))


@url(r"/user/info", needcheck = False, category = "用户")
class UserInfo(LoginedRequestHandler):
    """
        用户信息
    """
    def get(self):
        user = User.get_or_none(User.id == self.uid)
        message_count = Message.select().where(Message.to == self.uid, Message.status == 0).count()

        cond = []
        group_ids = []
        # 获取用户关联组
        groups = Group.select().where(Group.owner_id == self.uid)
        group_ids = [item.id  for item in groups]

        groups = GroupUser.select().where(GroupUser.user_id == self.uid)
        group_ids.extend([item.group_id for item in groups])
        # 获取用户关联组所有应用
        apps = App.select().where(App.group_id.in_(group_ids))
        app_ids = [item.id  for item in apps]

        if app_ids:
            cond.append(((Vul.user_id == self.uid) | (Vul.app_id.in_(app_ids))))
        else:
            cond.append(Vul.user_id == self.uid)

        todo_vul_count = Vul.select().where(Vul.vul_status.in_([10, 40, 50, 55]), *cond).count()
        done_vul_count = Vul.select().where(Vul.vul_status.in_([20, 30, 35, 60]), *cond).count()

        ex = Extension.select().where(Extension.status == 1)

        extension = {}
        for item in ex:
            doc = {"eid": item.eid, "name": item.name}
            if extension.get(item.type):
                extension[item.type].append(doc)
            else:
                extension[item.type] = [doc]

        accesses = ",".join([item for item in user.role.accesses.split(",") if "action." in item])

        self.set_cookie("__ROLELIST__", accesses)

        settings = SystemSettings.get_or_none()
        global_setting = json.loads(settings.global_setting)
        iwmo = global_setting.get("isWaterMarkOn")

        self.write(dict(username = user.username, \
                nickname = user.nickname, \
                total_points = user.total_points, \
                available_points = user.available_points, \
                frozen_points = user.frozen_points, \
                hornor = getHonorTitle(user.total_points), \
                avatar = user.avatar, \
                message_count = message_count, \
                todo_vul_count = todo_vul_count, \
                done_vul_count = done_vul_count, \
                extension = extension, iwmo = iwmo))


@url(r"/user/point/sort", needcheck = False, category = "用户")
class UserPointSort(LoginedRequestHandler):
    """
        用户积分排行

    """
    def get(self):
        search = self.get_argument('search', '')
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        direction = self.get_argument('direction', '')

        total = User.select().count()

        users = User.select().order_by(User.total_points.desc())

        result = [dict(no = 1 + no, \
                        username = user.nickname or user.username, \
                        total_points = user.total_points, \
                        hornor = getHonorTitle(user.total_points), \
                        ) for no, user in enumerate(users)]

        if search:
            result = [item for item in result if search in item.get('username')]

        if sort:
            if direction == "ascending":
                reverse = False
            else:
                reverse = True

            result = sorted(result, key = lambda item: item[sort], reverse = reverse)

        result = result[(page_index - 1) * page_size: page_index * page_size]

        self.write(dict(page_index = page_index, \
                total = total, \
                result = result))


@url(r"/user/point/log", needcheck = False, category = "用户")
class UserPointLog(LoginedRequestHandler):
    """
        个人用户积分日志

        search: 查询条件
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向

    """
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = [MessagePoint.to_uid == self.uid]

        if search:
            cond.append(MessagePoint.title.contains(search))

        if not cond:
            cond = (None, )

        if sort:
            sort = getattr(MessagePoint, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()

        total = MessagePoint.select().where(*cond).count()

        messages = MessagePoint.select().where(*cond). \
                        order_by(sort).\
                        paginate(page_index, page_size)

        result = [model_to_dict(item) for item in messages]
        for item in result:
            from_uid = item.pop("from_uid")
            to_uid = item.pop("to_uid")
            item['operator'] = ""
            item['relate_user'] = ""
            user = User.get_or_none(User.id == from_uid)
            if user:
                item['operator'] = user.username
            user = User.get_or_none(User.id == to_uid)
            if user:
                item['relate_user'] = user.username

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = result))


@url(r"/user/clear", category = "用户")
class UserClear(LoginedRequestHandler):
    """
        用户清理

        id: 清理id

    """
    def get(self):
        users = User.select().where((User.auth_from == "LDAP") | (User.auth_from == "AMS"), User.ldap_online == 0)
        count = users.count()
        count_week = len([user for user in users if user.ldap_offline_time >= time.time() - 60 * 60 * 24 * 7])
        count_month = len([user for user in users if user.ldap_offline_time >= time.time() - 60 * 60 * 24 * 30])

        data = [{"id": "0", "name": "全部", "count": count},
                {"id": "1", "name": "一个星期", "count": count_week},
                {"id": "2", "name": "一个月", "count": count_month}]

        self.write(dict(result = data))

    def post(self):
        _id = self.get_argument("id", None)

        del_time_flag = "0"
        if _id == "1":
            del_time_flag = time.time() - 60 * 60 * 24 * 7
        elif _id == "2":
            del_time_flag = time.time() - 60 * 60 * 24 * 30

        User.update(is_del = 1).where((User.auth_from == "LDAP") | (User.auth_from == "AMS"), User.ldap_online == 0, User.ldap_offline_time >= del_time_flag).execute()
        self.write(dict(status = True, msg = "清理成功"))


