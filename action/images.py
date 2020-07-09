#!coding=utf-8
import time
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import LoginedRequestHandler


@url(r"/image/upload", needcheck = False, category = "图片")
class ImageAdd(LoginedRequestHandler):
    """
        图片上传

        images: 文件
    """
    def post(self):
        img = self.request.files['image'][0]
        filename = img.get('filename')

        if filename.split(".")[-1].lower() not in ["jpg", "png", "jpeg"]:
            self.write(dict(status = False, msg = "图片格式错误"))
            return

        body = img.get('body')
        body_md5 = md5(body).hexdigest()

        new_filename = "{}.{}".format(body_md5, filename.split(".")[-1])
        path = "{}/images/{}".format(__conf__.STATIC_DIR_NAME, new_filename)

        with open(path, "wb") as f:
            f.write(body)

        self.write(dict(status = True, path = "{}/images/{}".format(__conf__.STATIC_DIR_NAME, new_filename)))

@url(r"/paper/cover", needcheck = False, category = "图片")
class ImageArticleCover(LoginedRequestHandler):
    """
        文章封面上传

        images: 文件
    """
    def post(self):
        img = self.request.files['file'][0]
        filename = img.get('filename')

        if filename.split(".")[-1].lower() not in ["jpg", "png", "jpeg"]:
            self.write(dict(status = False, msg = "图片格式错误"))
            return

        body = img.get('body')
        body_md5 = md5(body).hexdigest()

        new_filename = "{}.{}".format(body_md5, filename.split(".")[-1])
        path = "{}/images/{}".format(__conf__.STATIC_DIR_NAME, new_filename)

        with open(path, "wb") as f:
            f.write(body)

        self.write(dict(status = True, path = "{}/images/{}".format(__conf__.STATIC_DIR_NAME, new_filename)))

@url(r"/avatar/upload", needcheck = False, category = "图片")
class ImageAvatarUpload(LoginedRequestHandler):
    """
        头像上传

        file: 文件
    """
    def post(self):
        img = self.request.files['file'][0]
        filename = img.get('filename')

        if filename.split(".")[-1].lower() not in ["jpg", "png", "jpeg"]:
            self.write(dict(status = False, msg = "图片格式错误"))
            return

        body = img.get('body')
        body_md5 = md5(body).hexdigest()

        new_filename = "{}.{}".format(body_md5, filename.split(".")[-1])
        path = "{}/images/avatar/{}".format(__conf__.STATIC_DIR_NAME, new_filename)

        with open(path, "wb") as f:
            f.write(body)

        self.write(dict(status = True, path = "{}/images/avatar/{}".format(__conf__.STATIC_DIR_NAME, new_filename)))



