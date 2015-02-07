#encoding=utf-8
#-------------------------------------------------------------------------------
# Name:        webScan.py
# Purpose:     Scan Xss
# usage:       webScan.py    url    spider_count
#
# Author:      idhyt (idhytgg@gmail.com)
# Created:     $[DateTime-'DD/MM/YYYY'-DateFormat]
# Copyright:   (c) $[UserName] $[DateTime-'YYYY'-DateFormat]
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
from package import storeXssFuzz
import time

class MyWebScan:
    def __init__(self):
        t = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())) 
        print str(t)
        #labellist文件名
        self.labellist=str(t)
    def WebScanBegin(self,seeds,scanCount):
        print '\nScanBegin...'
        storeXssFuzz.ScanBegin(seeds, scanCount, self.labellist)
                         
if __name__=="__main__":
    if len(sys.argv)!=3:
        print "usage:"+sys.argv[0]+" http://test.com/"+" labelCount"
        print "example:"+sys.argv[0]+" http://127.0.0.1/xss.html"+" 100"
    else:
        seeds=sys.argv[1]     
        scanCount=int(sys.argv[2])
        #初始化全局变量
        print 'webScan initialise...'+str(seeds)
        webScan=MyWebScan()
        webScan.WebScanBegin(seeds,scanCount)    
        
        
        
        
        
        
        