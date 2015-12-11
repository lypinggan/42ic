# -*- coding: utf-8 -*-
from flask import Module, url_for, g, redirect, flash,request

from flaskext.mail import Message
from flaskext.babel import gettext as _

from iapp.helpers import render_template, cached
from iapp.models import User,User_Message,User_Follow,Question,Group_Topic
from iapp.decorators import keep_login_url
from iapp.extensions import db, mail, cache
from iapp.utils.online import is_login
'''
用户个人页面
'''
people = Module(__name__)

'''
个人页面首页
'''
@people.route("/<username>/")
@keep_login_url
def index(username):
    viewname = 'profile'
    peopleinfo = User.query.username_get_info(username)
    
    return render_template("people/index.html",peopleinfo=peopleinfo,\
            viewname=viewname)

'''
个人页面-人脉
'''
@people.route("/<username>/contacts")
@keep_login_url
def contacts(username):
    peopleinfo = User.query.username_get_info(username)
    viewname = 'contacts'
    follower = User_Follow.query.filter(User_Follow.main_id == peopleinfo.id).all()
    #我被这些人关注
    follower_list = []
    try:
        for m in follower:
            u = User.query.get(m.follower_id)
            follower_list.append(u)
    except:
        follower_list = None
    main = User_Follow.query.filter(User_Follow.follower_id == peopleinfo.id).all()
    #我关注的人
    main_list = []
    try:
        for m in main:
            u = User.query.get(m.main_id)
            main_list.append(u)    
    except:
        main_list = None
    return render_template("people/contacts.html",peopleinfo=peopleinfo,\
            viewname=viewname,follower_list=follower_list,main_list=main_list)

'''
个人页面-问题
'''
@people.route("/<username>/question")
@keep_login_url
def question(username):
    peopleinfo = User.query.username_get_info(username)
    viewname = 'question'
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1#如果没有指定就默认为第一页    
    question_list = Question.query.filter(Question.author_id == peopleinfo.id)\
                    .filter(Question.deleteed == 0).paginate(page, per_page=Question.PER_PAGE)
    page_url = lambda page: '?page='+str(page)
    return render_template("people/question.html",peopleinfo=peopleinfo,\
            viewname=viewname,question_list=question_list,page_url=page_url)
'''
个人页面-话题
'''
@people.route("/<username>/topic")
@keep_login_url
def topic(username):
    peopleinfo = User.query.username_get_info(username)
    viewname = 'topic'
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1#如果没有指定就默认为第一页    
    topic_list = Group_Topic.query.filter(Group_Topic.author_id == peopleinfo.id)\
                    .filter(Group_Topic.deleteed == 0).paginate(page, per_page=Group_Topic.PER_PAGE)
    page_url = lambda page: '?page='+str(page)

    return render_template("people/topic.html",peopleinfo=peopleinfo,\
            viewname=viewname,topic_list=topic_list,page_url=page_url)

'''
个人页面-通知
'''
@people.route("/<username>/notice")
@keep_login_url
def notice(username):
    if username != g.user.username:
        flash(u'无权访问', "error")
        return redirect("/")
    peopleinfo = User.query.username_get_info(username)
    viewname = 'notece'
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1#如果没有指定就默认为第一页

    page_url = lambda page: '?page='+str(page)
    mymsg = User_Message.query.get_my_list(g.user.id).\
        paginate(page, per_page=50)
    
    return render_template("people/notice.html",peopleinfo=peopleinfo,\
            viewname=viewname,mymsg=mymsg,page_url=page_url)

'''
个人页面-阅读通知
'''
@people.route("/<username>/notice/<int:notice_id>/read")
@keep_login_url
def notice_read(username,notice_id):
    peopleinfo = User.query.username_get_info(username)
    viewname = 'notece'
    msg = User_Message.query.get_or_404(notice_id)
    if msg.unread == 1:
        user = User.query.get_or_404(g.user.id)
        user.unread_message = user.unread_message - 1
        #清除缓存
        cache.delete('session_login_uid_'+str(session['user_id']))        
    msg.unread = 0
    db.session.commit()
    return render_template("people/read_notice.html",peopleinfo=peopleinfo,\
            viewname=viewname,msg=msg)
