# -*- coding: utf-8 -*-
import uuid
import time
import os
import random, string
from flask import Module, flash, request, g, current_app as app, \
    abort, redirect, url_for, session, jsonify

from flaskext.mail import Message
from flaskext.babel import gettext as _
from flaskext.principal import identity_changed, Identity, AnonymousIdentity


from iapp.forms import ChangePasswordForm, EditAccountForm, \
    DeleteAccountForm, LoginForm, SignupForm, RecoverPasswordForm, EditNameCardForm
from iapp.models import User,Users_icon
from iapp.helpers import render_template, md5
from iapp.extensions import db, mail, cache
from iapp.utils.online import is_login
from iapp.utils.pic import picopen, pic_square
from iapp.utils.public_fun import send_msg
from iapp.utils import Queue

queue = Queue()


'''
账户首页
自动跳转资料页面
'''
account = Module(__name__)
@account.route("/")
def home():
    return redirect(url_for("account.profile"))
    
'''
账户登录
登录后跳转首页
'''  
@account.route("/login/", methods=("GET", "POST"))
def login():
    form = LoginForm(login=request.args.get("login", None),
                     next=request.args.get("next", None))
    # TBD: ensure "next" field is passed properly
    if form.validate_on_submit():
        user, authenticated = User.query.authenticate(form.login.data,form.password.data)
        if user and authenticated:
            session['user_id'] = user.id
            flash(u"欢迎回来", "success")
            next_url = form.next.data
            if not next_url or next_url == request.path:
                next_url = url_for('frontend.index')
            #清除缓存
            cache.delete('session_login_uid_'+str(session['user_id'])) 
                
            return redirect(next_url)
        else:
            time.sleep(3)#安全性延时
            flash(u"对不起，登陆出错", "error")
    return render_template("account/login.html", form=form)
'''
用户注册
'''
@account.route("/signup/", methods=("GET", "POST"))
def signup():
    form = SignupForm(next=request.args.get("next"))
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.reg_ip = request.remote_addr
        db.session.add(user)
        user_icon = Users_icon()
        db.session.commit()
        user_icon.uid = user.id
        db.session.add(user_icon)
        #默认姓名就是用户名
        user.name = user.username
        
        #广播一下
        queue.push((101,user.id))
        db.session.commit()
        send_msg(user.id,u'欢迎加入42ic.com',u'42ic是一个专注于电子行业的社区网站，欢迎您的加入！')
        flash(u"您已经注册成功！请登陆", "success")
        next_url = form.next.data
        if not next_url or next_url == request.path:
            next_url = url_for('account.login')
        #print('OK')
        return redirect(next_url)

    return render_template("account/signup.html", form=form)

'''
账户退出
＠需要账户登录
'''
@account.route("/logout/")
def logout():
    is_login()
    session.pop('user_id', None)
    flash(u"你现在已经登出!", "success")
    return redirect(url_for('account.login'))

