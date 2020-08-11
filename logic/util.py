#!encoding=utf-8
import sys
import croniter
from datetime import datetime
from hashlib import md5
from uuid import uuid1
from random import randint
from captcha.image import ImageCaptcha

def password_md5(o):
    return md5('{}.{}'.format(md5(md5(o.encode()).hexdigest().encode()).hexdigest(),
                                __conf__.COOKIE_SECRET).encode()).hexdigest()

def conv_object(d):
    from datetime import datetime
    if isinstance(d, (datetime,)):
        return str(d)
    if isinstance(d, (bytes,)):
        if sys.version_info.major == 3:
            return d.decode()
        else:
            return d
    elif isinstance(d, (list, tuple)):
        return [conv_object(x) for x in d]
    elif isinstance(d, dict):
        return dict([(conv_object(k), conv_object(v)) for k, v in d.items()])
    else:
        return d

def gen_code():
    CODE = "abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    code, out = "", ""

    for i in range(4):
        code += CODE[randint(0, len(CODE) - 1)]

    out = "/tmp/{}.png".format(str(uuid1()))

    #image = ImageCaptcha(width=100, height=30, font_sizes = (40, 46, 50))
    image = ImageCaptcha()
    data = image.generate(code)

    image.write(code, out)
    return code, out

def get_crontab(sched):
    sched = sched.split(" ")[1:]
    sched.pop(-2)
    sched = " ".join(sched)
    sched = sched.replace("?", "*")
    sched = sched.replace("0/", "*/")
    return sched


def get_risk_score_and_end_date(rank, app):
    # 设置业务等级系数
    asset_level_value = 0
    if app.get('level') == 10:
        asset_level_value = 1
    elif app.get('level') == 20:
        asset_level_value = 0.9
    elif app.get('level') == 30:
        asset_level_value = 0.8
    else:
        asset_level_value = 0.7

    # 设置内外网系数
    asset_inout_value = 0
    if app.get("is_in") == 0:
        asset_inout_value = 1
    elif app.get("is_in") == 1:
        asset_inout_value = 0.8
    else:
        asset_inout_value = 0

    # 风险值＝rank * 业务等级系数 ＊ 风险值权重 ＊ 内外网系数
    risk_score = round(rank * asset_level_value * 5 * asset_inout_value, 2)

    if app.get("level") == 10:
        if 15 < rank <= 20:
            days = 1
        elif 10 < rank <= 15:
            days = 1
        elif 5 < rank <= 10:
            days = 7
        elif 0 < rank <= 5:
            days = 60
        else:
            days = 0
    elif app.get("level") == 20:
        if 15 < rank <= 20:
            days = 1
        elif 10 < rank <= 15:
            days = 1
        elif 5 < rank <= 10:
            days = 7
        elif 0 < rank <= 5:
            days = 60
        else:
            days = 0
    elif app.get("level") == 30:
        if 15 < rank <= 20:
            days = 7
        elif 10 < rank <= 15:
            days = 7
        elif 5 < rank <= 10:
            days = 60
        elif 0 < rank <= 5:
            days = 60
        else:
            days = 0
    else:
        if 15 < rank <= 20:
            days = 7
        elif 10 < rank <= 15:
            days = 7
        elif 5 < rank <= 10:
            days = 60
        elif 0 < rank <= 5:
            days = 60
        else:
            days = 0

    # 如果系统为上线前测试，将修复天数延长至1年
    if app.get("status") == 20 and days != 0:
        days = 365

    return risk_score, days

def get_next_time(sched, now):
    x = sched
    cron = croniter.croniter(sched, now)
    ret = cron.get_next(datetime)
    return ret


