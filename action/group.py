#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.groupuser import group_user
from logic.utility import LoginedRequestHandler


@url(r"/group/add", category = "用户组")
class GroupUpsert(LoginedRequestHandler):
    """
        用户组设置

        _id: 用户组id
        name: 用户组名称*
        parent: 父组id
        desc: 描述
    """
    def post(self):
        settings = SystemSettings.get_or_none()
        global_setting = json.loads(settings.global_setting)
        if global_setting.get("isCreateGroup") != "1":
            self.write(dict(status = False, msg = '不允许新建用户组'))
            return


        _id = self.get_argument('id', '')
        name = self.get_argument('name')
        desc = self.get_argument('desc', '')
        parent = self.get_argument('parent', '')

        if _id:
            Group.update(name = name, desc = desc, update_time = time.time()). \
                            where(Group._id == _id). \
                            execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            parent_id = 0
            if parent:
                parent_id = Group.get_or_none(Group._id == parent).id
            Group(name = name, desc = desc, owner = User(id = self.uid), parent = parent_id).save()
            self.write(dict(status = True, msg = '添加成功'))

@url(r"/group/del", category = "用户组")
class GroupDel(LoginedRequestHandler):
    """
        用户组删除

        _id: 用户组id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        group = Group.select().where(Group._id.in_(_id))
        group_id = [item.id for item in group]

        # 删除子组
        Group.delete().where(Group.parent.in_(group_id)).execute()

        # 删除本身
        Group.delete().where(Group._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/group/owner/set", category = "用户组")
class GroupOwnerSet(LoginedRequestHandler):
    """
        管理者变更

        id: 用户组id
        owner_id: 管理者id
    """
    def post(self):
        _id = self.get_arguments('id')
        owner_id = self.get_argument("owner_id")

        user_id = User.get_or_none(User._id == owner_id).id
        Group.update(owner_id = user_id).where(Group._id == _id).execute()

        self.write(dict(status = True, msg = '变更成功'))

@url(r"/group/list", category = "用户组")
class GroupList(LoginedRequestHandler):
    """
        用户组查询

        search: 查询条件
        page_index: 页码
        page_size: 每页条数
    """
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))
        group_id = self.get_argument('group_id', None)

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if search:
            cond = [Group.name.contains(search)]
            user = User.get_or_none(User.username == search)
            if user:
                gu = GroupUser.select().where(GroupUser.user_id == user.id)
                if gu:
                    group_ids = [item.group_id for item in gu]
                    cond = [(Group.name.contains(search))| (Group.id.in_(group_ids)) | (Group.owner_id == user.id)]

        if group_id:
            cond.append(Group._id == group_id)

        if not cond:
            cond.append(None)

        if sort:
            sort = getattr(Group, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()

        total = Group.select().where(*cond).count()

        group = Group.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        group = [model_to_dict(item) for item in group]
        for g in group:
            #g['groupuser'] = group_user(g.get('id'), findall = True)
            count = GroupUser.select().where(GroupUser.group_id == g['id']).count()
            #g['groupuser'] = [{} for item in range(count)]
            g['usercount'] = count
            g['owner'] = g['owner']['username']

        parent_group = dict((item.get('id'), item) for item in group if item.get('parent') == 0)
        child_group = [item for item in group if item.get('parent') != 0]

        no_parent_group = []
        for g in child_group:
            parent_id = g.get('parent')
            if parent_group.get(parent_id):
                if not parent_group[parent_id].get('children'):
                    parent_group[parent_id]['children'] = []

                g['id'] = g.pop('_id')
                g.pop('parent', None)
                g['parentname'] = parent_group[parent_id].get('name')
                parent_group[parent_id]['children'].append(g)
            else:
                no_parent_group.append(g)

        groups = list(parent_group.values()) + no_parent_group
        for g in groups:
            g['id'] = g.pop('_id')

        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = list(parent_group.values()) + no_parent_group))

