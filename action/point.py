#!coding=utf-8
import json
import time
from hashlib import md5
from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import *
from logic.service import send_pack as service_async


def notify_message(to_uid, title = "", content = ""):
    Message(title = title, content = content, to = to_uid, message_type = "point").save()

    to = []

    user = User.get_or_none(User.id == to_uid)
    if user and user.email:
        to.append(user.email)

    settings = SystemSettings.get_or_none()
    global_setting = json.loads(settings.global_setting)
    isSendEmail = global_setting.get("isSendEmail")
    if isSendEmail != 1:
        return

    if to:
        service_async("service_email", {"msg": title + " " + content, "to": to})


@url(r"/point/frozen", category = "积分")
class PointFrozen(LoginedRequestHandler):
    """
        积分冻结

        id*: 用户id
        point*: 积分
        content: 内容
    """
    def post(self):
        _id = self.get_argument('id')
        _id = User.get_or_none(User._id == _id).id
        point = int(self.get_argument('point'))
        content = self.get_argument('content', '')

        User.update(frozen_points = User.frozen_points + point, available_points = User.available_points - point).where(User.id == _id).execute()

        MessagePoint(title = "冻结积分", from_uid = self.uid, to_uid = _id, \
                    frozen_points = "+ {}".format(point),\
                    available_points = "- {}".format(point), \
                    content = content, \
                ).save()

        notify_message(_id, title = "冻结积分: {}".format(point), content = content)

        self.write(dict(status = True, msg = "积分已冻结"))

@url(r"/point/unfrozen", category = "积分")
class PointUnFrozen(LoginedRequestHandler):
    """
        积分解冻

        id*: 用户id
        point*: 积分
        content: 内容
    """
    def post(self):
        _id = self.get_argument('id')
        _id = User.get_or_none(User._id == _id).id
        point = int(self.get_argument('point'))
        content = self.get_argument('content', '')

        User.update(frozen_points = User.frozen_points - point, available_points = User.available_points + point).where(User.id== _id).execute()

        MessagePoint(title = "解冻积分", from_uid = self.uid, to_uid = _id, \
                    frozen_points = "- {}".format(point),\
                    available_points = "+ {}".format(point), \
                    content = content, \
                ).save()

        notify_message(_id, title = "解冻积分: {}".format(point), content = content)
        self.write(dict(status = True, msg = "积分已解冻"))

@url(r"/point/reward", category = "积分")
class PointReward(LoginedRequestHandler):
    """
        积分奖励

        id*: 用户id
        point*: 积分
        content: 内容
    """
    def post(self):
        _id = self.get_argument('id')
        _id = User.get_or_none(User._id == _id).id
        point = int(self.get_argument('point'))
        content = self.get_argument('content', '')
        User.update(total_points = User.total_points + point, available_points = User.available_points + point).where(User.id== _id).execute()
        MessagePoint(title = "积分奖励", from_uid = self.uid, to_uid = _id, \
                    total_points = "+ {}".format(point),\
                    available_points = "+ {}".format(point), \
                    content = content, \
                ).save()

        notify_message(_id, title = "积分奖励: {}".format(point), content = content)
        self.write(dict(status = True, msg = "积分已奖励"))


@url(r"/point/list", category = "积分")
class PointList(LoginedRequestHandler):
    """
        用户积分

        search: 查询条件
        role_id: 筛选条件
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向

    """
    def get(self):
        search = self.get_argument('search', None)
        role_id = self.get_argument('role_id', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if role_id:
            cond.append(User.role_id == role_id)

        if search:
            cond.append(User.username.contains(search))

        if not cond:
            cond = (None, )

        if sort:
            if sort == 'role_name':
                sort = 'role_id'

            sort = getattr(User, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = User.total_points.desc()

        total = User.select().where(*cond).count()

        users = User.select().where(*cond). \
                        order_by(sort).\
                        paginate(page_index, page_size)

        result = [dict(id = user._id, username = user.username, \
                        total_points = user.total_points, \
                        frozen_points = user.frozen_points, \
                        available_points = user.available_points, \
                        hornor = getHonorTitle(user.total_points), \
                        ) for user in users]

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = result))


@url(r"/point/log", category = "积分")
class PointLog(LoginedRequestHandler):
    """
        用户积分日志

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

        cond = []

        if search:
            cond.append(MessagePoint.title.contains(search))

        if not cond:
            cond = (None, )

        #if sort:
        #    sort = getattr(MessagePoint, sort)
        #    direction = direction.replace("ending", "")
        #    if direction == 'desc':
        #        sort = sort.desc()
        sort = MessagePoint.create_time.desc()

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


