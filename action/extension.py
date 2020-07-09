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

from logic import extension
from logic.define import *


@url(r"/extension/upload", category = "扩展")
class ExtensionUpload(LoginedRequestHandler):
    """
        扩展设置

        remark: 备注
    """
    def post(self):
        remark = self.get_argument('remark', "")

        data = self.request.files['file'][0]
        filename = data.get('filename')

        if not filename.endswith('.zip'):
            self.write(dict(status = False, msg = 'NOT ZIP ARCHIVE'))
            return

        body = data.get('body')
        data_md5 = md5(body).hexdigest()

        filename = "{}.zip".format(data_md5)
        zip_file = os.path.join("/tmp", filename)

        with open(zip_file, 'wb') as f:
            f.write(body)

        ex_path = os.sep.join(['{}/extensions'.format(__conf__.STATIC_DIR_NAME), data_md5])
        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(ex_path)
        zip_ref.close()
        os.remove(zip_file)

        if "config.json" not in os.listdir(ex_path):
            shutil.rmtree(ex_path)
            self.write(dict(status = False, msg = '扩展应用中未找到config.json文件'))
            return

        config_path = os.path.join(ex_path, "config.json")
        with open(config_path, 'r') as f:
            import json
            try:
                config = json.loads(f.read())
            except:
                self.write(dict(status = False, msg = 'config.json文件格式错误'))
                return
            eid = config.get('eid', '')
            name = config.get('name', '')
            desc = config.get('desc', '')
            config_template = config.get('args', '')
            version = config.get('version')
            _type = config.get('type')
            if _type not in [str(item) for item in range(8)]:
                self.write(dict(status = False, msg = '扩展类型错误'))
                return


        ex = Extension.get_or_none(Extension.eid == eid)
        if not eid:
            self.write(dict(status = False, msg = '扩展eid不能为空'))
            return
        if ex and ex.version == version:
            self.write(dict(status = False, msg = '扩展已存在'))
            return
        elif ex:
            ex_path = os.sep.join(['{}/extensions'.format(__conf__.STATIC_DIR_NAME), ex.path])
            shutil.rmtree(ex_path)
            Extension.update(config_template = json.dumps(config_template), desc = desc, name = name, type = _type, path = data_md5, version = version, remark = remark ).where(Extension.eid == eid).execute()
        else:
            Extension(config_template = json.dumps(config_template), desc = desc, name = name, eid = eid, type = _type, path = data_md5, version = version, remark = remark ).save()
        self.write(dict(status = True, msg = '添加成功'))

@url(r"/extension/del", category = "扩展")
class ExtensionDel(LoginedRequestHandler):
    """
        扩展删除

        eid: 扩展eid
    """
    def post(self):
        eid = self.get_argument('eid')

        ex = Extension.get_or_none(Extension.eid == eid)
        ex_path = os.sep.join(['{}/extensions'.format(__conf__.STATIC_DIR_NAME), ex.path])
        shutil.rmtree(ex_path)
        Extension.delete().where(Extension.eid == eid).execute()


        self.write(dict(status = True, msg = '删除成功'))

@url(r"/extension/enable", category = "扩展")
class ExtensionEnable(LoginedRequestHandler):
    """
        扩展启用禁用

        eid: 扩展eid
        status: 0:禁用, 1:启用
    """
    def post(self):
        eid = self.get_argument('eid')
        status = int(self.get_argument("status", 0))
        Extension.update(status = status).where(Extension.eid == eid).execute()

        self.write(dict(status = True, msg = '设置成功'))


@url(r"/extension/list", category = "扩展")
class ExtensionList(LoginedRequestHandler):
    """
        扩展查询

        search: 查询条件
    """
    def get(self):
        search = self.get_argument('search', None)

        cond = []
        if search:
            cond.append(Extension.name.contains(search) | Extension.eid.contains(search))

        if not cond:
            cond = (None,)

        extension = Extension.select().where(*cond)
        extension = [model_to_dict(item) for item in extension]
        for no, ex in enumerate(extension):
            ex.pop('id')
            ex['no'] = no
            ex['status'] = ex.get('status')
            ex['path'] = "{}/extensions/{}/logo.png".format(__conf__.STATIC_DIR_NAME, ex.get('path'))
            ex['config_template'] =json.loads(ex.get('config_template'))
            ex['config'] =json.loads(ex.get('config') or "{}")

        self.write(dict(result = extension))


