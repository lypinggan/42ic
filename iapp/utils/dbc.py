# -*- coding: utf-8 -*-
"""
数据中心
"""
import re
from StringIO import StringIO
from flask import request, url_for, current_app as app
from iapp.models import Attachment
from iapp.extensions import cache


'''
获取附件数据
如果是图片，则直接显示
如果是文件，则提供链接下载

参数内容如
[file]123[/file]
'''
def get_attachment_file_url(value):

    r = re.compile(r'\[file\](\d+)\[/file\]')
    #获取ID号
    p = r.findall(value.group())
    if cache.get('get_Attachment'+p[0]):
        return cache.get('get_Attachment'+p[0])
    else:
        a = Attachment.query.filter(Attachment.id == p[0] ).first()
        if a:
            if a.type_no == 1:#如果文件类型等于1则为图片，其他为非显示的文件
                html = u'<a href="%s" title="%s"><img src="%s"></a>' % \
                (app.config['UPFILE_URL']+'artwork/'+a.file_new_name,\
                a.file_old_name, app.config['UPFILE_URL']+'540/'+a.file_new_name)
            else:
                if a.file_size >1048576:
                    filesize = str(a.file_size/1048576)+'MB'
                elif a.file_size >1024:
                    filesize = str(a.file_size/1024)+'KB'
                else:
                    filesize = str(a.file_size)+'B'
                html = u'附件ID%s:<a href="%s">%s</a>(%s)' % \
                (p[0], url_for('upload.download_file',aid = p[0]), a. file_old_name,filesize)
            cache.set('get_Attachment'+p[0],html,5000)
            return html
        else:
            cache.set('get_Attachment'+p[0],'',5000)
            return ''
'''
获取预览方式的文件
'''
def get_mini_attachment_file_url(value):

    r = re.compile(r'\[file\](\d+)\[/file\]')
    #获取ID号
    p = r.findall(value.group())
    if cache.get('get_mini_Attachment'+p[0]):
        return cache.get('get_mini_Attachment'+p[0])
    else:
        a = Attachment.query.filter(Attachment.id == p[0] ).first()
        if a:
            if a.type_no == 1:#如果文件类型等于1则为图片，其他为非显示的文件
                html = u'<img src="%s">' % (app.config['UPFILE_URL']+'200/'+a.file_new_name)
            else:
                if a.file_size >1048576:
                    filesize = str(a.file_size/1048576)+'MB'
                elif a.file_size >1024:
                    filesize = str(a.file_size/1024)+'KB'
                else:
                    filesize = str(a.file_size)+'B'
                html = u'附件ID%s:<a href="%s">%s</a>(%s)' % \
                (p[0], url_for('upload.download_file',aid = p[0]), a. file_old_name,filesize)
            cache.set('get_mini_Attachment'+p[0],html,5000)
            return html
        else:
            cache.set('get_mini_Attachment'+p[0],'',5000)
            return ''
