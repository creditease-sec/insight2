#!encoding=utf-8
import os
import json
import time
import uuid
from datetime import datetime
from hashlib import md5

from peewee import *
from playhouse.shortcuts import model_to_dict

from logic.objectid import ObjectId
from logic.util import *

db = MySQLDatabase(__conf__.DB_NAME,
                    host = __conf__.DB_HOST,
                    port = __conf__.DB_PORT,
                    user = __conf__.DB_USER,
                    password = __conf__.DB_PASS)

id_func = lambda :str(ObjectId())

class LongTextField(TextField):
    field_type = 'LONGTEXT'


class BaseModel(Model):
    class Meta:
        database = db


class Role(BaseModel):
    id = AutoField()
    _id = CharField(default = id_func)
    name = CharField()
    level = IntegerField(default = 0)
    accesses = TextField(null = True)
    desc = CharField(default = "")
    type = IntegerField(default = 0)
    default = IntegerField(default = 0)

class User(BaseModel):
    id = AutoField()
    _id = CharField(default = id_func)
    username = CharField(unique = True)
    nickname = CharField(default = "")
    avatar = CharField(default = "")
    token = CharField(default = "")
    token_enable = IntegerField(default = 1)
    is_del = IntegerField(default = 0)
    email = CharField(default = "")
    password = CharField(default = "")
    enable = IntegerField(default = 1)
    ldap_online = IntegerField(default = 0)
    ldap_offline_time = DoubleField(default = 0)
    auth_from = CharField(default = "LOCAL")
    role = ForeignKeyField(Role)
    create_time = DoubleField(default = time.time)
    update_time = DoubleField(default = time.time)
    active_time = DoubleField(default = time.time)
    login_time = DoubleField(default = 0)
    total_points = IntegerField(default = 0)
    frozen_points = IntegerField(default = 0)
    available_points = IntegerField(default = 0)

class Group(BaseModel):
    id = AutoField()
    _id = CharField(default = id_func)
    name = CharField()
    desc = CharField()
    owner = ForeignKeyField(User)
    parent = IntegerField(default = 0)
    create_time = DoubleField(default = time.time)
    update_time = DoubleField(default = time.time)

class GroupUser(BaseModel):
    _id = CharField(default = id_func)
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    role = ForeignKeyField(Role)
    create_time = DoubleField(default = time.time)

class AuthMode(BaseModel):
    _id = CharField(default = id_func)
    name = CharField()
    mode = CharField(default = "")
    desc = CharField(default = "")
    config = TextField(default = "")
    enable = IntegerField(default = 1)
    create_time = DoubleField(default = time.time)
    update_time = DoubleField(default = time.time)

class SystemSettings(BaseModel):
    _id = CharField(default = id_func)
    smtp_host = CharField(null = True)
    smtp_port = CharField(null = True)
    smtp_user = CharField(null = True)
    smtp_pass = CharField(null = True)
    smtp_head = CharField(null = True)
    smtp_sign = CharField(null = True)
    smtp_auth_type= CharField(null = True)
    mail_list = CharField(null = True)
    vul_setting = CharField(null = True)
    global_setting = CharField(null = True)
    point_setting = CharField(null = True)
    site_status = CharField(null = True)
    version = CharField(null = True)

class App(BaseModel):
    _id = CharField(default = id_func)
    appname = CharField(default = "")
    apptype = IntegerField(default = 0)
    level = IntegerField(default = 0)
    sec_level = IntegerField(default = 0)
    group = ForeignKeyField(Group)
    status = IntegerField(default = 0)
    comment = CharField(default = "")
    check_time = DoubleField(default = time.time)
    offonline_time = DoubleField(default = time.time)
    create_time = DoubleField(default = time.time)
    update_time = DoubleField(default = time.time)
    sec_owner = IntegerField(default = 0)
    sensitive_data_count = IntegerField(default = 0)
    sensitive_data = TextField(default = "")
    secure_level = IntegerField(default = 0)
    business_cata = TextField(null = True)
    downtime = IntegerField(default = 0)
    is_open = IntegerField(default = 0)
    is_interface = IntegerField(default = 0)
    is_https = IntegerField(default = 0)
    eid = CharField(default = "")
    crontab = CharField(default = "")
    op_user_id = CharField(default = "")


class Asset(BaseModel):
    _id = CharField(default = id_func)
    app_id = IntegerField(default = 0)
    name = CharField(default = "")
    value = CharField(default = "")
    type = CharField(default = "")
    is_open = IntegerField(default = 0)
    is_https = IntegerField(default = 0)
    apptype = CharField(default = "")
    status = IntegerField(default = 0)
    create_time = DoubleField(default = time.time)
    update_time = DoubleField(default = time.time)


