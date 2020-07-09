#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler


@url(r"/paper/upsert", category = "文章")
class ArticleUpsert(LoginedRequestHandler):
    """
        文章设置

        _id: 文章id
        title: 标题
        alias: 别名
        category: 分类
        author: 作者
        status: 状态[0, 1]
        cover: 封面
        summary: 摘要
        content_type: 编辑器类型
        raw_content: 原文内容
        md_raw_content: markdown 原文内容
        content: 内容
    """
    def post(self):
        _id = self.get_argument('id', '')
        content = self.get_argument('content', '')
        raw_content = self.get_argument('raw_content', '')

        from logic import pxfilter

        parser = pxfilter.XssHtml()
        parser.feed(content)
        parser.close()
        content = parser.getHtml()

        parser = pxfilter.XssHtml()
        parser.feed(raw_content)
        parser.close()
        raw_content = parser.getHtml()

        doc = dict(
            title = self.get_argument('title', ''),
            alias = self.get_argument('alias', ''),
            category = int(self.get_argument('category', 0)),
            author = self.get_argument('author', ''),
            status = int(self.get_argument('status', 1)),
            cover = self.get_argument('cover', ''),
            publish_time = float(self.get_argument('publish_time', time.time())),
            modify_time = time.time(),
            summary = self.get_argument('summary', ''),
            content_type = int(self.get_argument('content_type', 1)),
            md_raw_content = self.get_argument('md_raw_content', ''),
            raw_content = raw_content,
            content = content,
        )

        if _id:
            doc.pop("publish_time", None)
            Article.update(**doc). \
                            where(Article._id == _id). \
                            execute()

            self.write(dict(status = True, msg = '编辑成功'))
        else:
            Article(**doc).save()
            self.write(dict(status = True, msg = '添加成功'))

@url(r"/paper/del", category = "文章")
class ArticleDel(LoginedRequestHandler):
    """
        文章删除

        id: 文章id[]
    """
    def post(self):
        _id = self.get_arguments('id')
        Article.delete().where(Article._id.in_(_id)).execute()

        self.write(dict(status = True, msg = '删除成功'))


@url(r"/paper/get", needcheck = False, category = "文章")
class ArticleGet(LoginedRequestHandler):
    """
        单个文章查询

        id: 文章id
    """
    def get(self):
        _id = self.get_argument('id')

        article = Article.get_or_none(Article._id == _id)
        if article:
            article = model_to_dict(article)
            article['id'] = article.pop('_id')

            article.pop("publish_datetime")
            category = Category.get_or_none(Category.id == article.get('category'))
            article["category_name"] = ""
            if category:
                article["category_name"] = category.name
        else:
            article = {}

        self.write(article)


@url(r"/paper/list", needcheck = False, category = "文章")
@url(r"/paper/open", needcheck = False, category = "文章")
class ArticleList(LoginedRequestHandler):
    """
        文章查询

        search: 查询条件
        page_index: 页码
        page_size: 每页条数
    """
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        sort = self.get_argument('sort', None)
        # 方向 desc
        direction = self.get_argument('direction', '')

        cond = []
        if "/paper/open" in self.request.uri:
            cond.append(Article.status == 1)

        if search:
            cond.append((Article.title.contains(search) | Article.alias.contains(search) | Article.summary.contains(search)))

        if not cond:
            cond = [None]

        if not sort:
            sort = Article.publish_time.desc()
        else:
            sort = getattr(Article, sort)
            direction = direction.replace("ending", "")
            if direction == 'desc':
                sort = sort.desc()

        total = Article.select().where(*cond).count()

        article = Article.select().where(*cond). \
                        order_by(sort). \
                        paginate(page_index, page_size)

        article = [model_to_dict(item) for item in article]
        for item in article:
            item.pop("publish_datetime")
            category = Category.get_or_none(Category.id == item.get('category'))
            item["category_name"] = ""
            if category:
                item["category_name"] = category.name

            item['id'] = item.pop("_id")


        self.write(dict(page_index = page_index, \
                            total = total, \
                            result = article))

