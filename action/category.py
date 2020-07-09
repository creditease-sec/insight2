#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler


@url(r"/category/add", category = "文章")
class CategoryUpsert(LoginedRequestHandler):
    """
        分类设置

        name: 分类
    """
    def post(self):
        name = self.get_argument("name", "")
        Category(name = name).save()
        self.write(dict(status = True, msg = '添加成功'))

@url(r"/category/del", category = "文章")
class CategoryDel(LoginedRequestHandler):
    """
        分类删除

        id: 分类id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        _id = [int(item) for item in _id]
        Category.delete().where(Category.id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))

@url(r"/category/list", needcheck = False, category = "文章")
class CategoryList(LoginedRequestHandler):
    """
        分类查询
    """
    def get(self):

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = (None, )

        if sort:
            sort = getattr(Category, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()

        category = Category.select()

        category = [model_to_dict(item) for item in category]
        for item in category:
            item["count"] = Article.select().where(Article.category == item.get('id')).count()

        self.write(dict(result = category))

