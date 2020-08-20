#!coding=utf-8
import time
import json
from hashlib import md5
from datetime import datetime

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import *
from logic.define import *
from logic.util import *

@url(r"/vul/add", needcheck = False, category = "漏洞")
class VulAdd(LoginedRequestHandler):
    """
        漏洞新增/编辑

        _id: 漏洞id
        vul_name          
        vul_type          
        vul_level         
        self_rank         
        vul_desc_type     
        vul_poc           
        vul_poc_html      
        vul_solution      
        vul_solution_html 
        paper_id: 解决方案id
        reply             
        vul_status        
        asset_level       
        real_rank         
        score             
        risk_score        
        left_risk_score: 剩余风险值
        app_id: 关联应用
        vul_source: 漏洞来源
        send_msg          
        is_retest         
        layer:漏洞层面
    """
    def post(self):
        _id               =    self.get_argument('id', '')
        app_id = self.get_argument("app_id")
        app_id = App.get_or_none(App._id == app_id).id if app_id else 0

        doc = dict(
            vul_name          = self.get_argument("vul_name"),
            vul_type          = self.get_argument("vul_type", 0),
            vul_level         = self.get_argument("vul_level", 0),
            self_rank         = self.get_argument("self_rank", ""),
            vul_desc_type     = self.get_argument("vul_desc_type", 0),
            vul_poc           = self.get_argument("vul_poc", ""),
            vul_poc_html      = self.get_argument("vul_poc_html", ""),
            vul_solution      = self.get_argument("vul_solution", ""),
            vul_solution_html = self.get_argument("vul_solution_html", ""),
            user_id = self.uid,
            article_id        = self.get_argument("article_id", ""),
            vul_status        = self.get_argument("vul_status", 10),
            asset_level       = self.get_argument("asset_level", 0),
            real_rank         = self.get_argument("real_rank", 0),
            score             = self.get_argument("score", 0),
            risk_score        = self.get_argument("risk_score", 0),
            left_risk_score   = self.get_argument("left_risk_score", 0),
            app_id            = app_id,
            vul_source        = self.get_argument("vul_source", 0),
            is_retest         = self.get_argument("is_retest", 0),
            layer             = self.get_argument("layer", 0),
            update_time       = time.time()
        )

        vul_status = int(doc.get("vul_status", 10))
        if vul_status in [40, 60]:
            doc["audit_time"] = time.time()
        elif vul_status in [50]:
            doc["notice_time"] = time.time()
        elif vul_status in [20, 30, 35, 60]:
            doc["fix_time"] = time.time()

        if _id:
            Vul.update(**doc). \
                        where(Vul._id == _id). \
                        execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            doc["user_id"] = self.uid
            Vul(**doc).save()
            self.write(dict(status = True, msg = '添加成功'))

