#!coding=utf-8
import os
import sys
import json
import time
from tornadoweb import *
from logic.model import *
from logic.util import *

sys.path.append("{}/extensions".format(__conf__.STATIC_DIR_NAME))

def run(crontab_id):
    def my_print(s):
        CronTab.update(log = CronTab.log + s + "\r\n").where(CronTab._id == crontab_id).execute()

    crontab = CronTab.get_or_none(CronTab._id == crontab_id, CronTab.enable == 1)
    if not crontab:
        return False, ""

    if crontab.status == 1:
        # 运行中的任务
        my_print("已经存在执行中的定时任务")
        return False, "任务正在执行中"

    # 执行中...
    CronTab.update(status = 1, log = "", last_time = time.time()).where(CronTab._id == crontab_id).execute()

    # 记录定时任务执行结果
    crontablog = CronTabLog(crontab_id = crontab_id, content = "", start_time = time.time())
    crontablog.save()
    crontablog_id = crontablog.id
    # CronTabLog

    my_print("任务开始执行\r\n--------")
    try:
        eid = crontab.eid
        relate = crontab.relate
        relate_id = crontab.relate_id

        extension = Extension.get_or_none(Extension.eid == eid)

        ex_path = "{}.main".format(extension.path)
        config = json.loads(extension.config or "{}")
        module = __import__(ex_path, fromlist = ["main"])
        module.__builtins__["println"] = my_print

        target = {}
        result = module.main(target, **config)
        if not isinstance(result, dict):
            my_print("\r\n[ERROR] 自定义扩展请返回dict类型\r\n")
        else:
            my_print(json.dumps(conv_object(result)))
            CronTabLog.update(content = json.dumps(conv_object(result))).where(CronTabLog.id == crontablog_id).execute()

    except:
        import traceback
        my_print(traceback.format_exc())

    # 执行完成
    CronTab.update(status = 2, exec_count = CronTab.exec_count + 1).where(CronTab._id == crontab_id).execute()
    CronTabLog.update(end_time = time.time()).where(CronTabLog.id == crontablog_id).execute()
    my_print("--------\r\n\r\n任务执行完成")

    next_time = get_next_time(crontab.crontab, datetime.now())
    CronTab.update(next_time = next_time.timestamp()).where(CronTab._id == crontab_id).execute()
    return True, "任务执行完成"

