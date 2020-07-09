#-*- coding:utf-8 -*-

import six
if six.PY3:
    import builtins as __builtin__
else:
    import __builtin__


from os.path import exists
from types import ModuleType

from .utility import app_path, staticclass



@staticclass
class ConfigLoader(object):

    @staticmethod
    def load(config = None):
        if config:
            pys = map(app_path, (config, ))
        else:
            pys = map(app_path, ("settings.py", ))

        dct = {}
        module = ModuleType("__conf__")

        for py in pys:
            scope = {}
            with open(py,'r') as f:
                body = f.read()
                exec(body, scope)

                for k, v in scope.items():
                    if k.startswith("__"): continue
                    setattr(module, k, v)

        __builtin__.__conf__ = module

