#!/usr/bin/env python
#-*- coding:utf-8 -*-
from optparse import OptionParser, OptionGroup
from tornadoweb import *


def _get_opt():
    parser = OptionParser("%prog [options]", version="%prog v0.9")
    parser.add_option("--config", dest = "config", default = "settings.py", help = "config")
    return parser.parse_args()

def main():
    opts, args = _get_opt()
    ConfigLoader.load(opts.config)

    from logic import cron_func
    cron_func.check_vul()

if __name__ == "__main__":
    main()




