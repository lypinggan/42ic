# -*- coding: utf-8 -*-
import uuid
import time
import os
import random, string
from flask import Module, flash, request, g, current_app, \
    abort, redirect, url_for, session ,jsonify

from flaskext.mail import Message
from flaskext.babel import gettext as _
from flaskext.principal import identity_changed, Identity, AnonymousIdentity

from iapp.utils.jsonify import jsonify as json2
from iapp.utils.public_fun import send_msg
from iapp.models import *
from iapp.helpers import render_template, md5
from iapp.extensions import db, mail
from iapp.utils.online import is_login

iadmin = Module(__name__)
def is_admin():
    if g.user:
        if not g.user.role>=300:
            abort(404)
    else:
        abort(404)
'''
后台首页
'''
@iadmin.route("/", methods=("GET", "POST"))
def index(page=1):
    is_admin()
    return render_template("/admin/index.html")
'''
用户管理
'''
@iadmin.route("/user/", methods=("GET", "POST"))
def user():
    is_admin()
    user_list = User.query.order_by(User.id.desc()).all()
    
    return render_template("/admin/user_index.html",user_list = user_list)

'''
小组申请管理
'''
@iadmin.route("/group_requisition/", methods=("GET", "POST"))
def group_requisition():
    is_admin()
    action = request.args.get("action", '').strip()
    #如果通过申请
    if action == 'pass':
        id = int(request.args.get("id", '').strip())
        gr = Group_Requisition.query.get_or_404(id)
        group = Group(gr.name,gr.url_name,gr.author_id,gr.description)
        gr.status = 1
        send_msg(gr.author_id,u'小组申请通过',u'恭喜您，您所申请的'+gr.name+u'小组已经通过审核。去http://www.42ic.com/group/'+gr.url_name+u',看看吧')
        db.session.add( group )
        db.session.commit()
        #申请人自动加入
        group_user = Group_User(group.id,gr.author_id)
        db.session.add( group_user )
        db.session.commit()
        return redirect(url_for("admin.group_requisition"))
    if action == 'refusal':
        id = int(request.args.get("id", '').strip())
        gr = Group_Requisition.query.get_or_404(id)
        gr.status = 2
        send_msg(gr.author_id,u'小组申请失败',u'对不起，您申请的小组'+gr.name+u'资料不全，未能通过审核')
        db.session.commit()
        return redirect(url_for("admin.group_requisition"))
    req_list = Group_Requisition.query.order_by(Group_Requisition.status).all()
    #send_msg(1,'hi','lyping')
    return render_template("/admin/group_requisition.html",req_list = req_list)
