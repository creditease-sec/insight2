#!encoding=utf-8
import pymysql
from logic.define import *
from logic.model import *

try:
    from_db = pymysql.connect(**__conf__.FROM_DB)
except:
    from_db = None

def transfer_user():
    print ("用户数据初始化...")
    cursor = from_db.cursor()
    cursor.execute("select email,username,password_hash,role_name,confirmed from login_users")
    data = cursor.fetchall()
    cursor.close()
    for d in data:
        email,username,password_hash,role_name,confirmed = d
        if role_name == "超级管理员":
            role_id = 1
        elif role_name == "普通用户":
            role_id = 2
        elif role_name == "安全人员":
            role_id = 3

        try:
            User(email = email, username = username, password = "", role_id = role_id).save()
        except:
            pass


def transfer_asset():
    print ("资产应用数据初始化...")
    cursor = from_db.cursor()
    cursor.execute("select id, sysname, domain, back_domain, web_or_int, is_http, is_https, in_or_out, level, department, owner, status, chkdate, ps, count_private_data, down_time, private_data, secure_level, business_cata, sec_owner, create_date, update_date from assets ")
    data = cursor.fetchall()
    cursor.close()

    now = str(datetime.now())[:10]

    for d in data:
        _id, sysname, domain, back_domain, web_or_int, is_http, is_https, in_or_out, level, department, owner, status, chkdate, ps, count_private_data, down_time, private_data, secure_level, business_cata, sec_owner, create_date, update_date = d
        sec_owner_id = 1
        if sec_owner:
            user = User.get_or_none((User.username == sec_owner) | (User.email == sec_owner))
            if user:
                sec_owner_id = user.id

        dict_sec_level = dict((v, k) for k, v in APP_SEC_LEVEL.items())
        dict_ASDC = dict((v, k) for k, v in APP_SENSITIVE_DATA_COUNT.items())
        dict_APP_DOWNTIME = dict((v, k) for k, v in APP_DOWNTIME.items())
        dict_ASSET_LEVEL = dict((v, k) for k, v in ASSET_LEVEL.items())
        dict_APP_STATUS = dict((v, k) for k, v in APP_STATUS.items())

        app = App (
            appname = sysname,
            apptype = 10,
            level = dict_ASSET_LEVEL.get(level) or "40",
            sec_level = dict_sec_level.get(secure_level) or "40",
            group_id = 1,
            status = dict_APP_STATUS.get(status) or "10",
            comment = "",
            check_time = time.mktime(time.strptime(str(chkdate or now), "%Y-%m-%d")),
            create_time = time.mktime(time.strptime(str(create_date or now), "%Y-%m-%d")),
            update_date = time.mktime(time.strptime(str(update_date or now), "%Y-%m-%d")),
            sec_owner = sec_owner_id,
            sensitive_data_count = dict_ASDC.get(count_private_data) or 0,
            sensitive_data = private_data or '',
            business_cata = business_cata or '',
            downtime = dict_APP_DOWNTIME.get(down_time) or 0,
            is_open = 0 if in_or_out == '内网' else 1,
            is_https = is_https
        )

        app.save()

        for value in domain.split(";"):
            Asset (
                app_id = app.id,
                name = sysname,
                value = value,
                type = 10,
                is_open = 0 if in_or_out == '内网' else 1,
                is_https = is_https,
                apptype = 10,
                status = dict_APP_STATUS.get(status) or "10"
            ).save()

