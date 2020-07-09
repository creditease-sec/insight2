#!coding=utf-8
import json
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.define import *
from logic.utility import *

@url(r"/authmode/add", category = "认证")
class AuthModeUpsert(LoginedRequestHandler):
    """
        认证设置

        _id: 认证id
        name: 认证名称*
        mode: 认证类型* [LDAP]
        desc: 描述
        config: JSON 格式 (名称 * 主机 * 端口 * Base DN *)
        enable: 禁用，启用 0, 1
    """
    def post(self):
        _id = self.get_argument('id', '')
        name = self.get_argument('name')
        mode = self.get_argument('mode')
        desc = self.get_argument('desc', '')
        config = self.get_argument('config', "{}") or "{}"
        enable = int(self.get_argument('enable', 1))

        if mode not in AUTH_MODE:
            self.write(dict(status = False, msg = 'mode error'))
            return

        if _id:
            authmode = AuthMode.get_or_none(AuthMode.id == _id)
            last_config = json.loads(authmode.config)
            config = json.loads(config)
            if not config.get("password") and last_config.get("password"):
                config["password"] = last_config.get("password")

            config = json.dumps(config)

            AuthMode.update(name = name, mode = mode, enable = enable, desc = desc, config = config, update_time = time.time()). \
                            where(AuthMode.id == _id). \
                            execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            AuthMode(name = name, mode = mode, enable = enable, desc = desc, config = config).save()
            self.write(dict(status = True, msg = '添加成功'))


@url(r"/authmode/del", category = "认证")
class AuthModeDel(LoginedRequestHandler):
    """
        认证删除

        _id: 认证id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        _id = [int(item) for item in _id]
        AuthMode.delete().where(AuthMode.id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/authmode/list", category = "认证")
class AuthModeList(LoginedRequestHandler):
    """
        认证查询

        search: 查询条件
        page_index: 页码
        page_size: 每页条数
    """
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))
        enable = self.get_argument('enable', None)

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []

        if enable != None:
            cond.append(AuthMode.enable == enable)

        if search:
            cond.append(AuthMode.name.contains(search))

        if not cond:
            cond = (None, )

        if sort:
            sort = getattr(AuthMode, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()

        total = AuthMode.select().where(*cond).count()

        authmode = AuthMode.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        authmode = [model_to_dict(item) for item in authmode]
        for am in authmode:
            am['usercount'] = User.select().where(User.auth_from == am['id']).count()
            config = am['config']
            am['config'] = {}
            if config:
                try:
                    am['config'] = json.loads(config)
                    am['config'].pop("password", None)
                except:
                    pass

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = authmode))


@url(r"/authmode/all", category = "认证")
class AuthModeAll(BaseHandler):
    """
        认证列表
    """
    def get(self):
        authmode = AuthMode.select().where(AuthMode.enable == 1)

        authmode = [model_to_dict(item) for item in authmode]
        for am in authmode:
            am.pop('config')
            am.pop('enable')
            am.pop('create_time')
            am.pop('update_time')

        self.write(dict(status = True, result = authmode))


@url(r"/authmode/test", category = "认证")
class AuthModeTest(LoginedRequestHandler):
    """
        认证测试

        id*: 认证id
    """
    def post(self):
        _id = self.get_argument('id')
        authmode = AuthMode.get_or_none(AuthMode.id == int(_id))
        authmode = model_to_dict(authmode)

        status, msg = auth_login(authmode, test = True)

        self.write(dict(status = status, msg = msg))

