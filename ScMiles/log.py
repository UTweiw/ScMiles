# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 15:49:08 2018

@author: Wei Wei

This subroutine writes running informations to log file.

"""

__all__ = ['log']


def log(msg):
    import os
    from datetime import datetime
    filePath = os.path.dirname(os.path.abspath(__file__)) 
    outfolder = os.path.abspath(os.path.join(filePath, os.pardir)) + '/my_project_output/current'
    with open(outfolder+'/log', 'a+') as f1:
        loginfo = str(datetime.now()).split('.')[0] + "    " + msg
        print(loginfo, file=f1)


if __name__ == '__main__':
    log('test')