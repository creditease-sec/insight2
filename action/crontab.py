#!coding=utf-8
import json
import time
import zipfile
import threading
import shutil
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler

from logic.define import *


@url(r"/crontab/add", category = "定时任务")
class CronTabAdd(LoginedRequestHandler):
    """
        定时任务增加/编辑

        *id: id
        *name: 名称
        *eid: 扩展id
        *crontab: cron表达式
        relate: 关联类型[SYSTEM,APP,ASSET,VUL,...]
        relate_id: 关联内容的id
        enable: 启用1，禁用0
        remark: 备注
        status: 未执行0; 执行中1; 执行完毕2
    """
    def post(self):
        _id = self.get_argument('id', '')
        name = self.get_argument('name')
        eid = self.get_argument('eid')
        crontab = self.get_argument('crontab')
        relate = self.get_argument('relate', 'SYSTEM')
        relate_id = self.get_argument('relate_id', '')
        enable = int(self.get_argument('enable', 1))
        remark = self.get_argument('remark', '')


        doc = {'name':name,'eid':eid,'crontab':crontab,'relate':relate, \
                'relate_id':relate_id,'enable':enable,'remark':remark}
        
        if _id:
            CronTab.update(**doc).where(CronTab._id == _id).execute()
        else:
            CronTab(**doc).save()
            self.write(dict(status = True, msg = '添加成功'))

@url(r"/crontab/del", category = "定时任务")
class CronTabDel(LoginedRequestHandler):
    """
        定时任务删除

        id: id
    """
    def post(self):
        _id = self.get_argument('id')
        CronTab.delete().where(CronTab._id == _id).execute()
        CronTabLog.delete().where(CronTabLog.crontab_id == _id).execute()
        self.write(dict(status = True, msg = '删除成功'))

@url(r"/crontab/enable", category = "定时任务")
class CronTabEnable(LoginedRequestHandler):
    """
        定时任务启用/禁用

        id: id
        enable: 0:禁用, 1:启用
    """
    def post(self):
        _id = self.get_argument('id')
        enable = int(self.get_argument("enable", 1))
        CronTab.update(enable = enable).where(CronTab._id == _id).execute()

        self.write(dict(status = True, msg = '设置成功'))

@url(r"/crontab/reset", category = "定时任务")
class CronTabReset(LoginedRequestHandler):
    """
        定时任务执行状态重置

        id: id
    """
    def post(self):
        _id = self.get_argument('id')
        CronTab.update(status = 0).where(CronTab._id == _id).execute()
        self.write(dict(status = True, msg = '设置成功'))

@url(r"/crontab/get", category = "定时任务")
class CronTabGet(LoginedRequestHandler):
    """
        获取单条定时任务内容

        id: 根据id查询
    """
    def get(self):
        _id = self.get_argument('id')
        result = model_to_dict(CronTab.get_or_none(CronTab._id == _id))
        result['id'] =result.pop('_id')
        self.write(result)


@url(r"/crontab/list", category = "定时任务")
class CronTabList(LoginedRequestHandler):
    """
        定时任务查询

        search: 查询条件
    """
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))
        sort = self.get_argument('sort', None)
        direction = self.get_argument('direction', '')


        cond = []
        if search:
            cond.append(CronTab.name.contains(search) | CronTab.eid.contains(search) | CronTab.remark.contains(search))

        if not cond:
            cond = (None,)

        if sort:
            sort = getattr(CronTab, sort)
            direction = direction.replace("ending", "")                      
            if direction == 'desc':
                sort = sort.desc()                                                  
        else:
            sort = CronTab.id.desc()

        total = CronTab.select().where(*cond).count()
        result = CronTab.select().where(*cond). \
                    order_by(sort). \
                    paginate(page_index, page_size)

        result = [model_to_dict(item) for item in result]
        for item in result:
            item['id'] =item.pop('_id')

        self.write(dict(total = total, result = result))



@url(r"/crontab/run", category = "定时任务")
class CronTabnRun(LoginedRequestHandler):
    """
        定时任务执行

        id: id
    """
    def get(self):
        _id = self.get_argument('id')
        from logic import crontab
        crontab.run(_id)
        self.write(dict(status = True, msg = '调用成功'))


import croniter
import datetime
from logic.util import *

def get_next_time(sched, now):
    x = sched
    #sched = get_crontab(sched)
    cron = croniter.croniter(sched, now)
    ret = cron.get_next(datetime.datetime)
    return ret


@url(r"/crontab/calendar", category = "定时任务")
class CrontabCalendar(LoginedRequestHandler):
    """
        定时任务日历
    """
    def get(self):
        crontabs = CronTab.select().where(CronTab.enable == 1)
        result = []
        for item in crontabs:
            now = datetime.datetime.now()
            for i in range(1):
                try:
                    start = get_next_time(item.crontab, now)
                except:
                    import traceback
                    traceback.print_exc()
                    continue

                x = dict(title = item.name, \
                        start = str(start).replace(" ", "T"))
                now = start

                result.append(x)

        self.write(dict(result = result))


@url(r"/crontablog/list", category = "定时任务")
class CronTabLogList(LoginedRequestHandler):
    """
        定时任务结果查询

        search: 查询条件
    """
    def get(self):
        crontab_id = self.get_argument('crontab_id')
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        cond = [CronTabLog.crontab_id == crontab_id]

        sort = CronTabLog.id.desc()

        total = CronTabLog.select().where(*cond).count()
        result = CronTabLog.select().where(*cond). \
                    order_by(sort). \
                    paginate(page_index, page_size)

        result = [model_to_dict(item) for item in result]
        for item in result:
            item['id'] =item.pop('_id')

        self.write(dict(total = total, result = result))


