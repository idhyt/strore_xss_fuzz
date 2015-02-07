#encoding=utf-8
#-------------------------------------------------------------------------------
# Name:        myParse
#
# Author:      idhyt (idhytgg@gmail.com)
# Created:     $[DateTime-'DD/MM/YYYY'-DateFormat]
# Copyright:   (c) $[UserName] $[DateTime-'YYYY'-DateFormat]
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import glVar
from bs4 import BeautifulSoup
import urlparse
import hashlib 
import time
import json
import datetime
import loginInfor

from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys 

class PageSourceParse:
    def __init__(self):
        self.fileOp = FileOperate()
        self.optmAlg = OptmAlg()
    
    #获取源码中得超链接
    def GetHyperLinks(self,url,pageSource):
        try:
            #查找页面a标签href
            links=[] 
            domain=url.split('/')[2]
            tempurl='http://'+domain 
            
            soup=BeautifulSoup(pageSource)
            a=soup.findAll({'a'}, {'href':True})
            for item in a:
                href=item['href']
                ahref=''
                if href.find('http')==0:
                    ahref=href
                elif href.find('//')==0:
                    ahref='http:'+href
                elif href.find('/')==0:
                    ahref=tempurl+href
                if len(ahref)!=0:
                    #针对重定向链接的处理 
                    #http://www.gd.gov.cn/jump.htm?url=http://www.rftgd.gov.cn/
                    #http://c.nfa.jd.com/adclick?sid=2&cid=601&aid=3627&bid=0&unit=75497&advid=113179&guv=&url=http://jmall.jd.com/p150919.html
                    if ahref.find('=http')!=-1:
                        ahref1=ahref.split("=http")[0]+'='
                        ahref2='http'+ ahref.split("=http")[1]
                        links.append(ahref1) 
                        links.append(ahref2)
                    else:
                        links.append(ahref)                                        
#             return links
        except Exception,e:
            print str(e)
            pass
        finally:
            return links
        
    #获取链接中的label
    def GetLabels(self,driver,link):
        #爬取获取到的链接中的label
        try:
            labelList=[]
            status={}
            newLabelCount=0
            startTime=datetime.datetime.now()                          
            #获取网页源码
            pageSource = self.GetPageSource(driver, link)
            if pageSource is not None:
                #获取label列表
                labelList=self.LabelParse(link,pageSource)
                newLabelCount=len(labelList)
                print "Get %d new Labels from link: %s" %(newLabelCount,link)                     
            endTime=datetime.datetime.now()
            useTime=(endTime-startTime).total_seconds() # 0.xxx Seconds    
        except Exception,e:
            print str(e)
            pass
        #记录爬取url信息
        finally:
            #记录每个链接爬取的label信息    
            status.setdefault('url', link) 
            status.setdefault('time', useTime)
            status.setdefault('count',newLabelCount)
            self.fileOp.StoreJson('spiderLog.json',status)
            return labelList
        
    #获取存在输入的标签及id
    #保存格式：{url:'xxxx',label:'input/textarea',id:'xx'}
    def LabelParse(self,url,pageSource):
        try:
            labelList=[]            
            soup=BeautifulSoup(pageSource)
            inputLabels=soup.findAll({'input'}, {'type':'text'}) 
            for label in inputLabels:
                labelDic={}
                if label.has_key('id'):
                    labelId=label['id']             
                    labelDic.setdefault('id',labelId)
                elif label.has_key('name'):
                    labelName = label['name']
                    labelDic.setdefault('name', labelName)
                elif label.has_key('class'):
                    import re
                    reClass = re.compile(r'class=[\"\']([\w\s]{1,})[\"\']', re.IGNORECASE)
                    reResult = reClass.search(str(label))
                    if reResult is not None:
                        strClass = reResult.group(0)
                        reValue = re.compile(r'[\"\'].+[\"\']', re.IGNORECASE)
                        reResult = reValue.search(strClass)
                        if reResult is not None:
                            labelValue = reResult.group(0).strip('"').strip("'")
