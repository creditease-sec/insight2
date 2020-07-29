#!coding=utf-8
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import *

@url(r"/vullog/del", category = "漏洞日志")
class VulLogDel(LoginedRequestHandler):
    """
        漏洞日志删除

        id*: 漏洞日志id[]
    """
    def post(self):
        _id = self.get_arguments('id')

        VulLog.delete().where(VulLog._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/vullog/list", category = "漏洞日志")
class VulLogList(LoginedRequestHandler):
    """
        漏洞日志/时间线

        search: 关键字查询
        vul_id: 漏洞id
        user_id: 用户id
        start: 开始时间
        end: 结束时间
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        vul_id = self.get_argument('vul_id', None)
        user_id = self.get_argument('user_id', None)
        start = float(self.get_argument('start', 0))
        end = float(self.get_argument('end', 0))
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []

        if search:
            cond.append((VulLog.title.contains(search) | VulLog.username.contains(search) | VulLog.action.contains(search) | VulLog.content.contains(search),))

        if start and end:
            cond.append(VulLog.create_time >= start)
            cond.append(VulLog.create_time <= end)

        if vul_id:
            if len(vul_id) < 24:
                cond.append(VulLog.vul_id == int(vul_id))
            else:
                vul = Vul.get_or_none(Vul._id == vul_id)
                if vul:
                    cond.append(VulLog.vul_id == int(vul.id))

        if user_id:
            cond.append(VulLog.user_id == int(user_id))

        if not cond:
            cond = [None]

        if sort:
            sort = getattr(VulLog, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = VulLog.id.desc()

        total = VulLog.select().where(*cond).count()

        vullogs = VulLog.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        vullogs = [model_to_dict(item) for item in vullogs]
        for vullog in vullogs:
            vullog['id'] = vullog.pop("_id", None)

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = vullogs))