@url(r"/extension/config", category = "扩展")
class ExtensionConfig(LoginedRequestHandler):
    """
        扩展参数配置

        eid: 扩展eid
        kwargs: 其他动态配置参数
    """
    def post(self):
        kwargs = dict((k, v[-1]) for k, v in self.request.arguments.items())
        for k in kwargs.keys():
            kwargs[k] = kwargs[k].decode()

        eid = kwargs.pop("eid")
        config = json.dumps(kwargs)
        Extension.update(config = config).where(Extension.eid == eid).execute()

        self.write(dict(status = True, msg = '配置成功'))


@url(r"/extension/run", category = "扩展")
class ExtensionRun(LoginedRequestHandler):
    """
        扩展测试调用

        eid: 扩展eid
        app_id: 应用id
        info: 说明
    """
    def post(self):
        eid = self.get_argument('eid')
        app_id = self.get_argument('app_id')
        content = self.get_argument('content', '')

        t = threading.Thread(target=extension.run, args=(eid, app_id, 1, content, ))
        t.daemon = True
        t.start()

        self.write(dict(status = True, msg = '调用成功'))

@url(r"/extension/log/add", category = "扩展")
class ExtensionLogAdd(LoginedRequestHandler):
    """
        扩展日志登记

        title:
        content: 内容
    """
    def post(self):
        app_id = self.get_argument('app_id')
        app = App.get_or_none(App.id == app_id)
        title = SEC_UTEST_TYPE.get(self.get_argument('title'))
        content = self.get_argument('content')
        log_doc = {}
        log_doc['app_id'] = app_id
        log_doc['op_user_id'] = self.uid

        ExtensionLog(is_auto = 1, title = title, content = content, **log_doc).save()
        App.update(check_time = time.time()).where(App._id == app_id).execute()
        self.write(dict(status = True, msg = "成功"))

@url(r"/extension/log/list", category = "扩展")
class ExtensionLogList(LoginedRequestHandler):
    """
        扩展调用日志查询

        search: 查询条件
    """
    def get(self):
        search = self.get_argument('search', None)
        start = float(self.get_argument('start', 0))
        end = float(self.get_argument('end', 0))
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if search:
            cond.append(ExtensionLog.content.contains(search))

        if start and end:
            cond.append(ExtensionLog.create_time >= start)
            cond.append(ExtensionLog.create_time <= end)

        if not cond:
            cond = [None]

        if sort:
            sort = getattr(ExtensionLog, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = ExtensionLog.id.desc()

        total = ExtensionLog.select().where(*cond).count()
        ex_log = ExtensionLog.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        ex_log = [model_to_dict(item) for item in ex_log]

        for item in ex_log:
            user = User.get_or_none(User.id == item.get('op_user_id'))
            if user:
                item['op_username'] = user.nickname or user.username

            app = App.get_or_none(App.id == item.get('app_id'))
            if app:
                item['app_name'] = app.appname

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = ex_log))


import croniter
import datetime
from logic.util import *

def get_next_time(sched, now):
    x = sched
    sched = get_crontab(sched)
    cron = croniter.croniter(sched, now)
    ret = cron.get_next(datetime.datetime)
    return ret


@url(r"/extension/crontab/calendar", category = "扩展")
class ExtensionCrontabCalendar(LoginedRequestHandler):
    """
        扩展定时任务日历转化
    """
    def get(self):
        apps = App.select().where(App.eid != "", App.crontab != "")
        result = []
        for app in apps:
            ex = Extension.get_or_none(Extension.eid == app.eid)
            if not ex: continue

            now = datetime.datetime.now()
            for i in range(1):
                try:
                    start = get_next_time(app.crontab, now)
                except:
                    import traceback
                    traceback.print_exc()
                    continue

                item = dict(title = "{} {}".format(ex.name, app.appname), \
                        start = str(start).replace(" ", "T"))
                now = start

                result.append(item)

        self.write(dict(result = result))
