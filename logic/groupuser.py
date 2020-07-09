#!encoding=utf-8

import time
from logic.model import *


def group_user(group_id, page_index = 1, page_size = 10, findall = False):
    if findall == True:
        groupusers = GroupUser.select().where(GroupUser.group_id == group_id)
    else:
        groupusers = GroupUser.select().where(GroupUser.group_id == group_id).paginate(page_index, page_size)

    groupusers = [model_to_dict(item) for item in groupusers]
    for groupuser in groupusers:
        groupuser["id"] = groupuser.pop("_id")
        user = groupuser.pop("user", {})
        group = groupuser.pop("group", {})
        role = groupuser.pop("role", {})
        groupuser["user_id"] = user.get("_id")
        groupuser["user_name"] = user.get("username")
        groupuser["group_id"] = group.get("_id")
        groupuser["group_name"] = group.get("name")
        groupuser["role_id"] = role.get("_id")
        groupuser["role_name"] = role.get("name")

    return groupusers