#                     labelValue=label['class']        
                        labelDic.setdefault('class',labelValue)
                if len(labelDic)>0:
                    labelDic.setdefault('url',url)
                    labelDic.setdefault('label','input')
                    labelList.append(labelDic)
            #针对textarea标签的查找
            if soup.find('textarea') is not None:
                textareaDic={}
                textareaDic.setdefault('url',url)
                textareaDic.setdefault('label', 'textarea')
                labelList.append(textareaDic)
            
            if len(labelList) > 1:
                labelList = self.optmAlg.DedupDict(labelList)
        except Exception,e:
            print str(e)
            pass
        finally:
            return labelList
        
    # 获取网页源码
    def GetPageSource(self, driver, url):
        try:
            pageSource = None
            if driver.current_url != url:
                driver.get(url)
                #如果是退出登录链接，增加验证
                loginInfor.MyLogin().Login(driver, url, 1)  
            pageSource = driver.page_source
            
        except exceptions.UnexpectedAlertPresentException,e:
            DataOperate().PopConfirm(driver)
        except Exception,e:
            print str(e)
        finally:
            return pageSource
        
    # 获取目标域名
    def GetUrlNetloc(self, url):
        try:
            netloc = None
            netloc = urlparse.urlparse(url)[1]
        except Exception,e:
            print str(e)
            
        finally:
            return netloc
    
    def GetUrlNet(self,url):
        try:
            net = None
            netloc = self.GetUrlNetloc(url)
            if netloc is not None:
                tmp = netloc.split('.')
                if len(tmp) == 3:
                    net = tmp[1:2][0]   
        except Exception,e:
            print str(e)
            pass
        finally:
            return net
        
    # 关闭非当前窗口标签页
    def CloseWindow(self, driver, currentWindowHandle):
        try:
            isClose = False
            allHandles=driver.window_handles
            #循环判断窗口是否为当前窗口
            if len(allHandles) > 1:
                for handle in allHandles:
                    if handle != currentWindowHandle:
                        driver.switch_to_window(handle)
                        driver.close()
            allHandles=driver.window_handles
            if len(allHandles) == 1:
                isClose = True
                
        except Exception,e:
            print str(e)
            pass
        finally:
            return isClose
        
#optimization algorithm
class OptmAlg: 
#     URL相似度判断
#         主要取4个值
#     1,netloc的hash值
#     2,path字符串拆解成列表的列表长度
#     3,path中字符串的长度
#     4,query参数名hash    a=1&b=2&c=3 : hash('abc')
    def UrlSimilar(self, url, hash_size=10000000):
        try:
            tmp = urlparse.urlparse(url)
            netloc = tmp[1]
            path = tmp[2][1:]
            query = tmp[4]
            
            netloc_value = 0
            path_value = 0
            query_value = 0
            url_value = 0
            
            if len(netloc) > 0:
                netloc = netloc.lower()
                netloc_value = hash(hashlib.new("md5", netloc).hexdigest())%(hash_size-1)
            
            if len(path) > 0:    
                #hash path
                path = path.lower()
                path_list = path.split('/')[:-1]
                # path = 'a/b/c/d.html'
                if len(path.split('/')[-1].split('.')) > 1:
                    tail = path.split('/')[-1].split('.')[:-1][0]
                # path = ''    
                elif len(path.split('/')) == 1 :
                    tail = path
                # path = 'a/'
                else:
                    tail = '1'
                path_list.append(tail)
                path_length = len(path_list)
                for i in range(path_length):
                    iLength = len(path_list[i]) * (10**(i+1))
                    path_value += iLength
                path_value = hash(hashlib.new("md5", str(path_value)).hexdigest())%(hash_size-1)
                                       
            #hash query (参数名串hash运算)
            if len(query) > 0:
                strKeyNames = ''
                query = query.lower()
                query_list = query.split('&')
                query_length = len(query_list)  # 2 1
                for i in range(query_length):
                    keyName = query_list[i].split('=')[0]
                    strKeyNames += keyName    
                query_value = hash(hashlib.new("md5", strKeyNames).hexdigest())%(hash_size-1)
                    
            url_value = hash(hashlib.new("md5", str(netloc_value + path_value + query_value)).hexdigest())%(hash_size-1)
        except Exception,e:
            print str(e)
            
        finally:
            return url_value
        
        
    #过滤列表中的字典Deduplication
    def DedupDict(self, DictList):
        try:
            for item in DictList:
                while DictList.count(item)>1:
                    DictList.remove(item)
        
        except Exception,e:
            print str(e)
        finally:
            return DictList
        
        
#文件操作类
class FileOperate:
    def __init__(self):
        pass
    
    #初始化    
    def InitFile(self,fineName):
        try:
            t = time.strftime('%Y-%m-%d',time.localtime(time.time()))     
            f=open(fineName,"a")
            f.write('\n---------'+t+'---------\n')
        except Exception,e:
            print str(e)
        finally:
            f.close() 
    
    # save log 403 error...
    def ErrorLog(self,fileName,infor):
        try:
            f=open(fileName,'a')
            f.write(infor+'\n')
        except Exception,e:
            print str(e)
        finally:
            f.close()
            
    # found xss log
    def FindLog(self,url,describ):
        try:
            f=open("found","a")
            f.write(url+'\n')
#            f.write(url+" ->found "+describ+"\n")
            print "found "+describ+" ->"+url
            #xss入库
#            KXssDB.AddXss(glVar.DOMAIN, url, 1)          
        except Exception,e:
            self.storeLog('error',str(e)+'->'+url)
        finally:
            f.close()

    def File2Lines(self,filename):
        try:
            f=open(filename,"r+")
            line=f.readlines();
            for i in range(0,len(line)):
                #delete \n
                line[i]=line[i].rstrip("\n")
            return line
        except Exception,e:
            print str(e)
        finally:
            f.close()
      
    def Lines2File(self,filename, lines):
        try:
            f=open(filename,"w+")
            for line in lines:
                f.write(line +'\n')
        except Exception,e:
            print str(e)
        finally:
            f.close() 
                 
    #扫描链接状态等信息：{'Code':'200', 'url':'xx.com', 'time':'0.123', 'xss':'yes'}
    def StoreJson(self,fileName,status):
        try:
            with open(fileName, 'a') as f:
                f.write(json.dumps(status)+'\n')
        except Exception,e:
            print str(e)
        finally:
            f.close()
                
    #保存list     
    def StoreList(self,fileName,listName):
        try:
            f=open(fileName,"w")
            for i in listName:
                f.write(str(i) +'\n')            
        except Exception,e:
            print str(e)
            pass
         
