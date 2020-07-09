# -*- coding:utf-8 -*-
from optparse import OptionParser, OptionGroup
from tornadoweb import *
from json import loads, dumps
from os import wait, fork, getpid, getppid, killpg, waitpid
from multiprocessing import cpu_count
from signal import signal, pause, SIGCHLD, SIGINT, SIGTERM, SIGUSR1, SIGUSR2, SIG_IGN

from redis import Redis, ConnectionError

#from settings import *


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
        self._processes = cpu_count()
        #self._processes = 1

        self._consumer = Consumer()
        self._parent = getpid()
        self._services = self._get_services()

    def _signal(self):

        def sig_handler(signum, frame):
            pid = getpid()

            if signum in (SIGINT, SIGTERM):
                if pid == self._parent:
                    signal(SIGCHLD, SIG_IGN)
                    killpg(self._parent, SIGUSR1)
            elif signum == SIGCHLD:
                if pid == self._parent:
                    print ("sub process {0} exit...".format(wait()))
            elif signum == SIGUSR1:
                print ("process {0} exit...".format(pid == self._parent and pid or (pid, self._parent)))
                exit(0)

        signal(SIGINT, sig_handler)
        signal(SIGTERM, sig_handler)
        signal(SIGCHLD, sig_handler)
        signal(SIGUSR1, sig_handler)


    def _get_services(self):
        from logic import service
        services = dict((item, getattr(service, item)) for item in dir(service) if item.startswith("service_"))
        for k, v in services.items():
            print (k, v)

        return services


    def _run(self):

        for i in range(self._processes):
            if fork() > 0: continue

            try:
                while True:
                    cmd, data = self._consumer.consume()
                    print (cmd, data)
                    srv_func = self._services.get(cmd)

                    if srv_func:
                        try:
                            srv_func(data)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()

            except ConnectionError as e:
                import traceback
                traceback.print_exc()
                print ("Exception {0}".format(getpid()), ":", e.message)
            exit(0)


    def run(self):
        self._signal()

        try:
            self._run()
        except RuntimeError:
            print ("ERROR", ": Is redis running?")
            exit(-1)

        while True: pause()


def _get_opt():
    parser = OptionParser("%prog [options]", version="%prog v0.9")
    parser.add_option("--config", dest = "config", default = "settings.py", help = "config")
    return parser.parse_args()


if __name__ == "__main__":
    opts, args = _get_opt()
    ConfigLoader.load(opts.config)

    Service().run()