'''
找回密码
提交邮箱地址后会将新的随机密码发到其邮箱中
'''
@account.route("/forgotpassword/", methods=("GET", "POST"))
def forgot_password():
    form = RecoverPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(u"临时登陆密码已发至"+form.email.data+u",请注意查收", "success")
            new_password = string.join( random.sample( ['a', 'b', 'c', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'm',
                                         'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                                         '2', '3', '5', '6', '7', '8'], 6 ) ).replace( " ", "" )
            user.password = new_password
            db.session.commit()
            body = render_template("emails/recover_password.html",
                                   new_password=new_password)
            message = Message(subject=u"42ic.com临时登陆密码",
                              body=body,
                              recipients=[user.email])
            mail.send(message)
            
            return redirect(url_for("frontend.index"))
        else:

            flash(u"对不起,您的邮箱地址不存在", "error")

    return render_template("account/recover_password.html", form=form)

'''
密码修改
＠需要账户登录
'''
@account.route("/changepass/", methods=("GET", "POST"))
def change_password():
    is_login()
    user = None
    if g.user:
        user = User.query.filter_by( id = g.user.id ).first()
    elif 'activation_key' in request.values:
        user = User.query.filter_by(
            activation_key=request.values['activation_key']).first()
    
    if user is None:
        abort(403)

    form = ChangePasswordForm(activation_key=user.activation_key)

    if form.validate_on_submit():

        user.password = form.password.data
        user.activation_key = None
        db.session.commit()
        #登出
        session.pop('user_id', None)

        flash(u"密码修改成功，请重新登录。", "success")
        #清除缓存
        cache.delete('session_login_uid_'+str(session['user_id']))         
        return redirect(url_for("account.login"))

    return render_template("account/change_password.html", form=form)
        
'''
资料修改
＠需要账户登录
'''
@account.route("/profile/", methods=("GET", "POST"))
def profile():
    is_login()
    form = EditAccountForm(g.user)

    if form.validate_on_submit():
        userinfo = User.query.filter_by( id = g.user.id ).first()
        form.populate_obj(userinfo)
        db.session.commit()
        flash(u'资料已经更新', "success")
        #清除缓存
        cache.delete('session_login_uid_'+str(session['user_id']))         
        return redirect(url_for("account.profile"))
    return render_template("account/edit_account.html", form=form)
'''
名片修改
＠需要账户登录
'''
@account.route("/namecard/", methods=("GET", "POST"))
def namecard():
    is_login()
    form = EditNameCardForm(g.user)

    if form.validate_on_submit():
        userinfo = User.query.filter_by( id = g.user.id ).first()
        form.populate_obj(userinfo)
        db.session.commit()
        flash(u'资料已经更新', "success")
        #清除缓存
        cache.delete('session_login_uid_'+str(session['user_id']))         
        return redirect(url_for("account.namecard"))
    return render_template("account/edit_namecard.html", form=form)
'''
@account.route("/delete/", methods=("GET", "POST"))
@auth.require(401)
def delete():
    # confirm password & recaptcha
    form = DeleteAccountForm()
    if form.validate_on_submit():
        db.session.delete(g.user)
        db.session.commit()
        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())

        flash(u"您的帐号已经被注销", "success")

        return redirect(url_for("frontend.index"))

    return render_template("account/delete_account.html", form=form)

'''

'''
编辑头像
＠需要账户登录
'''
@account.route( "/user_icon", methods = ['GET', 'POST'] )
def user_icon():
    is_login()
    if request.method == 'POST':
        xyh = request.form['imgpos'].split('_')
        ed_icon = Users_icon.query.filter_by( uid = g.user.id ).first()
        ed_icon.x = x = int(xyh[0])
        ed_icon.y = y = int(xyh[1])
        ed_icon.h = h = int(xyh[2])
        db.session.commit()
        #处理图片并保存
        import Image
        im = Image.open( app.config['AVATAR_IMAGE_PATH'] + "/" + ed_icon.image_name )
        box = (x,y,x+h,y+h)
        #裁剪图片
        image = im.crop(box)
        #缩略图片
        image2 = pic_square( image, 48)
        del image
        tmp = str(random.randrange(0,9))
        filename = tmp+'/'+str( g.user.id ) + "-" + str( int(time.time()) ) + "." + ed_icon.image_name.rsplit( '.', 1 )[1]
        image2.save( os.path.join( app.config['AVATAR_PATH'], filename ) )
        #更新用户资料
        ed_user = User.query.filter_by( id = g.user.id ).first()
        ed_user.avatar = filename
        db.session.commit()
        flash(u"头像编辑成功。", "success")
        #清除缓存
        cache.delete('session_login_uid_'+str(session['user_id']))         
    d = {}
    ed_icon = Users_icon.query.filter_by( uid = g.user.id ).first()
    d['icon_image_url'] = "avatar/image/" + ed_icon.image_name
    d['icon_x'] = ed_icon.x
    d['icon_y'] = ed_icon.y
    d['icon_h'] = ed_icon.h
    return render_template( 'account/user_icon.html',**d)

'''
验证文件类型
'''

ALLOWED_EXTENSIONS = set( ['bmp', 'png', 'jpg', 'jpeg', 'gif', 'BMP', 'PNG', 'JPG', 'JPEG', 'GIF'] )

def allowed_file( filename ):
    return '.' in filename and \
        filename.rsplit( '.', 1 )[1] in ALLOWED_EXTENSIONS
'''
上传图片
＠需要账户登录
'''
@account.route( "/user_icon_up_file", methods = ['GET', 'POST'] )
def user_icon_up_file():
    is_login()
    file = request.files['picfile']
    if g.user and file and allowed_file( file.filename ):
        #user = session.query( Users_icon ).filter_by( uid = uid ).first()
        #0-9是随机的目录
        tmp = str(random.randrange(0,9))
        filename = tmp+'/'+str( g.user.id ) + "-" + str( int(time.time()) ) + "." + file.filename.rsplit( '.', 1 )[1]
        file.save( os.path.join( app.config['AVATAR_IMAGE_PATH'], filename ) )
        try:
            ed_icon = Users_icon.query.filter_by( uid = g.user.id ).first()
        except:
            ed_icon = Users_icon()
        ed_icon.image_name = filename
        import Image
        iconname = str( g.user.id ) + "-"+ str( int(time.time()) ) + file.filename.rsplit( '.', 1 )[1]
        im = Image.open( image_path + "/" + filename )
        image2 = pic_square( im, 48 )
        image2.save( os.path.join( app.config['AVATAR_PATH'], filename ) )
        ed_user = User.query.filter_by( id = g.user.id ).first()
        ed_user.avatar = filename
        db.session.commit()
        flash(u"图片上传成功，请编辑头像。", "success")
        #清除缓存
        cache.delete('session_login_uid_'+str(session['user_id']))         
    return redirect(url_for("account.user_icon") )