@url(r"/vul/del", needcheck=False, category = "漏洞")
class VulDel(LoginedRequestHandler):
    """
        漏洞删除

        _id: 漏洞id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        Vul.delete().where(Vul._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/vul/delay", category = "漏洞")
class VulDelay(LoginedRequestHandler):
    """
        漏洞延期处理

        id: 漏洞id
        delay_days:延期天数
        delay_reason: 延期原因
    """
    def post(self):
        _id = self.get_argument('id')
        delay_days = self.get_argument("delay_days", 0)
        delay_reason = self.get_argument("delay_reason", "")
        Vul.update(delay_days = delay_days, delay_reason = delay_reason).where(Vul._id == _id).execute()

        self.write(dict(status = True, msg = '延期成功'))


@url(r"/vul/send_notification_email", category = "漏洞")
class VulSendNotificationEmail(LoginedRequestHandler):
    """
        漏洞手动发送邮件

        id: 漏洞id
        title: 标题
        content: 内容
    """
    def get(self):
        self.post(self)

    def post(self):
        _id = self.get_argument("id")
        title = self.get_argument("title", "")
        content = self.get_argument("content", "")

        users = get_vul_relate_users2(_id)
        user_ids = [user.get("id") for user in users]
        to = [user.get("email") for user in users if user.get("email")]
        #if int(self.uid) not in user_ids:
        #    self.send_error(403, msg = "无权操作此漏洞")
        #    return

        from logic.service import send_pack as service_async

        settings = SystemSettings.get_or_none()
        global_setting = json.loads(settings.global_setting)

        vul = Vul.get_or_none(Vul._id == _id)

        title = title or vul.vul_name
        data = {"vul_name": vul.vul_name, \
                "url": "{}/#/n_viewvulndetail?id={}".format(global_setting.get("domian"), vul._id), \
                "title": title, \
                "status": VUL_STATUS.get(str(vul.vul_status), ""), \
                "content": content}

        from tornado import template
        loader = template.Loader("template")
        text = loader.load("alert.html").generate(data = data)
        service_async("service_email", {"msg": text, "to": to, "title": title})

        self.write(dict(status = True, msg = '邮件已发送'))


@url(r"/vul/nget", needcheck = False, category = "漏洞")
@url(r"/vul/get", needcheck = False, category = "漏洞")
class VulGet(LoginedRequestHandler):
    """
        单个漏洞查询

        id: 漏洞id
    """
    def get(self):
        _id = self.get_argument('id')

        vul = Vul.get_or_none(Vul._id == _id)

        if "/vul/nget" in self.request.uri and vul.vul_status != 60:
            users = get_vul_relate_users2(_id)
            user_ids = [user.get("id") for user in users]
            if int(self.uid) not in user_ids:
                self.send_error(403, msg = "无权查看该漏洞详情")
                return

        if vul:
            vul = model_to_dict(vul)

            user = User.get_or_none(User.id == vul.get('user_id'))
            if user:
                vul['username'] = user.username

            app_id = vul.get('app_id')
            if app_id:
                app = App.get_or_none(App.id == app_id)
                vul['appname'] = app.appname
        else:
            vul = {}

        self.write(vul)


@url(r"/vul/list", category = "漏洞")
class VulList(LoginedRequestHandler):
    """
        漏洞列表

        search: 查询条件
        vul_status: 漏洞状态
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        vul_status = self.get_arguments('vul_status')
        is_related_me = self.get_argument('is_related_me', None)
        vul_type = self.get_arguments('vul_type')
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []

        if is_related_me == '1':
            apps = App.select().where(App.sec_owner == int(self.uid))
            app_ids = [item.id  for item in apps]
            cond.append((Vul.app_id.in_(app_ids)) | (Vul.user_id == int(self.uid)))

        if vul_status:
            cond.append(Vul.vul_status.in_(vul_status))

        if vul_type:
            cond.append(Vul.vul_type.in_(vul_type))

        if search:
            cond.append(Vul.vul_name.contains(search))

        if not cond:
            cond = [None]

        if sort and sort not in ["username"]:
            sort = getattr(Vul, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        elif is_related_me == '1':
            sort = Vul.vul_status.asc()
        else:
            sort = Vul.id.desc()

        total = Vul.select().where(*cond).count()

        vuls = Vul.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        vuls = [model_to_dict(item) for item in vuls]
        for vul in vuls:
            vul["id"] = vul.pop("_id")
            user = User.get_or_none(User.id == vul.get('user_id'))
            if user:
                vul['username'] = user.username

            app_id = vul.get('app_id')
            if app_id:
                app = App.get_or_none(App.id == app_id)
                if app:
                    vul['app_id'] = app._id
                    vul['appname'] = app.appname
                    group = app.group
                    if group:
                        vul['group_name'] = group.name
                        vul['group_id'] = group._id

                        parent = group.parent
                        vul['parent_name'] = ''
                        if parent:
                            pgroup = Group.get_or_none(Group.id == parent)
                            vul['parent_name'] = pgroup.name


                    vul['remaining_time'] = None
                    if vul.get("audit_time"):
                        app = model_to_dict(app)
                        risk_score, repair_time = get_risk_score_and_end_date(vul.get("real_rank"), app)
                        start_date = datetime.fromtimestamp(vul.get("audit_time"))
                        remaining_time = (start_date - datetime.now()).days + repair_time
                        vul['remaining_time'] = remaining_time

            article_id = vul.get('article_id')
            if article_id:
                article = Article.get_or_none(Article._id == article_id)
                if article: vul['article_name'] = article.title

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = vuls))


