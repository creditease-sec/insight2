#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler



@url(r"/message/del", needcheck=False, category = "消息")
class MessageDel(LoginedRequestHandler):
    """
        消息删除

        message_id[]: 消息id
        is_all: 全部 1
    """
    def post(self):
        is_all = int(self.get_argument('is_all', 0))
        if is_all:
            Message.update(status = 2).where(Message.status == 1, Message.to == self.uid).execute()
        else:
            message_id = self.get_arguments('message_id')
            Message.update(status = 2).where(Message.message_id.in_(message_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/message/restore", needcheck=False, category = "消息")
class MessageRestore(LoginedRequestHandler):
    """
        消息还原

        message_id[]: 消息id
    """
    def post(self):
        message_id = self.get_arguments('message_id')
        Message.update(status = 1).where(Message.message_id.in_(message_id)).execute()

        self.write(dict(status = True, msg = '还原成功'))

@url(r"/message/clear", needcheck=False, category = "消息")
class MessageClear(LoginedRequestHandler):
    """
        消息清空

        message_id[]: 消息id
    """
    def post(self):
        Message.delete().where(Message.status == 2, Message.to == self.uid).execute()
        self.write(dict(status = True, msg = '清空成功'))


@url(r"/message/read", needcheck=False, category = "消息")
class MessageRead(LoginedRequestHandler):
    """
        消息已读

        message_id[]: 消息id
        is_all: 全部 1
    """
    def post(self):
        is_all = int(self.get_argument('is_all', 0))
        if is_all:
            Message.update(status = 1).where(Message.to == self.uid).execute()
        else:
            message_id = self.get_arguments('message_id')
            Message.update(status = 1).where(Message.message_id.in_(message_id)).execute()

        self.write(dict(status = True, msg = '已读'))

@url(r"/message/list", needcheck=False, category = "消息")
class MessageList(LoginedRequestHandler):
    """
        消息查询
    """
    def get(self):
        status = [0, 1, 2]
        status_info = ["unread", "read", "recycle"]
        result = {}

        for no, s in enumerate(status):
            key = status_info[no]

            cond = [Message.to == self.uid]
            cond.append(Message.status == int(s))

            message = Message.select().where(*cond)

            message = [model_to_dict(item) for item in message]
            for msg in message:
                to = msg.pop("to")
                msg['username'] = to.get('nickname') or to.get('username')
                msg['email'] = to.get('email')

            result[key] = message

        self.write(dict(result = result))

