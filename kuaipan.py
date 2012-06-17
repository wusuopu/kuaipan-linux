#!/usr/bin/env python
#-*- coding:utf-8 -*-
## 
#  Copyright (C) 
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation.
# 本程序是免费软件，基于GPL许可发布。
# 
##
# @文件名(file): kuaipan.py
# @作者(author): 龙昌锦(LongChangjin)
# @博客(blog): http://www.xefan.com
# @邮箱(mail): admin@xefan.com
# @QQ: 346202141
# @时间(date): 2012-06-16
# 



import oauth.oauth
import os.path
from sys import argv
import webbrowser
from client import KuaipanAPI
from session import KuaipanSession

class Kuaipan:
    _consumer_key = "xcAA77bSrR1XERec"
    _consumer_secret = "HqOtBOyuPFIkYrGo"
    
    def __init__(self, app_type="kuaipan"):
        sess = KuaipanSession(self._consumer_key, self._consumer_secret, app_type)
        self.api = KuaipanAPI(sess)
        if os.path.exists('.token'):
            fp = open('.token', 'rb')
            key = fp.readline()
            secret = fp.readline()
            fp.close()
            sess.token = oauth.oauth.OAuthToken(key[:-1], secret[:-1])
        ret = self.account_info()
        if ret != False:
            print(u"%s 登陆成功..\n" % ret['user_name'])
            print(u"\t用户总空间：%dM" % (ret['quota_total']/1024/1024))
            print(u"\t已使用空间：%dM" % (ret['quota_used']/1024/1024))
            print(u"\t允许上传最大文件：%dM" % (ret['max_file_size']/1024/1024))
            print("--------------------------------------\n")
            return
        url = self.api.requestToken()
        print(u"如果没有自动访问的话，请将下面链接复制到浏览器中。\n%s" % url)
        webbrowser.open(url)
        print(u"使用上面链接登陆成功后按回车键继续..")
        raw_input()
        self.api.accessToken()
        fp = open('.token', 'wb')
        fp.write(sess.token.key + '\n')
        fp.write(sess.token.secret + '\n')
        fp.close()
    #获取用户信息
    def account_info(self):
        try:
            ret = self.api.account_info()
        except Exception, e:
            #print e
            return False
        return ret

    #获取文件（夹）信息
    def metadata(self, path):
        try:
            ret = self.api.metadata(path)
        except Exception, e:
            print e
            return False
        return ret

    #获取文件分享链接
    def shares(self, path):
        try:
            ret = self.api.shares(path)
        except Exception, e:
            print e
            return ''
        return ret['url']

    #创建文件夹
    def create_folder(self, name):
        try:
            ret = self.api.create_folder(name)
        except Exception, e:
            print e
            return False
        #print(u"file_id:%s" % (ret['file_id']))
        return ret['file_id']

    #删除文件（夹）
    def delete(self, name, to_recycle=True):
        try:
            ret = self.api.delete(name, to_recycle)
        except Exception, e:
            print e
            return False

    #移动文件（夹）
    def move(self, from_path, to_path):
        try:
            ret = self.api.move(from_path, to_path)
        except Exception, e:
            print e
            return False

    #复制文件（夹）
    def copy(self, from_path, to_path):
        try:
            ret = self.api.copy(from_path, to_path)
        except Exception, e:
            print e
            return False
        return ret['file_id']

    #上传文件
    def upload_file(self, path, file_name, bin=True, overwrite=True):
        if bin and not os.path.exists(file_name):
            print(u"%s 文件不存在！" % (file_name))
            return False
        try:
            if bin:
                ret = self.api.upload_file(path, open(file_name,'rb'), overwrite)
            else:
                ret = self.api.upload_file(path, file_name, overwrite)
        except Exception, e:
            print e
            return False
        print ret

    #下载文件
    def download_file(self, path):
        try:
            ret = self.api.download_file(path)
        except Exception, e:
            print e
            return False
        return ret

    #获取缩略图
    def thumbnail(self, path, width, height, save_as):
        try:
            ret = self.api.thumbnail(path, width, height)
        except Exception, e:
            print e
            return False
        fp = open(save_as, 'wb')
        fp.write(ret)
        fp.close()

    #文档转换
    def document_view(self, path, file_type, save_as, view='normal', is_zip=0):
        try:
            ret = self.api.document_view(path, view, file_type, is_zip)
        except Exception, e:
            print e
            return False
        fp = open(save_as, 'wb')
        fp.write(ret)
        fp.close()

if __name__ == "__main__":
    if len(argv) == 2 and argv[1] == "clean":
        if os.path.exists('.token'):
            os.unlink('.token')
        exit(0)
    try:
        kp = Kuaipan()
    except Exception, e:
        print e
        exit(1)
    ret = kp.account_info()
    print(u"%s 登陆成功..\n\t个人信息：" % ret['user_name'])
    print(u"\t用户总空间：%dM" % (ret['quota_total']/1024/1024))
    print(u"\t已使用空间：%dM" % (ret['quota_used']/1024/1024))
    print(u"\t允许上传最大文件：%dM" % (ret['max_file_size']/1024/1024))
    print("--------------------------------------\n")
    #kp.metadata("/clim.in")
    #kp.shares("slim.conf")
    #kp.create_folder("test/t1")
    #kp.delete('test')
    #kp.move('slim.conf', 'test/clim')
    #kp.copy('test/clim', 'clim.in')
    #kp.upload_file('all.js', 'all.js')
    #kp.download_file('kp_demo.py')
    #kp.thumbnail('lcarch.png', 300, 400, 'test.jpg')
    #kp.document_view('from.txt', 'txt', 'from.html')
