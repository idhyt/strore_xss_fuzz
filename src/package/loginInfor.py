#encoding=utf-8
#-------------------------------------------------------------------------------
# Name:        loginInfor
#
# Author:      idhyt (idhytgg@gmail.com)
# Created:     $[DateTime-'DD/MM/YYYY'-DateFormat]
# Copyright:   (c) $[UserName] $[DateTime-'YYYY'-DateFormat]
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import myParse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions

class MyLogin:
    def __init__(self):
        self.pageSourceParse = myParse.PageSourceParse()
    # flag=0 程序开始时登录操作    flag=1 fuzz过程中检测登录操作
    def Login(self, driver, url, flag):
        try:
#             #将浏览器最大化显示
#             driver.maximize_window()
            netloc = self.pageSourceParse.GetUrlNetloc(url)
            status = {'isLogin':False, 'isLogout':False}
            if 'skinpp' in netloc:
                if flag == 0:
                    driver.get('http://skinpp.com/setting')
                driver.find_element_by_id('login_email').clear()
                driver.find_element_by_id('login_email').send_keys('')
                driver.find_element_by_id('login_pwd').clear()
                driver.find_element_by_id('login_pwd').send_keys('')
                driver.find_element_by_css_selector('.btn-login').click()
                #判断登录成功标志（上传身份证）
                WebDriverWait(driver,10).until(lambda:driver, driver.find_element_by_id('imgFile'))
            
            elif '360' in netloc:
                if flag == 0:
                    driver.get('http://i.360.cn/login')
                driver.find_element_by_css_selector('input[class="quc-input quc-input-account"]').clear()
                driver.find_element_by_css_selector('input[class="quc-input quc-input-account"]').send_keys('')
                driver.find_element_by_css_selector('input[class="quc-input quc-input-password"]').clear()
                driver.find_element_by_css_selector('input[class="quc-input quc-input-password"]').send_keys('')
                driver.find_element_by_css_selector('input[class="quc-submit quc-button quc-button-sign-in"]').click()
                #判断登录成功标志（退出登录）
                WebDriverWait(driver,10).until(lambda:driver, driver.find_element_by_css_selector('a[class="lnk sign-out"]'))
                
            elif 'sohu' in netloc:
                if flag == 0:
                    driver.get('http://i.sohu.com/home.htm')
                driver.find_element_by_id('email').clear()
                driver.find_element_by_id('email').send_keys('')
                driver.find_element_by_id('password').clear()
                driver.find_element_by_id('password').send_keys('')
                driver.find_element_by_css_selector('input[type="submit"]').click()
                #判断登录成功标志（退出登录）
                WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id('logout_toolbar'))
                
            elif 'zhnews' in netloc:
                #myxsstest ks123456
                if flag == 0:
                    driver.get('http://bbs.zhnews.net/bbs/forum.php')
                driver.find_element_by_id('ls_username').clear()
                driver.find_element_by_id('ls_username').send_keys('')
                driver.find_element_by_id('ls_password').clear()
                driver.find_element_by_id('ls_password').send_keys('')
                driver.find_element_by_css_selector('button[type="submit"]').click()
                #判断登录成功标志（我的帖子）
                WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id('myitem'))
            
            elif 'mop' in netloc:
                #mytestxss ks123456
                if flag == 0:
                    driver.get('http://passport.mop.com/')
                driver.find_element_by_id('loginName').clear()
                driver.find_element_by_id('loginName').send_keys('')
                driver.find_element_by_id('loginPasswd').clear()
                driver.find_element_by_id('loginPasswd').send_keys('')
                driver.find_element_by_css_selector('input[class="fl btn btn-red"]').click()
                #判断登录成功标志（用户信息）
                WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_id('hi_user_info'))
    
            #不异常 即成功    
            status['isLogin'] = True
            status['isLogout'] = True
        #查找元素失败，即检测登录或者退出状态
        except exceptions.NoSuchElementException:
            status['isLogin'] = False
            status['isLogout'] = False  
        except Exception,e:
            print str(e)
        finally:
            return status
        
#     def LogoutDetect(self, driver, url):
#         try:
#             isLogout = False
#             netloc = urlparse.urlparse(url)[1]
#             if 'sohu' in netloc:
#                 driver.find_element_by_id('email')
#                 driver.find_element_by_id('password')
#                 self.Login(driver, url)
#         except:
#             isLogout = True            
#         finally:
#             return isLogout
            
        

        