#-*- coding:utf-8 -*-
import os
import sys
import zipfile

def go():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print ('Usage: tornadoweb_init project')
    else:
        p = sys.argv[1]

        current_dir = (os.path.dirname(__file__))
        zip_ref = zipfile.ZipFile(os.path.join(current_dir, 'project.zip'), 'r')
        zip_ref.extractall(p)
        zip_ref.close()

if __name__ == "__main__":
    go()