# 开放已解决漏洞
@url(r"/vul/open/list", needcheck = False, category = "漏洞")
class VulOpen(LoginedRequestHandler):
    """
        漏洞列表

        search: 查询条件
        vul_status: 漏洞状态
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        vul_status = self.get_arguments('vul_status')
        vul_type = self.get_arguments('vul_type')
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []

        cond.append(Vul.vul_status.in_([60]))

        if vul_type:
            cond.append(Vul.vul_type.in_(vul_type))

        if search:
            cond.append(Vul.vul_name.contains(search))

        if not cond:
            cond = [None]

        if sort and sort not in ["username"]:
            sort = getattr(Vul, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = Vul.id.desc()

        total = Vul.select().where(*cond).count()

        vul = Vul.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        vuls = [model_to_dict(item) for item in vul]
        for vul in vuls:
            vul["id"] = vul.pop("_id")
            user = User.get_or_none(User.id == vul.get('user_id'))
            if user:
                vul['username'] = user.username

            app_id = vul.get('app_id')
            if app_id:
                app = App.get_or_none(App.id == app_id)
                if app:
                    vul['app_id'] = app._id
                    vul['appname'] = app.appname

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = vuls))

# 我的漏洞
@url(r"/vul/my/list", needcheck = False, category = "漏洞")
class VulMy(LoginedRequestHandler):
    """
        我的漏洞列表

        search: 查询条件
        vul_status: 漏洞状态 0:待处理, 1:已完成
        page_index: 页码
        page_size: 每页条数
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        vul_status = self.get_argument('vul_status', "0")
        vul_type = self.get_arguments('vul_type')
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []

        group_ids = []
        # 获取用户关联组
        groups = Group.select().where(Group.owner_id == self.uid)
        group_ids = [item.id  for item in groups]

        groups = GroupUser.select().where(GroupUser.user_id == self.uid)
        group_ids.extend([item.group_id for item in groups])
        # 获取用户关联组所有应用
        apps = App.select().where(App.group_id.in_(group_ids))
        app_ids = [item.id  for item in apps]

        if app_ids:
            cond.append(((Vul.user_id == self.uid) | (Vul.app_id.in_(app_ids))))
        else:
            cond.append(Vul.user_id == self.uid)

        if vul_status == "0":
            cond.append(Vul.vul_status.in_([10, 40, 50, 55]))
        elif vul_status == "1":
            cond.append(Vul.vul_status.in_([20, 30, 35, 60]))
        else:
            cond.append(Vul.vul_status.in_([int(vul_status)]))


        if vul_type:
            cond.append(Vul.vul_type.in_(vul_type))

        if search:
            cond.append(Vul.vul_name.contains(search))

        if not cond:
            cond = [None]

        if sort and sort not in ["username"]:
            sort = getattr(Vul, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = Vul.id.desc()

        total = Vul.select().where(*cond).count()

        vul = Vul.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        vuls = [model_to_dict(item) for item in vul]
        for vul in vuls:
            vul["id"] = vul.pop("_id")
            user = User.get_or_none(User.id == vul.get('user_id'))
            if user:
                vul['username'] = user.username

            app_id = vul.get('app_id')
            if app_id:
                app = App.get_or_none(App.id == app_id)
                if app:
                    vul['appname'] = app.appname

            article_id = vul.get('article_id')
            if article_id:
                article = Article.get_or_none(Article._id == article_id)
                if article: vul['article_name'] = article.title

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = vuls))



