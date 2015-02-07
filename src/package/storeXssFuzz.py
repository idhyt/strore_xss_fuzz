#encoding=utf-8
#-------------------------------------------------------------------------------
# Name:        xss fuzz
#
# Author:      idhyt (idhytgg@gmail.com)
# Created:     $[DateTime-'DD/MM/YYYY'-DateFormat]
# Copyright:   (c) $[UserName] $[DateTime-'YYYY'-DateFormat]
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import glVar
import sys
import datetime
from selenium import webdriver
from selenium.common import exceptions
#from selenium.webdriver.common.keys import Keys 
import loginInfor
import myParse

class StoreXssFuzz:
    def __init__(self,seeds,labelCount,labelFileName):
        #初始化类函数
        self.labelCount=labelCount
        self.labelFileName=labelFileName
        self.linkQuence=LinkQuence()
        self.ignore_ext = ('js','css','png','jpg','gif','bmp','svg','exif','jpeg','exe','apk','rar','zip','doc','docx','ppt','pptx','pdf','ico')
        #myParse类实例化
        self.pageSourceParse = myParse.PageSourceParse()
        self.optmAlg = myParse.OptmAlg()
        self.fileOperate = myParse.FileOperate()
        self.dataOperate = myParse.DataOperate()
        #loginInfor实例化
        self.myLogin = loginInfor.MyLogin()
        #其他变量
        #seeds = http:/xxx.xxx.com
        self.seeds = seeds
        self.seedsNet = self.pageSourceParse.GetUrlNet(seeds)
        if self.seedsNet is None:
            print 'seeds format error!'
            exit(0)
        
        #使用种子初始化url队列
        if isinstance(seeds,str):
            self.linkQuence.AddUnvisitedUrl(seeds)
            #添加hash表
            seed_hash=self.optmAlg.UrlSimilar(seeds)
            self.linkQuence.AddUrlHash(seed_hash)
        #针对目标是多个域名的情况，暂时不考虑
        if isinstance(seeds,list):
            for seed in seeds:
                self.linkQuence.AddUnvisitedUrl(seed)
                #添加hash表
                seed_hash=self.optmAlg.UrlSimilar(seed)
                self.linkQuence.AddUrlHash(seed_hash)
        print "Add the seeds url \"%s\" to the unvisited url list" %str(self.linkQuence.unVisited)
   
    #fuzz主流程
    def XssFuzz(self, gNum = 0):
        #打开浏览器并登录
        self.driver = webdriver.Chrome()  
#            self.driver.implicitly_wait(20)
        if self.myLogin.Login(self.driver, self.seeds, 0)['isLogin'] is True:
            #登录成功,待抓取的链接不空且labels数量不大于指定数量
            while self.linkQuence.UnVisitedUrlsEnmpy() is False and self.linkQuence.GetLabelCount()<self.labelCount:
                try:
                    links=[]
                    #队头url出队列
                    visitUrl = self.linkQuence.UnVisitedUrlDeQuence()
                    #获取网页源码
                    pageSource = self.pageSourceParse.GetPageSource(self.driver, visitUrl)
                    if pageSource is None:
                        continue
                    #获取网页中超链接
                    links = self.pageSourceParse.GetHyperLinks(visitUrl,pageSource)
                    print "Get %d new links from link: %s" %(len(links), visitUrl)
                    #将visitUrl放入已访问的url中
                    self.linkQuence.AddVisitedUrl(visitUrl)
                    print "%d visited url count:" %self.linkQuence.GetVisitedUrlCount()
                    #遍历links，fuzz过程
                    self.TraverseLinks(links)                             
                    print "%d unVisited url count:" %self.linkQuence.GetUnvisitedUrlCount()                              
                except Exception,e:
                    print str(e)
                    pass
        #退出chrome
        self.driver.close()
        self.driver.quit()
                        
    def TraverseLinks(self, links):
        for link in links:
            try:
                link=link.lower()
                #解码 eg:'http%3a%2f%2fwww.skinpp.com%2fsetting%2f'
                if '%3a' in link:
                    import urllib
                    link=urllib.unquote(link)
                #判断是否为目标网站
                if self.seedsNet in self.pageSourceParse.GetUrlNetloc(link): #可优化
                    #过滤文件下载链接
                    if link.split('.')[-1].rstrip() not in self.ignore_ext:
                        #计算链接hash值
                        link_hash=self.optmAlg.UrlSimilar(link)
                        if link_hash not in self.linkQuence.urlHash:
                            self.linkQuence.AddUrlHash(link_hash)
                            self.linkQuence.AddUnvisitedUrl(link)
                            labelList = self.pageSourceParse.GetLabels(self.driver,link)# = 'http://news.sohu.com/20141207/n406726880.shtml')
                            if len(labelList) > 0:
                                #获取当前标签页面句柄
                                currentWindowHandle = self.driver.current_window_handle
                                for label in labelList:
                                    # label 入列
                                    self.linkQuence.AddLabelList(label)
                                    # fuzz label 
                                    self.FuzzBegin(label)
                                #关闭非当前标签页，以免造成标签页过多导致浏览器卡死
                                self.pageSourceParse.CloseWindow(self.driver, currentWindowHandle)
                                #回到原先窗口
                                self.driver.switch_to_window(currentWindowHandle)
                                print "%d total labelList:" %self.linkQuence.GetLabelCount()
                if self.linkQuence.GetLabelCount() > self.labelCount:
                    break
            except Exception,e:
                print str(e)
        
    def FuzzBegin(self,label):
        try:
            status={}
            startTime=datetime.datetime.now()
            xDict=label
            # input:3, textarea:2
            if len(xDict) >= 2:
                #解析label标签
                status = self.dataOperate.GetLabelInfor(xDict)
