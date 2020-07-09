#!coding=utf-8
import json
from hashlib import md5

from playhouse.shortcuts import model_to_dict

from tornadoweb import *
from logic.model import *
from logic.utility import *

@url(r"/docs", needcheck = False, category = "Docs")
class Docs(LoginedRequestHandler):
    def get(self):
        total = 0
        result = []
        ret = {}
        handlers = get_handlers()
        for k, v in handlers.items():
            method = "GET" if 'get' in  v.__dict__ else "POST"
            doc = v.__doc__ or "未知"
            doc = [item for item in doc.split("\n") if item.strip()]
            name = doc[0].strip()
            args = [item.strip() for item in doc[1:]]
            response = ""
            if args and args[-1].startswith("response:"):
                response = args[-1]
                args = args[:-1]

            for item in v.__urls__:
                uri = __conf__.API_VERSION + item[0]
                category = item[3]
                total += 1

                doc = dict(doc = name, uri = uri, args = args, method = method, id = uri, name = name)
                if response:
                    try:
                        doc["response"] = eval(response.replace("response:", "").strip())
                    except Exception as e:
                        doc["response"] = response.replace("response:", "").strip()


                if ret.get(category):
                    ret[category].append(doc)
                else:
                    ret[category] = [doc]

        for k, v in ret.items():
            result.append(dict(id = k, name = k, children = v))

        category = [item.get('name') for item in result]
        self.write(dict(total = total, result = result, category = category))


@url(r"/log/tail", category = "系统日志")
class LogList(LoginedRequestHandler):
    """
        系统日志

        size: 读取行数
    """
    def get(self):
        size = int(self.get_argument("size", 100))

        with open("./logs/web.log") as f:
            data = f.readlines()
            data = data[-1 * size:]
        
        self.write(dict(log = data))

@url(r"/init/db", category = "系统")
class InitDB(LoginedRequestHandler):
    """
        初始化数据库
    """
    def get(self):
        from logic.model import init_db
        init_db()
        self.write(dict(status = True, msg = "初始化完毕"))

@url(r"/example/data", category = "系统")
class ExampleData(LoginedRequestHandler):
    """
        示例数据
    """
    def get(self):
        from logic.model import gen_data
        gen_data()
        self.write(dict(status = True, msg = "生成完毕"))

