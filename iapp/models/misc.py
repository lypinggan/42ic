# -*- coding: utf-8 -*-
import hashlib

from datetime import datetime

from werkzeug import generate_password_hash, check_password_hash, \
    cached_property

from flaskext.sqlalchemy import BaseQuery
from flaskext.principal import RoleNeed, UserNeed, Permission

from iapp.extensions import db
from iapp.permissions import null
from iapp.models.permissions import Permissions




'''
验证是否为图片文件
'''
IMG_EXTENSIONS = set( ['bmp', 'png', 'jpg', 'jpeg', 'gif', 'BMP', 'PNG', 'JPG', 'JPEG', 'GIF'] )
def file_is_img(filename):
    return '.' in filename and \
        filename.rsplit( '.', 1 )[1] in IMG_EXTENSIONS
ZIP_EXTENSIONS = set( ['rar', 'RAR', 'zip', 'ZIP', '7z', '7Z'] )
def file_is_zip(filename):
    return '.' in filename and \
        filename.rsplit( '.', 1 )[1] in ZIP_EXTENSIONS
PDF_EXTENSIONS = set( ['pdf', 'PDF'] )
def file_is_pdf(filename):
    return '.' in filename and \
        filename.rsplit( '.', 1 )[1] in PDF_EXTENSIONS
def file_type_no(filename):
    if file_is_img(filename):
        return 1
    elif file_is_zip(filename):
        return 2
    elif file_is_pdf(filename):
        return 3
    else:
        return 0
class AttachmentQuery(BaseQuery):
    def all_list(self):
        return self.order_by(Upload_File.id.desc())

'''
附件上传记录
'''
class Attachment(db.Model):
    
    __tablename__ = "attachment"
    query_class = AttachmentQuery

    id = db.Column(db.Integer, primary_key=True)
    
    #发生时间
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    #上传者ID
    user_id = db.Column(db.Integer)

    #文件后缀
    file_type = db.Column(db.String(20),default=u'')
    
    file_size = db.Column(db.Integer)
    #是否为图片
    type_no = db.Column(db.Integer, default=0) #1=图片；2=压缩包；3：PDF
    num_down = db.Column(db.Integer,default=0)
    #文件名字
    file_old_name = db.Column(db.String(250),default=u'')
    
    file_new_name = db.Column(db.String(250),default=u'')

    def __init__(self, user_id, file_type, file_size, file_old_name, file_new_name):
        self.user_id = user_id
        self.file_type = file_type
        self.type_no = file_type_no( file_old_name )
        self.file_size = file_size
        self.file_old_name = file_old_name
        self.file_new_name = file_new_name
