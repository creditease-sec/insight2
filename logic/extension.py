#!coding=utf-8
import sys
import json
from logic.model import *
sys.path.append("upload/extensions")

def run(ex, app_id = 0, is_auto = 0, content = ""):
    extension = Extension.get_or_none(Extension.eid == ex)

    if not extension:
        return

    #ex_path = "upload.extensions.{}.main".format(extension.path)

    ex_path = "{}.main".format(extension.path)
    module = __import__(ex_path, fromlist = ["main"])
    eid = extension.eid
    config = json.loads(extension.config or "{}")

    log_doc = {}
    if extension:
        log_doc['name'] = extension.name
        log_doc['path'] = extension.path
        log_doc['title'] = extension.name
        log_doc['content'] = extension.config + " " + content

    if app_id:
        app = App.get_or_none(App.id == app_id)
        if app:
            log_doc['op_user_id'] = app.op_user_id
            log_doc['op_user_id'] = 1

    ExtensionLog(eid = ex, app_id = app_id, is_auto = is_auto, **log_doc).save()


    """
    App app_id 对应的资产进行 扩展调用
    """
    if app_id:
        assets = Asset.select().where(Asset.app_id == app_id)
        targets = [item.value for item in assets]
    else:
        targets = []
    module.main(targets, **config)




