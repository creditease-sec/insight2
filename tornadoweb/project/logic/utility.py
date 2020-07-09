#-*- coding:utf-8 -*-
import time
import json

from tornadoweb import *

class LoginedRequestHandler(BaseHandler):
    uid = property(lambda self: (self.get_secure_cookie("__UID__") or '').decode())
    username = property(lambda self: (self.get_secure_cookie("__USERNAME__") or '').decode())

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    def options(self, *args, **kwargs):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')


    def prepare(self):
        """
            REQUEST BEFORE HOOK
        """
        if not self.uid:
            self.send_error(403)

        # TODO ADD SELF ACCESS 


    def on_finish(self):
        """
            REQUEST FINISH HOOK
        """
        pass