#数据类操作
class DataOperate: 
    
    #参数： 标签 元素 字典
    def SelectorCode(self, xDict):
        try:
            strCode=None
            xLabel=xDict['label']
            if xLabel == 'textarea':
                strCode='textarea'
            elif 'id' in xDict:
                # $("input[type='text'][id='id值']").attr('value','xss');
                #strCode='$(\'input[type="text"][id="' + xDict['id'] + '"]\').attr("value","' + glVar.strPayload+ '")'
                # document.getElementById('query').value=glVar.strPayload
                strCode='document.getElementById("' + xDict['id'] + '").value="' + glVar.strPayload + '"'                
            elif 'name' in xDict:
                strCode='$(\'input[type="text"][name="' + xDict['name'] + '"]\').attr("value","' + glVar.strPayload+ '")'
            elif 'class' in xDict:
                # $("input[type='text'][value='value值']");
                strCode='$(\'input[type="text"][class="' + xDict['class'] + '"]\').attr("value","' + glVar.strPayload+ '")'
        except Exception,e:
            print str(e)
        finally:
            return strCode
    
    #指定窗口插入payload并提交
    def EmuSbmt(self, driver, xDict):
        try:
            isSbmt = False
            element = None
            xLabel = xDict['label']
            xUrl = xDict['url']

            #先判断textarea
            if xLabel == 'textarea':
                isSbmt = self.SbmtTextarea(driver, xUrl)
            elif xLabel == 'input':
                if 'id' in xDict:
                    xId = xDict['id']
                    element = driver.find_element_by_id(xId)
                elif 'name' in xDict:
                    xName = xDict['name']
                    xName = 'input[type="text"]' + '[name="' + xName + '"]'
                    element = driver.find_element_by_css_selector(xName)
                elif 'class' in xDict:
                    xClass = xDict['class']
                    xClass = 'input[type="text"]' + '[class="' + xClass + '"]'
                    element = driver.find_element_by_css_selector(xClass)
                
                if element is not None:
                    element.send_keys(glVar.strPayload)
                    element.send_keys(Keys.ENTER)
                    isSbmt = True
                    time.sleep(1)  
                              
        except Exception,e:
            print str(e)
            isSbmt = False
        finally:
            return isSbmt
        
    #针对弹窗的处理    
    def PopConfirm(self, driver):
        try:
            isAlert = None
            isAlert=driver.switch_to_alert()
            if isAlert is not None:
                #接受警告提示
                isAlert.accept()
#                 #取消对话框
#                 isAlert.dismiss()
        except Exception,e:
            print str(e)
        finally:
            pass
    
    #获取存储信息Dict
    def GetLabelInfor(self, xDict):
        try:
            status = {}
            xUrl=xDict['url']
            xLabel=xDict['label']
            if 'id' in xDict:
                status.setdefault('id', xDict['id'])
            elif 'name' in xDict:
                status.setdefault('name', xDict['name'])
            elif 'class' in xDict:
                status.setdefault('class', xDict['class'])
            
            status.setdefault('url', xUrl)
            status.setdefault('label', xLabel)                
        except Exception,e:
            print str(e)
            pass
        finally:
            return status
        
    #textarea方法
    def SbmtTextarea(self,driver,url):
        try:
            isSbmt = False
            netloc = urlparse.urlparse(url)[1]
            element = driver.find_element_by_tag_name('textarea')
            inserText = glVar.strPayload + '以前不懂，看贴总是不回 ，一直没提升等级和增加经验'  #现在我明白了，反正回贴可以升级 ，也可以赚经验，而升级又需要经验 ，我就把这句话复制下来 ，遇贴就灌水，捞经验就闪'
            element.send_keys(inserText)
            if 'sohu' in netloc:
                #<button class="btn-fw btn-bf btn-fw-main">发布</button>
                driver.find_element_by_css_selector('input[class="btn-fw btn-bf btn-fw-main"]').click()
                time.sleep(1)
                isSbmt = True
                
            elif 'zhnews' in netloc:
                driver.find_element_by_css_selector('input[type="submit"]').click()
                time.sleep(1)
                isSbmt = True
            elif 'mop' in netloc:
                driver.find_element_by_css_selector('a[class="hi-btnMdfPwd middle mr10 h-profile-basic-save"]').click()    
                time.sleep(1)
                isSbmt = True
        except Exception,e:
            isSbmt = False
            print str(e)
            pass
        finally:
            element.send_keys(Keys.CONTROL, Keys.ENTER)
            return isSbmt  
    
        
        
        
     
