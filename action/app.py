#!coding=utf-8
import os
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler
from logic.util import *

@url(r"/app/add", category = "应用")
class AppAdd(LoginedRequestHandler):
    """
        应用设置

        _id: 应用id
        appname*: 应用名称*
        apptype: 终端，服务
        level:
        sec_level:安全等级
        group_id:
        status:
        comment:
        sec_owner:
        sensitive_data_count:
        sensitive_data:
        business_cata:
        downtime:
        is_open:
        is_interface:
        is_https:

    """
    def post(self):
        _id = self.get_argument('id', '')
        appname = self.get_argument('appname', '')
        apptype = self.get_argument('apptype', 1)
        assets = self.get_arguments('asset_list')
        level = self.get_argument('level', 0)
        sec_level = self.get_argument('sec_level', 0)
        group_id = self.get_argument('group_id')
        status = self.get_argument('status', 0)
        comment = self.get_argument('comment', '')
        sec_owner = self.get_argument('sec_owner', 0)
        sensitive_data_count = self.get_argument('sensitive_data_count', 0)
        sensitive_data = self.get_argument('sensitive_data', '')
        business_cata = self.get_argument('business_cata', '')
        downtime = self.get_argument('downtime', 0)
        is_open = self.get_argument('is_open', 0)
        is_interface = self.get_argument('is_interface', 0)
        is_https = self.get_argument('is_https', 0)

        try:
            group_id = Group.get_or_none(Group._id == group_id).id if group_id else 0
        except Exception as e:
            self.write(dict(status = False, msg = '部门选择错误'))
            return

        try:
            sec_owner = User.get_or_none(User._id == sec_owner).id if sec_owner else 0
        except Exception as e:
            self.write(dict(status = False, msg = '安全官选择错误'))
            return

        doc = dict(appname = appname, apptype = apptype, \
                sec_level = sec_level, \
                downtime = downtime, \
                is_open = is_open, \
                is_interface = is_interface, \
                is_https = is_https, \
                level = level, group_id = group_id, \
                status = status, comment = comment, \
                sec_owner = sec_owner, \
                sensitive_data_count = sensitive_data_count, \
                sensitive_data = sensitive_data, \
                business_cata = business_cata)

        if _id:
            app = App.get_or_none(App._id == _id)
            # 更新前应用下的资产
            assets_old = Asset.select().where(Asset.app_id == app.id)
            assets_old_ids = [item._id for item in assets_old]
            # 需要更新新增加的资产
            assets_new_ids = list(set(assets) - set(assets_old_ids))
            # 遍历判断新增加的是否属于其他应用
            for asset_id in assets_new_ids:
                asset = Asset.get_or_none(Asset._id == asset_id)
                if asset and asset.app_id:
                    app = App.get_or_none(App.id == asset.app_id)
                    if app:
                        self.write(dict(status = False, msg = '资产已关联{}应用'.format(app.appname)))
                        return

            Asset.update(app_id = 0).where(Asset.app_id == app.id).execute()

            for asset_id in assets:
                Asset.update(app_id = app.id). \
                        where(Asset._id == asset_id). \
                        execute()

            App.update(**doc).where(App._id == _id).execute()
            self.write(dict(status = True, msg = '编辑成功'))
        else:
            for asset_id in assets:
                asset = Asset.get_or_none(Asset._id == asset_id)

                if asset.app_id:
                    app = App.get_or_none(App.id == asset.app_id)
                    if app:
                        self.write(dict(status = False, msg = '资产已关联{}应用'.format(app.appname)))
                        return

            app = App(**doc)
            app.save()

            for asset_id in assets:
                Asset.update(app_id = app.id). \
                        where(Asset._id == asset_id). \
                        execute()
            self.write(dict(status = True, msg = '添加成功'))

@url(r"/app/del", category = "应用")
class AppDel(LoginedRequestHandler):
    """
        应用删除

        _id: 应用id[]
    """
    def post(self):
        _id = self.get_arguments('id')

        apps = App.select().where(App._id.in_(_id))
        app_ids = [item.id for item in apps]

        Asset.update(app_id = 0). \
                where(Asset.app_id.in_(app_ids)). \
                execute()

        App.delete().where(App._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))


@url(r"/app/get", category = "应用")
class AppGet(LoginedRequestHandler):
    """
        单个应用查询

        id: 应用id
    """
    def get(self):
        _id = self.get_argument('id')

        app = App.get_or_none(App.id == _id)

        if app:
            app = model_to_dict(app)

            group = app.pop('group')
            app['group_id'] = group.get('id')
            app['group_name'] = group.get('name')
            sec_owner = app.pop('sec_owner')
            if sec_owner:
                user = User.get_or_none(User.id == sec_owner)
                if user:
                    app['sec_owner'] = user.nickname or user.username

            assets = Asset.select().where(Asset.app_id == app.get('id'))
            app['assets'] = [i.id for i in assets]
        else:
            app = {}

        self.write(app)


@url(r"/app/select", needcheck = False, category = "应用")
@url(r"/app/list", category = "应用")
class AppList(LoginedRequestHandler):
    """
        应用查询

        search: 查询条件
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))
        app_id = self.get_argument('app_id', None)

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if search:
            cond.append(App.appname.contains(search))

        if app_id:
            cond.append(App._id == app_id)

        if not cond:
            cond = (None, )

        if sort:
            sort = getattr(App, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = App.id.desc()

        total = App.select().where(*cond).count()

        app = App.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        if "/app/select" in self.request.uri:
            result = []
            for item in app:
                result.append(dict(id = item._id, appname = item.appname))

            self.write(dict(page_index = page_index, \
                                total = total, \
                                result = result))
        else:
            app = [model_to_dict(item) for item in app]

            for item in app:
                group = item.pop('group')
                item['group_id'] = group.get('_id')
                item['group_name'] = group.get('name')
                item['group_owner'] = group.get('owner',{}).get("nickname") or group.get('owner',{}).get("username")

                parent = group.get('parent')
                item['parent_name'] = ''
                if parent:
                    pgroup = Group.get_or_none(Group.id == parent)
                    item['parent_name'] = pgroup.name

                sec_owner = item.pop('sec_owner')
                if sec_owner:
                    user = User.get_or_none(User.id == sec_owner)
                    if user:
                        item['sec_owner'] = user._id
                        item['sec_owner_name'] = user.nickname or user.username

                assets = Asset.select().where(Asset.app_id == item.get('id'))
                item['asset_list'] = [i._id for i in assets]
                item["id"] = item.pop("_id")

            self.write(dict(page_index = page_index, \
                                total = total, \
                                result = app))


@url(r"/app/extension/config", category = "应用")
class AppExConfig(LoginedRequestHandler):
    """
        应用扩展设置

        id: 应用id[]
        eid: 扩展eid
        crontab: crontab 表达式
    """
    def post(self):
        _id = self.get_arguments('id')
        eid = self.get_argument('eid')
        crontab = self.get_argument("crontab")

        App.update(eid = eid, crontab = crontab, op_user_id = self.uid). \
                where(App._id.in_(_id)). \
                execute()

        init_crontab()
        self.write(dict(status = True, msg = '配置成功'))

