#!usr/bin/env python
#-*- coding:utf-8 -*-
import sys

def main(target, **kwargs):
    println ("开始扫描目标: {}".format(str(target)))
    println ("发现异常")
    println ("扫描过程详情 xxx")
    println ("扫描完成")
    return dict(status = True, data = ["hello", "world"])

if __name__ == "__main__":
    main()
