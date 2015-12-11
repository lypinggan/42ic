# -*- coding: utf-8 -*-
import random, string, time, os
import Image
from flask import Module, url_for, \
    redirect, g, flash, request, current_app as app, abort, session as s, jsonify


from iapp.extensions import mail, db, cache
from iapp.helpers import render_template
from iapp.utils.online import is_login
from iapp.decorators import keep_login_url
from iapp.models import Attachment
from iapp.utils.pic import Graphics, WriteText
upload = Module(__name__)

'''
验证是否为图片文件
'''
IMG_EXTENSIONS = set( ['bmp', 'png', 'jpg', 'jpeg', 'gif', 'BMP', 'PNG', 'JPG', 'JPEG', 'GIF'] )
def file_is_img(filename):
    return '.' in filename and \
        filename.rsplit( '.', 1 )[1] in IMG_EXTENSIONS

'''
验证文件类型
'''
UPFILE_EXTENSIONS = set( ['bmp', 'png', 'jpg', 'jpeg', 'gif', 'BMP', 'PNG', 'JPG', 'JPEG', 'GIF','pdf','PDF','rar','RAR','zip','7z'] )
def allowed_file( filename ):
    return '.' in filename and \
        filename.rsplit( '.', 1 )[1] in UPFILE_EXTENSIONS

'''
文件上传
'''
@upload.route( "", methods=("GET", "POST") )
def upload_file():
    is_login()
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1#如果没有指定就默认为第一页
        
    if request.method == 'POST':
        file = request.files['upfile']
        if allowed_file( file.filename ):
            tmp = str(random.randrange(0,9))#0-9是随机的目录
            filename = tmp+'/42ic.com-'+ str( int(time.time()) ) + "." + file.filename.rsplit( '.', 1 )[1]
            #存放原始文件
            file.save( os.path.join( app.config['UPFILE_PATH'], filename ) )
            filesize = os.path.getsize( app.config['UPFILE_PATH']+ filename)
            #如果是图片文件，就生成两组小图
            if file_is_img(file.filename):
                im = Image.open( app.config['UPFILE_PATH'] + "/" + filename ).convert("RGB")
                #大图也加一个水印
                im_artwork = im.copy()
                WriteText(im_artwork, 'www.42ic.com', os.path.join( app.config['UPFILE_PATH']+'artwork/', filename ))
                #生成2组小图并加水印
                i = Graphics(im, app.config['UPFILE_PATH'],filename);
                i.run_thumb_all([200,400],[540,1000]);
            a = Attachment( g.user.id, file.filename.rsplit( '.', 1 )[1],\
                 filesize, file.filename, filename)
            db.session.add( a )
            db.session.commit()
            flash(u"上传成功。", "success")
    file_list = Attachment.query.filter(Attachment.user_id==g.user.id).\
                order_by(Attachment.id.desc()).paginate(page, per_page=10)
    page_url = lambda page: '?page='+str(page)
    return render_template("upload.html",file_list=file_list,page_url=page_url)

'''
下载文件
需要用户登陆才能下载
'''
@upload.route( "/download/<int:aid>", methods=("GET", "POST") )
def download_file(aid):
    is_login()
    a = Attachment.query.get_or_404(aid)
    #下载计数统计
    a.num_down = a.num_down + 1
    db.session.commit()
    #返回文件URL
    return redirect(app.config['UPFILE_URL']+a.file_new_name)
