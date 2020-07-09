# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil

def walk_dir(d,topdown=True):
    for root, dirs, files in os.walk(d, topdown):
        for name in files:
            fn = os.path.join(root,name)
            if fn.endswith("py"):
                print(fn)
                os.remove(fn)


        for name in dirs:
            #print ('d', os.path.join(root,name))
            pass

if __name__=='__main__':
    walk_dir("./action")
    walk_dir("./logic")
    walk_dir("./tornadoweb")
