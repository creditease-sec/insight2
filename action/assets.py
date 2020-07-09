#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler


@url(r"/asset/add", category = "资产")
class AssetAdd(LoginedRequestHandler):
    """
        资产设置

        _id: 资产id
        name: 资产名称*
        type: ip or 域名[0, 1]
        value: ip或者域名
        is_open: 是否外网开放
        is_https: 是否https
        status: 状态
    """
    def post(self):
        _id = self.get_argument('id', '')
        name = self.get_argument('name')
        _type = self.get_argument('type', 1)
        value = self.get_argument('value', '')
        is_open = self.get_argument('is_open', 0)
        is_https = self.get_argument('is_https', 0)
        apptype = self.get_argument('apptype', 10)
        status = self.get_argument('status', 0)

        doc = dict(name = name, type = _type, value = value, \
                is_open = is_open, is_https = is_https, \
                apptype = apptype, status = status)
        if _id:
            Asset.update(**doc). \
                            where(Asset._id == _id). \
                            execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            Asset(**doc).save()
            self.write(dict(status = True, msg = '添加成功'))

@url(r"/asset/del", category = "资产")
class AssetDel(LoginedRequestHandler):
    """
        资产删除

        _id: 资产id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        Asset.delete().where(Asset._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))


@url(r"/asset/get", category = "资产")
class AssetGet(LoginedRequestHandler):
    """
        单个资产查询

        id: 资产id
    """
    def get(self):
        _id = self.get_argument('id')

        asset = Asset.get_or_none(Asset._id == _id)
        if asset:
            asset = model_to_dict(asset)

            app = App.get_or_none(App.id == asset.get('app_id'))
            if app:
                asset['appname'] = app.appname

        else:
            asset = {}

        self.write(asset)

@url(r"/asset/list", category = "资产")
@url(r"/asset/select", needcheck = False, category = "资产")
class AssetList(BaseHandler):
    """
        资产查询

        search: 查询条件
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        app_id = self.get_argument('app_id', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if search:
            cond.append((Asset.name.contains(search) | Asset.value.contains(search)))

        if app_id == "0":
            cond.append(Asset.app_id == int(app_id))
        elif app_id:
            app_id = App.get_or_none(App._id == app_id).id
            cond.append(Asset.app_id == app_id)

        if not cond:
            cond = [None]

        if sort:
            if sort == "appname":
                sort="app_id"
            sort = getattr(Asset, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = Asset.id.desc()

        total = Asset.select().where(*cond).count()

        assets = Asset.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        if "/asset/select" in self.request.uri:
            result = [dict(id = item._id, name = item.name, value = item.value) for item in assets]
            self.write(dict(page_index = page_index, \
                                total = total, \
                                result = result))
        else:
            assets = [model_to_dict(item) for item in assets]

            for asset in assets:
                asset["id"] = asset.pop("_id")
                app = App.get_or_none(App.id == asset.get('app_id'))
                if app:
                    asset['appname'] = app.appname

            self.write(dict(page_index = page_index, \
                                total = total, \
                                result = assets))

@url(r"/asset/all", category = "资产")
class AssetAll(LoginedRequestHandler):
    """
        资产列表

        search: 查询条件
    """
    def get(self):
        search = self.get_argument('search', None)

        cond = (None, )
        if search:
            cond = ((Asset.name.contains(search) | Asset.value.contains(search)), )

        assets = Asset.select().where(*cond)

        assets = [model_to_dict(item) for item in assets]

        ret = []
        for item in assets:
            ret.append(dict(name = item.get('name'), value = item.get('value')))

        self.write(dict(result = ret))


@url(r"/asset/download", needcheck = False, category = "资产")
class AssetDownload(BaseHandler):
    """
        资产下载

        search: 查询条件
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        app_id = self.get_argument('app_id', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if search:
            cond.append((Asset.name.contains(search) | Asset.value.contains(search)))

        if app_id == "0":
            cond.append(Asset.app_id == int(app_id))
        elif app_id:
            app_id = App.get_or_none(App._id == app_id).id
            cond.append(Asset.app_id == app_id)

        if not cond:
            cond = [None]

        if sort:
            if sort == "appname":
                sort="app_id"
            sort = getattr(Asset, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = Asset.id.desc()

        assets = Asset.select().where(*cond). \
                        order_by(sort)

        from logic.define import ASSET_TYPE, ASSET_LEVEL, APP_SEC_LEVEL
        text = "资产名称,资产,类型,是否外网,所属应用,部门,重要程度,安全重要等级,漏洞数量\r\n<br>"
        for asset in assets:
            app = App.get_or_none(App.id == asset.app_id)
            vul_count = 0
            if app:
                vul_count = Vul.select().where(Vul.app_id == app.id).count()

            text += "{},{},{},{},{},{},{},{},{}\r\n<br>".format(asset.name, asset.value, ASSET_TYPE.get(asset.type), asset.is_open, \
                    app.appname if app else "", app.group.name if app and app.group else "", \
                    ASSET_LEVEL.get(str(app.level), "") if app else "", APP_SEC_LEVEL.get(str(app.sec_level), "") if app else "", \
                    vul_count, \
                    )
                    
        self.write(text)


@url(r"/asset/import", category = "资产")
class AssetImport(LoginedRequestHandler):
    """
        资产导入
    """
    def post(self):
        data = self.request.files['file'][0]
        body = data.get('body')
        body = [item.strip().split(",") for item in body.split("\n") if item]
        for item in body[1:]:
            name, value, _type, is_open, is_https, apptype, appname = item
            _ASSET_TYPE = dict((v, k) for k, v in ASSET_TYPE.items())
            _type = _ASSET_TYPE.get(_type) or "10"
            _ASSET_APP_TYPE = dict((v, k) for k, v in ASSET_APP_TYPE.items())
            apptype = _ASSET_APP_TYPE.get(apptype) or "10"
            app_id = 0
            if appname:
                app = App.get_or_none(App.appname == appname)
                if app:app_id = app.id

            asset = Asset.get_or_none(Asset.value == value)
            if not asset:
                Asset(name = name, value = value, type = _type, is_open = is_open, is_https = is_https, app_id = app_id).save()
