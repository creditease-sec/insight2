#!coding=utf-8
import json
import math
import time
from hashlib import md5
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import *
from logic.define import *

@url(r"/dashboard", needcheck = False, category = "面板")
class DashBoard(LoginedRequestHandler):
    """
        概览

    """
    def get(self):
        start = float(self.get_argument("start", 0))
        end = float(self.get_argument("end", time.time()))

        vuls = [item for item in Vul.select(Vul.submit_time, Vul.vul_status, Vul.fix_time, Vul.vul_source, Vul.real_rank, Vul.vul_type, Vul.audit_time, Vul.app_id)]
        apps = [item for item in App.select(App.id, App.appname, App.check_time)]
        assets = [item for item in Asset.select(Asset.id, Asset.app_id, Asset.type)]
        ### 概览
        now = datetime.now()
        current_month_start = datetime(year = now.year, month = now.month, day = 1)
        current_month_start = time.mktime(time.strptime(str(current_month_start), "%Y-%m-%d %H:%M:%S"))
        last_month = now - timedelta(days = now.day)

        last_month_start = datetime(year = last_month.year, month = last_month.month, day = 1)
        last_month_start = time.mktime(time.strptime(str(last_month_start), "%Y-%m-%d %H:%M:%S"))

        last_month_end = datetime(year = last_month.year, month = last_month.month, day = last_month.day)
        last_month_end = time.mktime(time.strptime(str(last_month_end), "%Y-%m-%d %H:%M:%S"))

        current_month_vul_count = len([item for item in vuls if item.submit_time >= current_month_start])
        last_month_vul_count = len([item for item in vuls if (item.submit_time >= last_month_start and item.submit_time < last_month_end)])

        fix_count = len([item for item in vuls if item.vul_status == 60])

        last_three_month =  now - timedelta(weeks = 12)
        last_three_month_start = datetime(year = last_three_month.year, month = last_three_month.month, day = 1)
        last_three_month_start = time.mktime(time.strptime(str(last_three_month_start), "%Y-%m-%d %H:%M:%S"))
        app_count = len(apps)
        test_app_count = len([item for item in apps if item.check_time >= last_three_month_start])

        total_vul_count = len(vuls)
        test_percent = round(test_app_count / app_count * 100, 2) if app_count else 0
        fixes_percent = round(fix_count / total_vul_count * 100, 2) if total_vul_count else 0

        star_level = math.ceil((test_percent/100 + fixes_percent/100) / 2 / 0.2) or 1

        vul_ratio_data = []
        for k, v in VUL_STATUS.items():
            count = len([item for item in vuls if item.vul_status == int(k)])
            if count:
                vul_ratio_data.append({"name": v, "value": count})

        k_date = {}
        for vul in vuls:
            f_time = time.strftime("%Y-%m-%d", time.localtime(vul.submit_time))
            if f_time in k_date:
                k_date[f_time] += 1
            else:
                k_date[f_time] = 1

        x = []
        y = []
        for key in sorted(k_date.keys()):
            x.append(key)
            y.append(k_date.get(key))

        today = date.today()
        quarter_start_date = date(today.year,today.month - (today.month - 1) % 3, 1)
        quarter_start_ts = time.mktime(time.strptime(str(quarter_start_date), "%Y-%m-%d"))

        today = date.today()
        quarter_end_date = date(today.year,today.month - (today.month - 1) % 3 +2, 1) + relativedelta(months=1,days=-1)
        quarter_end_ts = time.mktime(time.strptime(str(quarter_end_date), "%Y-%m-%d"))

        vullogs = VulLog.select().where(VulLog.create_time >= quarter_start_ts, VulLog.create_time <= quarter_end_ts)
        ex_logs = ExtensionLog.select().where(ExtensionLog.create_time >= quarter_start_ts, ExtensionLog.create_time <=quarter_end_ts)

        hot_data = {}
        for item in vullogs:
            f_time = time.strftime("%Y-%m-%d", time.localtime(item.create_time))
            if f_time in hot_data:
                hot_data[f_time] += 1
            else:
                hot_data[f_time] = 1

        for item in ex_logs:
            f_time = time.strftime("%Y-%m-%d", time.localtime(item.create_time))
            if f_time in hot_data:
                hot_data[f_time] += 1
            else:
                hot_data[f_time] = 1
        hot_data = sorted([[k, v, k] for k, v in hot_data.items()], key = lambda item:item[0])

        dashboard_data = {
            "summary":{
                "current_month_vul_count":current_month_vul_count,
                "vul_increase_percent": round((current_month_vul_count - last_month_vul_count)/last_month_vul_count * 100 if last_month_vul_count else 0, 2),
                "vul_increase_count": current_month_vul_count - last_month_vul_count,
                "test_percent": test_percent,
                "fixes_percent": fixes_percent,
                "star_level": star_level,
                "hot_data": {"data": hot_data, "range": [quarter_start_date.isoformat(), quarter_end_date.isoformat()]},
                "vul_trend_data":{
                  "x": x,
                  "y": y
                },
                "vul_ratio_data": vul_ratio_data
            },
        }

        ### 漏洞统计
        vuls2 = [item for item in vuls if item.submit_time >= start and item.submit_time <= end]
        total_vul_count = len(vuls2)
        solved_count = 0
        total_solved_cost = 0
        for vul in vuls2:
            if vul.fix_time:
                total_solved_cost += (vul.fix_time - vul.submit_time)
                solved_count += 1

        average_solved_cost = total_solved_cost / solved_count if solved_count else 0

        solved_score = solved_count / total_vul_count * 100 if total_vul_count else 0

        vul_source_data = []
        for k, v in VUL_SOURCE.items():
            count = len([item for item in vuls2 if item.vul_source == int(k)])
            if count:
                vul_source_data.append({"name": v, "value": count})

        rank_distribution_data = {}
        for vul in vuls2:
            rank = vul.real_rank
            if not rank: continue
            if rank in rank_distribution_data:
                rank_distribution_data[rank] += 1
            else:
                rank_distribution_data[rank] = 0

        rank_distribution_data = [[k, v, k] for k, v in rank_distribution_data.items()]
        rank_distribution_data = [['score', 'amount', 'rank']] + rank_distribution_data

        vul_type_data = []
        for k, v in VUL_TYPE.items():
            count = len([item for item in vuls2 if item.vul_type == int(k)])
            if count:
                vul_type_data.append({"name": v, "value": count})

        vul_types = [item["name"] for item in vul_type_data]
        vul_type_data = sorted(vul_type_data, key=lambda item:item['value'], reverse = True)

        vul_type_trend_line_data = dict((vul_type, []) for vul_type in vul_types)

        for vul_type in vul_types:
            tmp_data = dict((week, 0) for week in range(1, 8))
            for vul in vuls2:
                if not vul.audit_time: continue
                audit_time = datetime.fromtimestamp(vul.audit_time)
                week_day = audit_time.weekday() + 1
                tmp_data[week_day] += 1

            series = {
                "name": vul_type,
                "type": 'line',
                "stack": '总量',
                "data": list(tmp_data.values())
            }
            vul_type_trend_line_data[vul_type] = series


        vul_dashboard = {
           "total_vul_count":total_vul_count,
           "average_solved_cost": average_solved_cost,
           "total_solved_cost": total_solved_cost,
           "solved_score": round(solved_score, 2),
           "vul_source_data": {"data": vul_source_data},
           "vul_ratio_data": {"data": vul_ratio_data},
           "rank_distribution_data": rank_distribution_data,
           "vul_type_top_data":{
                 "xAxis_data": [item["name"] for item in vul_type_data],
                 "series_data": [item["value"] for item in vul_type_data]
           },
           "vul_type_trend_line_data":{
                "legend_data": list(vul_type_trend_line_data.keys()),
                "xAxis_data": ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                "series": list(vul_type_trend_line_data.values())
           }
        }

        dashboard_data["vul"] = vul_dashboard

        ### 资产统计
        vuls3 = vuls
        unassociated_asset_count = len([item for item in assets if not item.app_id])
        app_asset_associated_percent = round((len(assets) - unassociated_asset_count) / len(assets) * 100, 2) if len(assets) else 0

        unactive_asset_count = len([item for item in apps if item.check_time <= time.time() - 3600 * 24 * 30])

        dict_apps = dict((item.id, item.appname) for item in apps)

        asset_generation_data = {}
        asset_overdue_sovled_data = {}
        asset_overdue_unsovled_data = {}
        for vul in vuls3:
            app_id = vul.app_id
            if not app_id: continue
            appname = dict_apps.get(app_id)

            if appname in asset_generation_data:
                asset_generation_data[appname] += 1
            else:
                asset_generation_data[appname] = 1

            if vul.vul_status in [20, 30, 35, 60]:
                if appname in asset_overdue_sovled_data:
                    asset_overdue_sovled_data[appname] += 1
                else:
                    asset_overdue_sovled_data[appname] = 1
            else:
                if appname in asset_overdue_unsovled_data:
                    asset_overdue_unsovled_data[appname] += 1
                else:
                    asset_overdue_unsovled_data[appname] = 1

        asset_ratio_data = {}
        for asset in assets:
            type_name = ASSET_TYPE.get(asset.type)
            if not type_name: continue

            if type_name in asset_ratio_data:
                asset_ratio_data[type_name] += 1
            else:
                asset_ratio_data[type_name] = 1

        asset_ratio_data = [{"name": k, "value": v} for k, v in asset_ratio_data.items()]

        _asset = {
            "total_app_count": len(apps),
            "total_asset_count": len(assets),
            "app_asset_associated_percent": app_asset_associated_percent,
            "unassociated_asset_count": unassociated_asset_count,
            "unactive_asset_count":unactive_asset_count,
            "asset_generation_data":{
                "total": sum(asset_generation_data.values()),
                "x_data": list(asset_generation_data.keys()),
                "series_data": list(asset_generation_data.values()),
            },
            "asset_overdue_sovled_data":{
                "total":sum(asset_overdue_sovled_data.values()),
                "x_data": list(asset_overdue_sovled_data.keys()),
                "series_data": list(asset_overdue_sovled_data.values())
            },
            "asset_overdue_unsovled_data":{
                "total":sum(asset_overdue_unsovled_data.values()),
                "x_data": list(asset_overdue_unsovled_data.keys()),
                "series_data": list(asset_overdue_sovled_data.values()),
            },
            "asset_ratio_data":{
                "data": asset_ratio_data
            }
        }


        dashboard_data['assets'] = _asset
        self.write(dict(status = True, data = dashboard_data))