def transfer_vul():
    print ("漏洞数据导入...")
    cursor = from_db.cursor()
    cursor.execute("select id, author, timestamp, title, related_asset, related_asset_inout, related_asset_status, related_vul_type, vul_self_rank, vul_source, vul_cesrc_id, vul_poc, vul_poc_html, vul_solution, vul_solution_html, grant_rank, vul_type_level, risk_score, person_score, done_solution, done_rank, residual_risk_score, vul_status, start_date, end_date, fix_date, attack_check, related_vul_cata from vul_reports ")

    data = cursor.fetchall()
    cursor.close()
    dict_VUL_TYPE = dict((v, k) for k, v in VUL_TYPE.items())
    dict_VUL_LEVEL = dict((v, k) for k, v in VUL_LEVEL.items())
    dict_VUL_STATUS = dict((v, k) for k, v in VUL_STATUS.items())
    dict_VUL_SOURCE = dict((v, k) for k, v in VUL_SOURCE.items())
    dict_VUL_LAYER = dict((v, k) for k, v in VUL_LAYER.items())


    now = str(datetime.now())[:10]

    for d in data:
        _id, author, timestamp, title, related_asset, related_asset_inout, related_asset_status, related_vul_type, vul_self_rank, vul_source, vul_cesrc_id, vul_poc, vul_poc_html, vul_solution, vul_solution_html, grant_rank, vul_type_level, risk_score, person_score, done_solution, done_rank, residual_risk_score, vul_status, start_date, end_date, fix_date, attack_check, related_vul_cata = d
        asset = Asset.get_or_none(Asset.value == related_asset)

        app_id = 0
        if asset:
            app_id = asset.app_id

        user_id = 1
        if author:
            user = User.get_or_none(User.email == author)
            if user:
                user_id = user.id

        if vul_status == "已通告":
            vul_status = "已确认"
        elif vul_status == "完成":
            vul_status = "已完成"
        elif vul_status == "未审核":
            vul_status = "待审核"

        if not dict_VUL_STATUS.get(vul_status):
            print (title, vul_status, dict_VUL_STATUS.get(vul_status))

        if vul_poc:vul_poc = vul_poc.replace("/srcpm/src/static/upload", "/upload")
        if vul_poc_html:vul_poc_html = vul_poc_html.replace("/srcpm/src/static/upload", "/upload")
        if vul_solution:vul_solution = vul_solution.replace("/srcpm/src/static/upload", "/upload")
        if vul_solution_html:vul_solution_html = vul_solution_html.replace("/srcpm/src/static/upload", "/upload")

        Vul(vul_name = title,
                vul_type = dict_VUL_TYPE.get(related_vul_type) or 75,
                vul_level = dict_VUL_LEVEL.get(vul_type_level) or 10,
                self_rank = vul_self_rank or 0,
                vul_desc_type = 0,
                vul_poc = vul_poc,
                vul_poc_html = vul_poc_html,
                vul_solution = vul_solution,
                vul_solution_html = vul_solution_html,
                audit_user_id = 1,
                reply = "",
                user_id = user_id if user_id else 0,
                submit_time = time.mktime(time.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S")),
                audit_time = time.mktime(time.strptime(str(start_date or now), "%Y-%m-%d")),
                notice_time = time.mktime(time.strptime(str(start_date or now), "%Y-%m-%d")),
                fix_time = time.mktime(time.strptime(str(fix_date or now), "%Y-%m-%d")),
                vul_status = dict_VUL_STATUS.get(vul_status) or 10,
                real_rank = done_rank or 0,
                risk_score = risk_score or 0,
                left_risk_score = residual_risk_score or 0,
                app_id = app_id,
                vul_source = dict_VUL_SOURCE.get(vul_source) or 0,
                send_msg = 0,
                is_retest = 0,
                layer = dict_VUL_LAYER.get(related_vul_cata) or 0
            ).save()


def transfer_article():
    print ("文章数据迁移...")
    cursor = from_db.cursor()
    cursor.execute("select drop_name,drop_title,drop_content,drop_content_html,drop_create_time,status,author_id,drop_modified_time,category_id,tags_name from postdrops")
    data = cursor.fetchall()
    cursor.close()
    for d in data:
        drop_name,drop_title,drop_content,drop_content_html,drop_create_time,status,author_id,drop_modified_time,category_id,tags_name = d
        cursor = from_db.cursor()
        cursor.execute("select email from login_users where id={}".format(author_id))
        data = cursor.fetchall()
        cursor.close()
        email = ""
        if data:
            email = data[0][0]

        drop_content = drop_content.replace("/srcpm/drops/static/upload", "/upload")
        drop_content_html = drop_content_html.replace("/srcpm/drops/static/upload", "/upload")

        Article(title = drop_title, alias = drop_name,
                content_type = 1,
                md_raw_content = drop_content,
                content = drop_content_html,
                raw_content = "",
                publish_time = time.mktime(time.strptime(str(drop_create_time), "%Y-%m-%d %H:%M:%S")),
                modify_time = time.mktime(time.strptime(str(drop_modified_time), "%Y-%m-%d %H:%M:%S")),
                author = email,
                category = category_id,
                status = status).save()


def transfer_score():
    print ("用户积分迁移...")
    users = User.select()
    for user in users:
        cursor = from_db.cursor()
        cursor.execute("select risk_score from vul_reports where author='{}'".format(user.email))
        data = cursor.fetchall()
        cursor.close()
        score = 0.0
        for d in data:
            score += (d[0] or 0)

        if score:
            User.update(total_points = score, available_points = score).where(User.id==user.id).execute()

def transfer_category():
    print ("文章分类迁移...")
    cursor = from_db.cursor()
    cursor.execute("select id,category_name from categorys ")
    data = cursor.fetchall()
    cursor.close()
    ids = [d[0] for d in data]
    max_ids = max(ids)
    for i in range(max_ids):
        Category(name="").save()

    for d in data:
        _id, category_name = d
        Category.update(name = category_name).where(Category.id == _id).execute()

    Category.delete().where(Category.id.not_in(ids)).execute()

def transfer_departs():
    print ("部门迁移到分组...")
    cursor = from_db.cursor()
    cursor.execute("select id,department,leader,email from departs ")
    data = cursor.fetchall()
    cursor.close()

    for d in data:
        _id,department,leader,email = d

        # 如果没有此用户，创建用户
        if email:
            email = email.lower().split(";")[0]
            user = User.get_or_none(User.email == email)
            if not user:
                username = email.split("@")[0]
                User(username = username, nickname = username, email = email, role_id = 2).save()


        group = Group.get_or_none(Group.name == department)
        if not group:
            owner = User.get_or_none(User.email == email)
            if owner:
                owner_id = owner.id
            else:
                owner_id = 1

            Group(name = department, desc = department, owner_id = owner_id).save()


    # 从资产中迁移owner到组用户中
    print ("从资产中迁移owner到组用户中...")
    cursor = from_db.cursor()
    cursor.execute("select department, owner from assets ")
    data = cursor.fetchall()
    cursor.close()

    for d in data:
        department, owner = d

        group = Group.get_or_none(Group.name == department)

        if group and owner:
            emails = owner.lower().split(";")
            for email in emails:
                user = User.get_or_none(User.email == email)
                if not user:
                    username = email.split("@")[0]
                    try:
                        user = User(username = username, nickname = username, email = email, role_id = 2)
                        user.save()
                    except Exception as e:
                        print ("username: {}, email not {}".format(username, email))
                        continue

                user_id = user.id
                group_id = group.id
                if not GroupUser.get_or_none(GroupUser.user_id == user_id, GroupUser.group_id == group_id):
                    GroupUser(user_id = user_id, group_id = group_id, role_id = 2).save()




def transfer_app_group():
    print ("应用组关联...")
    cursor = from_db.cursor()
    cursor.execute("select domain, department from assets")
    data = cursor.fetchall()
    cursor.close()

    for d in data:
        domain, department = d

        # 部门对应组
        group = Group.get_or_none(Group.name == department)

        # domain 对应找到应用
        if ";" in domain:
            domain = domain.split(";")[0]

        asset = Asset.get_or_none(Asset.value == domain)
        if group and asset:
            print ("app_id->group_id", asset.app_id, group.id)
            App.update(group_id = group.id).where(App.id == asset.app_id).execute()

