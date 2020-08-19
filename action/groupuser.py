#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.groupuser import group_user
from logic.utility import LoginedRequestHandler


@url(r"/groupuser/add", category = "用户组")
class GroupUserUpsert(LoginedRequestHandler):
    """
        组用户设置

        group_id*: 组id
        user_id*: 用户id
        role_id*: 角色id
    """
    def post(self):

        _id = self.get_argument('id', '')
        role_id = self.get_argument('role_id')
        role_id = Role.get_or_none(Role._id == role_id).id

        if _id:
            GroupUser.update(role_id = role_id).where(GroupUser._id == _id).execute()
            self.write(dict(status = True, msg = '更新成功'))
        else:
            group_id = self.get_argument('group_id')
            group_id = Group.get_or_none(Group._id == group_id).id
            user_ids = self.get_arguments('user_id')
            user_ids = [item.id for item in User.select().where(User._id.in_(user_ids))]

            settings = SystemSettings.get_or_none()
            global_setting = json.loads(settings.global_setting)
            group_member_limit = global_setting.get("group_member_limit")

            count = GroupUser.select().where(GroupUser.group_id == group_id).count()
            if count >= int(group_member_limit):
                self.write(dict(status = False, msg = '超过组最大成员数'))
                return

            for user_id in user_ids:
                groupuser = GroupUser.get_or_none(group_id = group_id, user_id = user_id)
                if not groupuser:
                    GroupUser(group_id = group_id, user_id = user_id, role_id = role_id).save()

            self.write(dict(status = True, msg = '添加成功'))


@url(r"/groupuser/del", category = "用户组")
class GroupUserDel(LoginedRequestHandler):
    """
        组用户删除

        _id: 用户组id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        GroupUser.delete().where(GroupUser._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/groupuser/list", category = "用户组")
class GroupUserList(LoginedRequestHandler):
    """
        组用户查询

        group_id*: 组id
        page_index: 页码
        page_size: 每页条数
    """
    def get(self):
        group_id = self.get_argument('group_id')
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        group_id = Group.get_or_none(Group._id == group_id).id

        total = GroupUser.select().count()

        groupusers = group_user(group_id, page_index = page_index, page_size = page_size, findall = True)

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = groupusers))

