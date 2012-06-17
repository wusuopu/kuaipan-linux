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
# @文件名(file): main.py
# @作者(author): 龙昌锦(LongChangjin)
# @博客(blog): http://www.xefan.com
# @邮箱(mail): admin@xefan.com
# @QQ: 346202141
# @时间(date): 2012-06-16
# 


from kuaipan import Kuaipan
import fuse
import stat
import errno
import sys
import time
import thread
import os

class KP_fs(fuse.LoggingMixIn, fuse.Operations):
    def __init__(self, app_type="kuaipan"):
        self.kp = Kuaipan(app_type)
        self.now = time.time()
        print(u"获取文件列表...")
        self.all_dir = []
        self.get_ok = False
        thread.start_new_thread(self.walk, ())
        while not self.get_ok:
            time.sleep(1)

    #5分钟遍历一次列表
    def walk(self):
        while True:
            self.all_dir = self.walk_recursion("/")
#            print self.all_dir
            if not self.get_ok:
                self.get_ok = True
            print(u"文件列表获取成功")
            time.sleep(300)
    def get_list(self, path):
        dir_list = self.kp.metadata(path)
        return dir_list['files']
    def walk_recursion(self, path):
        data_list = self.get_list(path)
        for d_list in data_list:
            if d_list['type'] == "folder":
                d_list['files'] = self.walk_recursion(path + d_list['name'])
        return data_list
    #文件属性
    def getattr(self, path, fh=None):
#        print("getattr path:%s" % path)
        if path == '/':
            st = dict(st_mode=(stat.S_IFDIR|0644), st_nlink=2)
            st['st_ctime'] = st['st_mtime'] = st['st_atime'] = self.now
            return st

        path = os.path.normpath(path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        path_list = dirname.split('/')
        deep = len(path_list)
        i = 1
        c_list = self.all_dir
        while i < deep:
            for d_list in c_list:
                if path_list[i] == d_list['name']:
                    c_list = d_list['files'] if d_list.has_key('files') else []
                    break
            i += 1
        for d_list in c_list:
            if basename == d_list['name']:
                if d_list['type'] == "folder":
                    st = dict(st_mode=(stat.S_IFDIR|0644), st_nlink=2)
                else:
                    st = dict(st_mode=(stat.S_IFREG|0644), st_size=d_list['size'])
                st['st_ctime'] = time.mktime(time.strptime(d_list['create_time'], "%Y-%m-%d %H:%M:%S"))
                st['st_mtime'] = st['st_atime'] = time.mktime(time.strptime(d_list['modify_time'], "%Y-%m-%d %H:%M:%S"))
                return st
#        print("getattr:path %s not exists!" % path)
        raise fuse.FuseOSError(errno.ENOENT)
    #文件列表
    def readdir(self, path, fh):
#        print("readdir path:%s" % path)
        data = ['.', '..']
        if path == '/':
            for d_list in self.all_dir:
                data.append(d_list['name'])
            return data
        path_list = path.split('/')
        deep = len(path_list)
        i = 1
        c_list = self.all_dir
        while i < deep:
            for d_list in c_list:
                if path_list[i] == d_list['name']:
                    c_list = d_list['files'] if d_list.has_key('files') else []
                    break
            i += 1
        for d_list in c_list:
            data.append(d_list['name'])
        return data
    #重命名/移动文件
    def rename(self, old, new):
        print("rename old:%s  new:%s" % (old, new))
        self.kp.move(old, new)
        self.all_dir = self.walk_recursion("/")
    #创建目录
    def mkdir(self, path, mode=0644):
        print("mkdir path:%s" % path)
        self.kp.create_folder(path)
        self.all_dir = self.walk_recursion("/")
    #删除目录
    def rmdir(self, path):
        print("del path:%s" % path)
        self.kp.delete(path)
        self.all_dir = self.walk_recursion("/")
    #删除文件
    unlink = rmdir
    #读文件
    def read(self, path, size, offset, fh):
        print("read: %s %d %d" % (path, size, offset))
        return self.kp.download_file(path).read(size)
    #写文件
    def write(self, path, data, offset, fh):
        print("read: %s" % (path))
        self.kp.upload_file(path, data, False)
        self.all_dir = self.walk_recursion("/")
        return len(data)
    #创建文件
    def create(self, path, mode=0644, fi=None):
        print("create %s" % path)
        self.kp.upload_file(path, '', False)
        self.all_dir = self.walk_recursion("/")
        return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <point>" % sys.argv[0])
        exit(1)
    print(u"|--------------------------------------------------")
    print(u"|\t\t\t金山快盘文件系统             ")
    print(u"|\t作者：龙昌                          ")
    print(u"|\t博客：http://www.xefan.com             ")
    print(u"|\t邮箱：admin@xefan.com                   ")
    print(u"|--------------------------------------------------")
    fuse = fuse.FUSE(KP_fs("app_folder"), sys.argv[1], foreground=True)