class Vul(BaseModel):
    _id = CharField(default = id_func)
    vul_name          =    CharField(null = True)
    vul_type          =    IntegerField(default = 0)
    vul_level         =    IntegerField(default = 0)
    self_rank         =    CharField(null = True)
    vul_desc_type     =    IntegerField(default = 0)
    vul_poc           =    LongTextField(null = True)
    vul_poc_html      =    LongTextField(null = True)
    vul_solution      =    LongTextField(null = True)
    vul_solution_html =    LongTextField(null = True)
    article_id        =    CharField(null = True)
    audit_user_id     =    IntegerField(default = 0) #未用
    reply             =    TextField(null = True)
    user_id           =    IntegerField(default = 0)
    submit_time       =    DoubleField(default = time.time)
    audit_time        =    DoubleField(default =0)
    notice_time       =    DoubleField(default =0)
    update_time       =    DoubleField(default =0)
    fix_time          =    DoubleField(default =0)
    vul_status        =    IntegerField(default = 0)
    asset_level       =    IntegerField(default = 0)
    real_rank         =    IntegerField(default = 0)
    score             =    IntegerField(default = 0)
    risk_score        =    IntegerField(default = 0)
    left_risk_score   =    IntegerField(default = 0)
    app_id            =    IntegerField(default = 0)
    vul_source        =    IntegerField(default = 0)
    send_msg          =    IntegerField(default = 0)
    is_retest         =    IntegerField(default = 0)
    layer             =    IntegerField(default = 0)
    delay_days = IntegerField(default = 0)
    delay_reason = TextField(null = True)

class VulLog(BaseModel):
    _id = CharField(default = id_func)
    vul_id = IntegerField(default=0)
    title = TextField(default = "")
    user_id = IntegerField(default = 0)
    username = CharField(default = "")
    action = TextField(default = "")
    content = TextField(default = "")
    create_time = DoubleField(default = time.time)

class Message(BaseModel):
    _id = CharField(default = id_func)
    message_id = CharField(default = id_func)
    message_type = CharField(default = "")
    title = TextField(default = "")
    content = TextField(default = "")
    to = ForeignKeyField(User)
    status = IntegerField(default = 0)
    create_time = DoubleField(default = time.time)

class MessagePoint(BaseModel):
    _id = CharField(default = id_func)
    message_id = CharField(default = id_func)
    from_uid = IntegerField(default = 0)
    to_uid = IntegerField(default = 0)
    title = TextField(default = "")
    content = TextField(default = "")
    total_points = CharField(default = "")
    frozen_points = CharField(default = "")
    available_points = CharField(default = "")
    create_time = DoubleField(default = time.time)

class Category(BaseModel):
    _id = CharField(default = id_func)
    name = CharField(default = "")
    create_time = DoubleField(default = time.time)

class Extension(BaseModel):
    _id = CharField(default = id_func)
    eid = CharField(default = "")
    name = CharField(default = "")
    path = CharField(default = "")
    type = IntegerField(default = 0)
    version = CharField(default = "")
    remark = CharField(default = "")
    desc = CharField(default = "")
    status = IntegerField(default = 1)
    config_template = TextField(default = "")
    config = TextField(default = "")
    create_time = DoubleField(default = time.time)

class CronTab(BaseModel):
    _id = CharField(default = id_func)
    name = TextField(default = "")
    uid = IntegerField(default = 0)
    eid = CharField(default = "")
    crontab = CharField(default = "")
    relate = CharField(default = "SYSTEM")# 关联的类型 SYSTEM, APP, ASSET, VUL 等
    relate_id = CharField(default = "")# 关联的id
    enable = IntegerField(default = 1) # 0, 1
    remark = TextField(default = "")
    exec_count = IntegerField(default = 0)
    status = IntegerField(default = 0) # 0, 1, 2
    log = LongTextField(null = True)
    config = TextField(default = "")
    create_time = DoubleField(default = time.time)
    update_time = DoubleField(default = time.time)
    last_time = DoubleField(default = 0)
    next_time = DoubleField(default = 0)

class CronTabLog(BaseModel):
    _id = CharField(default = id_func)
    eid = CharField(default = "")
    content = LongTextField(null = True)
    start_time = DoubleField(default = 0)
    end_time = DoubleField(default = 0)
    create_time = DoubleField(default = time.time)

class ExtensionLog(BaseModel):
    _id = CharField(default = id_func)
    eid = CharField(default = "")
    app_id = IntegerField(default = 0)
    is_auto = IntegerField(default = 0) # 0:自动, 1:手动
    op_user_id = CharField(default = "")
    name = CharField(default = "")
    path = CharField(default = "")
    title = CharField(default = "")
    content = TextField(default = "")
    status = IntegerField(default = 0)
    create_time = DoubleField(default = time.time)