@url(r"/vul/my/export", needcheck = False, category = "漏洞")
@url(r"/vul/export", category = "漏洞")
class VulExport(LoginedRequestHandler):
    """
        漏洞导出

        search: 查询条件
        vul_status: 漏洞状态
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        vul_status = self.get_argument('vul_status', None)

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if "/vul/my/export" in self.request.uri:
            cond.append(Vul.user_id == self.uid)

        if vul_status == "0":
            cond.append(Vul.vul_status.in_([10, 40, 50, 55]))
        elif vul_status == "1":
            cond.append(Vul.vul_status.in_([20, 30, 35, 60]))
        elif vul_status:
            cond.append(Vul.vul_status.in_([int(vul_status)]))

        if search:
            cond.append(Vul.vul_name.contains(search))

        if not cond:
            cond = [None]

        if sort:
            sort = getattr(Vul, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = Vul.id.desc()


        vuls = Vul.select(Vul, User).join(User, JOIN.LEFT_OUTER, on=(Vul.user_id == User.id,)).where(*cond)

        data = ""
        for vul in vuls[:]:
            if hasattr(vul, "user"):
                username = vul.user.username
            else:
                username = ""

            data += "{},{},{},{},{},{}\r\n".format(vul.vul_name, VUL_TYPE.get(str(vul.vul_type), ""), \
                        vul.self_rank, username, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(vul.submit_time)), \
                        VUL_STATUS.get(str(vul.vul_status), ""))

        title = "漏洞名称,类型,Rank,提交人,提交时间,状态\r\n"

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'filename=VUL_{}.csv'.format(str(datetime.now())))
        self.write(title + data)


@url(r"/vul/status/group", needcheck=False, category = "漏洞")
class VulStatusGroup(LoginedRequestHandler):
    """
        漏洞状态统计

    """
    def get(self):
        is_related_me = self.get_argument("is_related_me", None)

        cond = []
        if is_related_me == '1':
            apps = App.select().where(App.sec_owner == int(self.uid))
            app_ids = [item.id  for item in apps]
            cond.append((Vul.app_id.in_(app_ids)) | (Vul.user_id == int(self.uid)))

        if cond:
            values = Vul.select(Vul.vul_status, fn.SUM(1)).where(*cond).group_by(Vul.vul_status).tuples()
        else:
            values = Vul.select(Vul.vul_status, fn.SUM(1)).group_by(Vul.vul_status).tuples()

        result = []

        for k, v in values:
            result.append(dict(id = k, name = VUL_STATUS.get(str(k)), count = int(v)))

        self.write(dict(result = result))


@url(r"/vul/my/status/group", needcheck = False, category = "漏洞")
class VulMyStatusGroup(LoginedRequestHandler):
    """
        漏洞状态统计

        vul_status: 漏洞状态 0:待处理, 1:已完成
    """
    def get(self):
        vul_status = self.get_argument("vul_status", "0")

        cond = []

        group_ids = []
        # 获取用户关联组
        groups = Group.select().where(Group.owner_id == self.uid)
        group_ids = [item.id  for item in groups]

        groups = GroupUser.select().where(GroupUser.user_id == self.uid)
        group_ids.extend([item.group_id for item in groups])
        # 获取用户关联组所有应用
        apps = App.select().where(App.group_id.in_(group_ids))
        app_ids = [item.id  for item in apps]

        if app_ids:
            cond.append(((Vul.user_id == self.uid) | (Vul.app_id.in_(app_ids))))
        else:
            cond.append(Vul.user_id == self.uid)

        if vul_status == "0":
            cond.append(Vul.vul_status.in_([10, 40, 50, 55]))
        elif vul_status == "1":
            cond.append(Vul.vul_status.in_([20, 30, 35, 60]))

        values = Vul.select(Vul.vul_status, fn.SUM(1)).where(*cond).group_by(Vul.vul_status).tuples()

        result = []

        for k, v in values:
            result.append(dict(id = k, name = VUL_STATUS.get(str(k)), count = int(v)))

        self.write(dict(result = result))


@url(r"/vul/download", needcheck = False, category = "漏洞")
class VulDownload(LoginedRequestHandler):
    """
        漏洞列表

        search: 查询条件
        vul_status: 漏洞状态
        sort: 排序字段
        direction: 排序方向[asc, desc]ending
    """
    def get(self):
        search = self.get_argument('search', None)
        vul_status = self.get_arguments('vul_status')
        vul_type = self.get_arguments('vul_type')

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []

        if vul_status:
            cond.append(Vul.vul_status.in_(vul_status))

        if vul_type:
            cond.append(Vul.vul_type.in_(vul_type))

        if search:
            cond.append(Vul.vul_name.contains(search))

        if not cond:
            cond = [None]

        if sort and sort not in ["username"]:
            sort = getattr(Vul, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()
        else:
            sort = Vul.id.desc()

        vuls = Vul.select().where(*cond). \
                        order_by(sort)

        text = "漏洞名称,类型,Rank,提交人,提交时间,状态,是否外网,部门,应用,资产信息\r\n<br>"
        for vul in vuls:
            user = User.get_or_none(User.id == vul.user_id)
            app = App.get_or_none(App.id == vul.app_id)
            assets = Asset.select().where(Asset.app_id == vul.app_id)
            assets_text = ""
            if assets:
                assets_text = "|".join([asset.value for asset in assets])

            text += "{},{},{},{},{},{},{},{},{},{}\r\n<br>".format(vul.vul_name, VUL_TYPE.get(str(vul.vul_type), ""), vul.real_rank,user.username if user else "", \
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(vul.submit_time)), VUL_STATUS.get(str(vul.vul_status), ""), app.is_open if app else "", \
                        app.group.name if app and app.group else "", app.appname if app else "", assets_text)


        self.write(text)

@url(r"/vul/import", category = "漏洞")
class VulImport(BaseHandler):
    """
        漏洞导入

    """
    def get(self):
        self.post()

    def post(self):
        data = self.request.body
        data = b'[{"ip":"10.134.136.89","user_group":"shiro-CVE-2020-11989\xe6\xbc\x8f\xe6\xb4\x9e\xe9\x80\x9a\xe5\x91\x8a\xe7\xbb\x84","leader":"fangzhouli@creditease.cn|xiaojunzhang@creditease.cn","app":"\xe5\xae\x9c\xe4\xbf\xa1\xe8\xb4\xa2\xe5\xaf\x8c\xe8\xb5\x84\xe4\xba\xa7\xe5\xad\x98\xe5\x9c\xa8shiro-CVE-2020-1234\xe6\xbc\x8f\xe6\xb4\x9e","responser":"jianwang163@creditease.cn|binxu37@creditease.cn","framework_name":"shiro","framework_version":"1.2.3","app_path":"/opt/yrd_web/credit-parser/WEB-INF","business_group":"\xe6\x9c\xaa\xe5\x88\x86\xe7\xbb\x84\xe4\xb8\xbb\xe6\x9c\xba","risk":"\xe8\xbf\x9c\xe7\xa8\x8b\xe4\xbb\xa3\xe7\xa0\x81\xe6\x89\xa7\xe8\xa1\x8c\xe3\x80\x81\xe6\x9c\xaa\xe6\x8e\x88\xe6\x9d\x83\xe8\xae\xbf\xe9\x97\xae"},{"ip":"10.151.5.220","user_group":"shiro-CVE-2020-11989\xe6\xbc\x8f\xe6\xb4\x9e\xe9\x80\x9a\xe5\x91\x8a\xe7\xbb\x84","leader":"fangzhouli@creditease.cn|xiaojunzhang@creditease.cn","app":"\xe5\xae\x9c\xe4\xbf\xa1\xe8\xb4\xa2\xe5\xaf\x8c\xe8\xb5\x84\xe4\xba\xa7\xe5\xad\x98\xe5\x9c\xa8shiro-CVE-2020-1234\xe6\xbc\x8f\xe6\xb4\x9e","responser":"jianwang163@creditease.cn|binxu37@creditease.cn","framework_name":"shiro","framework_version":"1.4.0","app_path":"/opt/amhome/am/WEB-INF","business_group":"\xe6\x9c\xaa\xe5\x88\x86\xe7\xbb\x84\xe4\xb8\xbb\xe6\x9c\xba","risk":"\xe6\x9c\xaa\xe6\x8e\x88\xe6\x9d\x83\xe8\xae\xbf\xe9\x97\xae"},{"ip":"10.134.136.72","user_group":"shiro-CVE-2020-11989\xe6\xbc\x8f\xe6\xb4\x9e\xe9\x80\x9a\xe5\x91\x8a\xe7\xbb\x84","leader":"fangzhouli@creditease.cn|xiaojunzhang@creditease.cn","app":"\xe5\xae\x9c\xe4\xbf\xa1\xe8\xb4\xa2\xe5\xaf\x8c\xe8\xb5\x84\xe4\xba\xa7\xe5\xad\x98\xe5\x9c\xa8shiro-CVE-2020-1234\xe6\xbc\x8f\xe6\xb4\x9e","responser":"jianwang163@creditease.cn|binxu37@creditease.cn","framework_name":"shiro","framework_version":"1.5.3","app_path":"/data/yx_soft/activemq/lib/optional","business_group":"\xe6\x9c\xaa\xe5\x88\x86\xe7\xbb\x84\xe4\xb8\xbb\xe6\x9c\xba","risk":"\xe6\x9c\xaa\xe6\x8e\x88\xe6\x9d\x83\xe8\xae\xbf\xe9\x97\xae"},{"ip":"10.134.90.15","user_group":"shiro-CVE-2020-11989\xe6\xbc\x8f\xe6\xb4\x9e\xe9\x80\x9a\xe5\x91\x8a\xe7\xbb\x84","leader":"fangzhouli@creditease.cn|xiaojunzhang@creditease.cn","app":"\xe5\xae\x9c\xe4\xbf\xa1\xe8\xb4\xa2\xe5\xaf\x8c\xe8\xb5\x84\xe4\xba\xa7\xe5\xad\x98\xe5\x9c\xa8shiro-CVE-2020-1234\xe6\xbc\x8f\xe6\xb4\x9e","responser":"jianwang163@creditease.cn|binxu37@creditease.cn","framework_name":"shiro","framework_version":"1.5.3","app_path":"/data/yx_soft/activemq/lib/optional","business_group":"\xe6\x9c\xaa\xe5\x88\x86\xe7\xbb\x84\xe4\xb8\xbb\xe6\x9c\xba","risk":"\xe6\x9c\xaa\xe6\x8e\x88\xe6\x9d\x83\xe8\xae\xbf\xe9\x97\xae"},{"ip":"10.140.129.13","user_group":"shiro-CVE-2020-11989\xe6\xbc\x8f\xe6\xb4\x9e\xe9\x80\x9a\xe5\x91\x8a\xe7\xbb\x84","leader":"jianwang163@creditease.cn|binxu37@creditease.cn","app":"\xe5\xae\x9c\xe4\xba\xba\xe8\xb4\xa2\xe5\xaf\x8c\xe8\xb5\x84\xe4\xba\xa7\xe5\xad\x98\xe5\x9c\xa8shiro-CVE-2020-1234\xe6\xbc\x8f\xe6\xb4\x9e","responser":"fangzhouli@creditease.cn|xiaojunzhang@creditease.cn","framework_name":"shiro","framework_version":"1.2.3","app_path":"/home/multimedia/report-tomcat-replace/webapps/AnBangReport/WEB-INF","business_group":"\xe6\x9c\xaa\xe5\x88\x86\xe7\xbb\x84\xe4\xb8\xbb\xe6\x9c\xba","risk":"\xe8\xbf\x9c\xe7\xa8\x8b\xe4\xbb\xa3\xe7\xa0\x81\xe6\x89\xa7\xe8\xa1\x8c\xe3\x80\x81\xe6\x9c\xaa\xe6\x8e\x88\xe6\x9d\x83\xe8\xae\xbf\xe9\x97\xae"}]'

        data = json.loads(data.decode())

        vuls = {}
        for item in data:
            vul_name = item.get('app')
            asset = {'ip': item.get('ip'), 'framework_name': item.get('framework_name'), 'framework_version': item.get('framework_version'), \
                    'app_path': item.get('app_path'), 'business_group': item.get('business_group'), 'risk': item.get('risk')}

            if not vuls.get(vul_name):
                vuls[vul_name] = dict(vul_name = vul_name, group_name = vul_name, appname = vul_name, \
                        parent_group = item.get('user_group'), assets = [asset], \
                        users = item.get('responser', '').split('|') + item.get('leader').split('|'))
            else:
                vuls[vul_name]['assets'].append(asset)

        for k, vul in vuls.items():
            users = [item for item in vul.get('users') if item]
            owner_email = users[-1]
            users = list(set(users))

            user_ids = []
            for email in users:
                username = email.split("@")[0]
                from action.user import get_default_role
                user = User.get_or_none(User.username == username)
                if not user:
                    user = User(username = username, email = email, role_id = get_default_role())
                    user.save()
                elif not user.email:
                    User.update(email = email).where(User.username == username).execute()
                user_ids.append(user.id)

            owner_username = owner_email.split("@")[0]
            owner = User.get_or_none(User.username == owner_username)

            parent_group = Group.get_or_none(Group.name == vul.get('parent_group'), Group.parent == 0)
            if not parent_group:
                parent_group = Group(name = vul.get('parent_group'), owner = owner.id, desc = vul.get('parent_group'))
                parent_group.save()
            parent_group_id = parent_group.id

            assets = vul.get('assets')
            group_name = vul.get('group_name')
            appname = vul.get('appname')
            vul_name = vul.get('vul_name')

            group = Group.get_or_none(Group.name == group_name, Group.parent == parent_group_id)
            if not group:
                group = Group(name = group_name, owner = owner.id, parent = parent_group_id, desc = group_name)
                group.save()

            role = Role.get_or_none(Role.type == 1)
            for user_id in user_ids:
                gu = GroupUser.get_or_none(GroupUser.group_id == group.id, GroupUser.user_id == user_id)
                if not gu:
                    GroupUser(group_id = group.id, user_id = user_id, role_id = role.id).save()

                gu = GroupUser.get_or_none(GroupUser.group_id == parent_group_id, GroupUser.user_id == user_id)
                if not gu:
                    GroupUser(group_id = parent_group_id, user_id = user_id, role_id = role.id).save()

            app = App.get_or_none(App.appname == appname)
            if not app:
                app = App(appname = appname, group_id =  group.id, level = 10, sec_level = 10, apptype = 20, sec_owner = owner.id)
                app.save()

            vul_poc = """
