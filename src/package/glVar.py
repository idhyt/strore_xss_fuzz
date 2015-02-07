#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        global
# Purpose:     模块间传递全局变量,配置文件信息
#
# Author:      idhyt (idhytgg@gmail.com)
# Created:     $[DateTime-'DD/MM/YYYY'-DateFormat]
# Copyright:   (c) $[UserName] $[DateTime-'YYYY'-DateFormat]
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import re
#域名
DOMAIN=''
#请求超时
TIMEOUT=3
#扫描延时
nSleep=1
#payload
strPayload='<"g(0x41)g">'
reSIGNOFXSS=re.compile(r'[<"].{0,5}g\(0x41\)g.{0,5}[>"]',re.IGNORECASE)
#提交按钮
sbmtSelector="$('input[type=submit]').trigger('click')"