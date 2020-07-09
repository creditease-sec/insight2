# -*- coding:utf-8 -*-

from inspect import isclass
import tornado
from tornado.web import RequestHandler, ErrorHandler

class BaseHandler(RequestHandler):
    """
        Torando RequestHandler
        http://www.tornadoweb.org/

    """
    __UID__ = "__UID__"
    __USERNAME__ = "__USERNAME__"


    def get(self, *args, **kwargs):
        self.send_error(404)

    def post(self, *args, **kwargs):
        self.send_error(404)

    def get_current_user(self):
        return self.get_secure_cookie(self.__USERNAME__)


ErrorHandler.__bases__ = (BaseHandler,)

ACL = dict()
CATEGORY = ""

class ACLNode(object):
    def __init__(self, handler):
        self.name = '{0}.{1}'.format(handler.__module__, handler.__name__)
        self.intro = handler.__doc__ or self.name
        self.handler = handler

"""
def needcheck(**kwargs):
    def actual(handler):
        assert(issubclass(handler, tornado.web.RequestHandler))
        #handler.__needcheck__ = kwargs

        #category = kwargs.get('category',CATEGORY)
        #if not ACL.get(category,None):ACL[category] = {}
        #aclnode = ACLNode(handler)
        #ACL[category][aclnode.name] = aclnode
        #handler.__checkname__ = aclnode.name

        return handler

    return actual
"""



def url(pattern, order = 0, needcheck=True, category="Default"):
    def actual(handler):
        if not isclass(handler) or not issubclass(handler, RequestHandler):
            raise Exception("must be RequestHandler's sub class.")

        if not hasattr(handler, "__urls__"): handler.__urls__ = []
        handler.__urls__.append((pattern, order, needcheck, category))

        if needcheck:
            if not ACL.get(category):ACL[category] = {}
            aclnode = ACLNode(handler)
            ACL[category][aclnode.name] = aclnode

        return handler

    return actual


__all__ = ["BaseHandler", "url", "ACL"]