#                 #调用组装选择器代码模块
#                 strCode=self.dataOperate.SelectorCode(xDict)
                strCode = True
                if strCode is not None:  
                    #调用fuzz模块
                    if self.Fuzzing(xDict, strCode) is True:
                        status.setdefault('xss', 'yes')                                                                              
            endTime=datetime.datetime.now()
            useTime=(endTime-startTime).total_seconds() # 0.xxx Seconds                                     
        except Exception,e:
            print str(e)
            pass 
        finally:
            #信息存储         
            status.setdefault('time', useTime)
            status.setdefault('xss', 'no')
            self.fileOperate.StoreJson('scanLog.json',status)
            
    def Fuzzing(self, xDict, strCode):
        try:
            isXss=False
            xUrl=xDict['url']
            driver = self.driver
            if driver.current_url != xUrl:
                driver.get(xUrl)
                self.myLogin.Login(driver, xUrl, 1)
#             #插入payload         
#             driver.execute_script(strCode)
            #输入框发送payload并回车即代替提交功能
            if self.dataOperate.EmuSbmt(driver, xDict) is True:
#                 #刷新页面
#                 driver.refresh()
                #正则匹配payload
                pageSource=driver.page_source
                if glVar.reSIGNOFXSS.search(pageSource) is not None:
                    print 'fond xss from %s' %xUrl
                    isXss=True
                    self.fileOperate.StoreJson('found', xDict)
        #增加弹窗异常处理
        except exceptions.UnexpectedAlertPresentException,e:
            self.dataOperate.PopConfirm(driver)
            pass
        except Exception,e:
            print str(e)
        finally:            
            return isXss

#访问列表类   
class LinkQuence:
    def __init__(self):
        #已访问的url集合
        self.visited=[]
        #待访问的url集合
        self.unVisited=[]
        #获取的fuzz label
        self.labelList=[]
        #所有url的hash表
        self.urlHash=[]

    #添加到访问过得url队列中
    def AddVisitedUrl(self,url):
        self.visited.append(url)
    #未访问过得url出队列,pop
    def UnVisitedUrlDeQuence(self):
        try:
            return self.unVisited.pop()
        except:
            return None
    #保证每个url只被访问一次
    def AddUnvisitedUrl(self,url):
#         if url!="" and url not in self.visited and url not in self.unVisited:
        if url!="":
            self.unVisited.insert(0,url)
    #获得已访问的url数目
    def GetVisitedUrlCount(self):
        return len(self.visited)
    #获得未访问的url数目
    def GetUnvisitedUrlCount(self):
        return len(self.unVisited)
    #判断未访问的url队列是否为空
    def UnVisitedUrlsEnmpy(self):
        return len(self.unVisited)==0
    
    #添加到labelList列表
    def AddLabelList(self,label):
        self.labelList.append(label)
    #获得已获取的label数目
    def GetLabelCount(self):
        return len(self.labelList)
    
    #新url的hash入表
    def AddUrlHash(self, value):
        self.urlHash.append(value)
    
def ScanBegin(seeds,labelCount, labelFileName):
    #初始化unvisited列表
    myFuzz = StoreXssFuzz(seeds,labelCount,labelFileName)
    #main func
    myFuzz.XssFuzz()
#     #save
#     myFuzz.fileOperate.StoreList(labelFileName, myFuzz.linkQuence.labelList)
    print 'scan success!'
    
if __name__=="__main__":
    if len(sys.argv)!=3:
        print "usage:"+sys.argv[0]+" http://test.com/"+" labelCount"
        print "example:"+sys.argv[0]+" http://127.0.0.1/xss.html"+" 100"
    else:    
        #爬虫
        seeds=sys.argv[1]      
        labelCount=int(sys.argv[2])
        labelFileName='labellist'
        ScanBegin(seeds,labelCount, labelFileName)     
        
        