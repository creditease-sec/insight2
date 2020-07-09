#!coding=utf-8
from hashlib import md5

from tornadoweb import *
from logic.utility import LoginedRequestHandler

def password_md5(o):
    return md5('{}.{}'.format(md5(md5(o.encode()).hexdigest().encode()).hexdigest(),
                                __conf__.COOKIE_SECRET).encode()).hexdigest()

@url(r"/login")
class LoginHandler(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        password = password_md5(self.get_argument('password'))

        # TODO LOGIN LOGIC
        self.set_secure_cookie("__UID__", "admin")
        self.set_secure_cookie("__USERNAME__", "admin")
        self.write(dict(status = True, msg = "登陆成功"))


@url(r"/logout")
class LogoutHandler(LoginedRequestHandler):
    def get(self):
        self.clear_cookie("__UID__")
        self.clear_cookie("__USERNAME__")
        self.write(dict(status = True, msg = "登出成功"))