class Article(BaseModel):
    _id = CharField(default = id_func)
    #article_id = CharField(default = id_func)
    title = CharField(default = "")
    alias = CharField(default = "")
    category = IntegerField(default = 0)
    author = CharField(default = "")
    publish_time = DoubleField(default = time.time)
    publish_datetime = DateTimeField(default=datetime.now)
    modify_time = DoubleField(default = time.time)
    status = IntegerField(default = 1)
    cover = LongTextField(null = True)
    summary = TextField(default = "")
    content_type = IntegerField(default = 0) #0副文本 1Markdown
    raw_content = LongTextField(default = "")
    md_raw_content = LongTextField(default = "")
    content = LongTextField(default = "")

def init_db():
    db.drop_tables([GroupUser, User, Role, Group, Vul, AuthMode, SystemSettings, Asset, App, VulLog, Message, MessagePoint, Article, Category, Extension, ExtensionLog, CronTab, CronTabLog])
    db.create_tables([Role, User, Group, GroupUser, Vul, AuthMode, SystemSettings, Asset, App, VulLog, Message, MessagePoint, Article, Category, Extension, ExtensionLog, CronTab, CronTabLog])

    CronTab(name = "测试", uid = 1, eid = "scan", crontab = "*/1 * * * *", relate = "SYSTEM", enable = 1, remark = "测试").save()

    Role(name = "超级管理员", level = 0, accesses = "").save()
    Role(name = "普通用户", level = 5, accesses = "").save()
    Role(name = "安全人员", level = 8, accesses = "", type = 1).save()

    User(username = "admin", password = password_md5("admin!Aa2020"), role_id = 1).save()

    Group(name = "安全部", owner = 1, desc = "安全部 ...").save()
    GroupUser(group_id = 1, user_id = 1, role_id = 3).save()

    global_setting = {"group_member_limit": "10", "isSendEmail": "1", "isCreateGroup": "1"}
    email_setting = {"smtp_host": "", "smtp_port": "", "smtp_user": "", "smtp_pass": "", "smtp_head": "", "smtp_sign": "", "mail_list": ""}
    point_setting = {"ti_level_point": 1, "times_level_point": 1, "one_level_point": 1, "two_level_point": 1, "three_level_point": 1, "other_level_point": 1}
    SystemSettings(global_setting = json.dumps(global_setting), point_setting = json.dumps(point_setting), **email_setting).save()

    from logic.utility import access_list
    accesses = []
    for item in access_list():
        accesses.extend([_.get('id') for _ in item.get('children')])

    accesses = ",".join(accesses)
    Role.update(accesses = accesses).where(Role.id == 1).execute()

def version_upgrade():
    import pymysql
    from logic.upgrade import VERSIONS
    conn = pymysql.connect(host = __conf__.DB_HOST, port = __conf__.DB_PORT, user = __conf__.DB_USER, passwd = __conf__.DB_PASS, database = __conf__.DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("alter table systemsettings add column version varchar(255) default '';")
    except:
        pass


    version = SystemSettings.get_or_none().version
    for v in sorted(VERSIONS.keys()):
        if v > version:
            for sql in VERSIONS.get(v):
                cur.execute(sql)

            SystemSettings.update(version = v).execute()

    cur.close()
    conn.close()

def init_crontab():
    cs = CronTab.select().where(CronTab.enable == 1)
    path = os.path.dirname(os.path.dirname(__file__))

    crontab = """
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root

# For details see man 4 crontabs

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name  command to be executed
"""
    for item in cs:
        crontab += "\n{} root cd {};python run.py --crontab_id={} --config=dev_settings.py".format(item.crontab, path, item._id)

    crontab += "\n1 10 * * * root cd {};python run_check_vul.py".format(path)
    crontab += "\n1 6 * * * root cd {};python run.py --ex=ldap".format(path)

    os.system('echo "{}" > /etc/crontab'.format(crontab))


def gen_data():
    # 生成示例数据
    from logic.example_data import CATEGORY, PAPER, ASSET, APP, VULS

    for item in CATEGORY:
        Category(**item).save()

    for item in PAPER[:5]:
        Article(**item).save()

    for item in ASSET:
        Asset(**item).save()

    for item in APP:
        App(**item).save()

    for item in VULS:
        Vul(**item).save()


def init_data():
    from transfer_data import transfer
    transfer.transfer_category()
    transfer.transfer_user()
    transfer.transfer_asset()
    transfer.transfer_vul()
    transfer.transfer_article()
    transfer.transfer_score()
    transfer.transfer_departs()
    transfer.transfer_app_group()

