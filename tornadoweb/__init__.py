from .web import *
from .app import *
from .config import *
from .utility import *

set_default_encoding()

import os
import traceback
import tornado
from tornado.web import RequestHandler
from tornado.httpclient import HTTPError
from inspect import getmembers

#CATEGORY = "Default"
#ACL = dict()
#
##class ACLNode(object):
#    def __init__(self, handler):
#        self.name = '{0}.{1}'.format(handler.__module__, handler.__name__)
#        self.intro = handler.__doc__ or self.name
#        self.handler = handler
#
#
#def needcheck(**kwargs):
#    def actual(handler):
#        assert(issubclass(handler, tornado.web.RequestHandler))
#        handler.__needcheck__ = kwargs
#
#        category = kwargs.get('category',CATEGORY)
#        if not ACL.get(category,None):ACL[category] = {}
#        aclnode = ACLNode(handler)
#        ACL[category][aclnode.name] = aclnode
#        handler.__checkname__ = aclnode.name
#
#        return handler
#
#    return actual
#