一、漏洞概述
2020年08月18日， Apache Shiro发布了权限绕过 的风险通告，漏洞编号为 CVE-2020-13933，漏洞等级高危。 Apahce Shiro由于处理身份验证请求时出错存在权限绕过漏洞，远程攻击者可以发送特制的HTTP请求，绕过身份验证过程并获得对应用程序的未授权访问。
参考链接：https://www.anquanke.com/post/id/214577

二、影响版本
Apache Shiro < 1.6.0

三、修复建议
建议使用Apache Shiro 的业务及时升级到最新版本Apache Shiro >= 1.6.0。
下载地址：http://shiro.apache.org/download.html

四、受威胁业务
目前青藤云监控检测到我司受影响IP列表如下。请各位owner及时回复修复进度，安装路径可联系安全部查询。未安装青藤监控的主机请业务及时自查，或联系安全部添加。
无主IP安全部将进行统一处理，尽可能确保业务连续性。


|  主机IP   | 框架名称  |  框架版本  |  应用路径  |  业务组  |  风险  |
|  ----  | ----  | ----  | ----  | ----  | ----  |
            """
            for asset in assets:
                xasset = Asset.get_or_none(Asset.value == asset.get('ip'))
                if not xasset:
                    Asset(name = asset.get('ip'), value = asset.get('ip'), app_id = app.id, type = 20).save()

                asset = {'ip': asset.get('ip'), 'framework_name': asset.get('framework_name'), 'framework_version': asset.get('framework_version'), \
                        'app_path': asset.get('app_path'), 'business_group': asset.get('business_group'), 'risk': asset.get('risk')}
                asset_info = "| {}  | {} | {} | {} | {} | {} |\r\n".format(asset['ip'], asset['framework_name'], asset['framework_version'], asset['app_path'], asset['business_group'], asset['risk'])
                vul_poc += asset_info

            vul = Vul(vul_name = vul_name, vul_type = 75, vul_level = 30, app_id = app.id, user_id = owner.id, vul_poc = vul_poc, self_rank = 7)
            vul.save()

        self.write(dict(status = True, msg = "导入成功"))
