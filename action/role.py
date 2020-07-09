#!coding=utf-8
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import *


@url(r"/role/add", category = "角色")
class RoleAdd(LoginedRequestHandler):
    """
        角色添加编辑

        id: 角色id
        name*: 角色名称
        level*: 级别
        type: 类型(0:系统角色, 1:审核角色)
        accesses: 权限[]
        desc: 描述
    """
    def post(self):
        _id = self.get_argument('id', '')
        name = self.get_argument('name')
        level = int(self.get_argument('level'))
        _type = int(self.get_argument('type', 0))
        accesses = self.get_arguments('accesses')
        desc = self.get_argument('desc', '')

        accesses = [item for item in accesses if "action." in item]
        accesses = ','.join(accesses)

        self.check_role_level(level)

        if _id:
            role = Role.get_or_none(Role._id == _id)
            doc = dict(name = name, level = level, type = _type, desc = desc)
            if role.id != 1 or (role.id == 1 and self.uid == "1"):
                doc['accesses'] = accesses

            Role.update(**doc).where(Role._id == _id).execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            role = Role.get_or_none(Role.name == name)
            if role:
                self.write(dict(status = False, msg = "角色已存在"))
            else:
                Role(name = name, level = level, type = _type, accesses = accesses, desc = desc).save()
                self.write(dict(status = True, msg = '添加成功'))

@url(r"/role/default", category = "角色")
class RoleDefault(LoginedRequestHandler):
    """
        角色设置

        id*: 角色id
        type: 类型(0:系统角色, 1:审核角色)
    """
    def post(self):
        _id = self.get_argument('id')
        _type = int(self.get_argument('type', 0))

        role = Role.get_or_none(Role._id == _id)
        _id = role.id

        self.check_role_id(_id)

        Role.update(default = 0). \
                    where(role.type == _type). \
                    execute()

        Role.update(default = 1). \
                    where(Role.id == _id, role.type == _type). \
                    execute()

        self.write(dict(status = True, msg = '设置成功'))


@url(r"/role/del", category = "角色")
class RoleDel(LoginedRequestHandler):
    """
        角色删除

        id*: 角色id[]
    """
    def post(self):
        _id = self.get_arguments('id')

        role = Role.get_or_none(Role._id == _id)
        if role.id == 1:
            self.write(dict(status = False, msg = '超级管理员角色不可删除'))
            return

        Role.delete().where(Role._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/role/list", category = "角色")
class RoleList(LoginedRequestHandler):
    """
        角色列表

        search: 关键字查询
        type*: 类型(0:系统角色, 1:审核角色)
    """
    def get(self):
        search = self.get_argument('search', None)
        _type = self.get_argument('type', None)

        user = User.get_or_none(User.id == self.uid)
        level = user.role.level

        cond = [Role.level >= level]
        if _type != None:
            cond.append(Role.type == _type)
        if search:
            cond.append(Role.name.contains(search))

        roles = Role.select().where(*cond).order_by(Role.level.asc())
        roles = [model_to_dict(item) for item in roles]

        for role in roles:
            role['id'] = role.pop('_id')
            role['accesses'] = [item for item in role['accesses'].split(",") if item]

        self.write(dict(status = True, result = roles))


@url(r"/role/select", needcheck = False, category = "角色")
class RoleSelect(LoginedRequestHandler):
    """
        角色列表
        type*: 类型(0:系统角色, 1:审核角色)
    """
    def get(self):
        _type = int(self.get_argument('type', 0))
        user = User.get_or_none(User.id == self.uid)
        level = user.role.level

        cond = [Role.level >= level, Role.type == _type]

        roles = Role.select().where(*cond).order_by(Role.level.asc())

        result = []
        for role in roles:
            result.append(dict(id = role._id, name = role.name, default = role.default))

        self.write(dict(status = True, result = result))


@url(r"/access/list", needcheck=False, category = "角色")
class AccessList(LoginedRequestHandler):
    """
        权限列表
    """
    def get(self):
        user = User.get_or_none(User.id == self.uid)
        accesses = user.role.accesses
        ret = access_list(accesses = accesses, uid = self.uid)
        self.write(dict(status = True, result = ret))

