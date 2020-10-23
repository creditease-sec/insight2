# -*- coding:utf-8 -*-
from json import loads, dumps
from optparse import OptionParser, OptionGroup

from redis import Redis

from tornadoweb import *

def unpack(data):
    pack = loads(data)
    return pack["cmd"], pack["data"]


class Consumer(object):
    def __init__(self):
        self._redis = Redis(host = __conf__.REDIS_HOST, port = __conf__.REDIS_PORT, \
                password = __conf__.REDIS_PASS, db = __conf__.REDIS_DB)


    def consume(self):
        return unpack(self._redis.blpop(__conf__.REDIS_CHANNEL)[1])


    def close(self):
        if hasattr(self, "_redis"):
            self._redis.connection_pool.disconnect()


class Service(object):
    def __init__(self):
        self._consumer = Consumer()
        self._services = self._get_services()


    def _get_services(self):
        from logic import service
        services = dict((item, getattr(service, item)) for item in dir(service) if item.startswith("service_"))
        for k, v in services.items():
            print (k, v)

        return services



    def run(self):
        while True:
            cmd, data = self._consumer.consume()
            srv_func = self._services.get(cmd)

            if srv_func:
                try:
                    srv_func(data)
                except Exception as e:
                    import traceback
                    traceback.print_exc()


def _get_opt():
    parser = OptionParser("%prog [options]", version="%prog v0.9")
    parser.add_option("--config", dest = "config", default = "settings.py", help = "config")
    return parser.parse_args()


if __name__ == "__main__":
    opts, args = _get_opt()
    ConfigLoader.load(opts.config)

    Service().run()
