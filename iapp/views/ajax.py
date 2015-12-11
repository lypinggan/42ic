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
from iapp.models import User,Users_icon, Question, Question_Follow,\
                    Question_Votes,Answer_Comment,User_Follow,Event,Event_User
from iapp.helpers import render_template, md5
from iapp.extensions import mail, db, cache
from iapp.utils.online import is_login
from iapp.utils.public_fun import send_msg
from iapp.utils import Queue

queue = Queue()

ajax = Module(__name__)
'''
获取用户登录信息：
如果登录=返回用户相关信息
如果未登录=ID返回0
'''
@ajax.route("/user_init/<slug>")
def user_init(slug):
    if g.user:
        return jsonify( id = g.user.id, username = g.user.username, role = g.user.role, icon = url_for('.static', filename= "avatar/"+g.user.avatar) )
    else:
        return jsonify( id = 0 )
'''
页面提示信息获取
每次打开页面都会获取一次
'''
@ajax.route("/messages/<slug>")
def messages(slug):
    return render_template("ajax/messages.html")


'''
浏览一次问题
增加一次访问记录
返回：
uid:用户ID
answer_permissions:是否有权限解答
num_follow：关注人数
num_votes:喜欢的人数
is_follow:我是否关注
is_votes:我是否喜欢
'''
@ajax.route("/question_view/<int:question_id>/<slug>")
def question_view( question_id, slug ):
    question = Question.query.get_or_404(question_id)
    question.views = question.views + 1
    db.session.commit()
    uid, answer_permissions, num_follow, num_votes, is_follow, is_votes = 0,0,0,0,0,0
    if g.user:
        uid = g.user.id
        if g.user.role < 100 :
            answer_permissions = 0
        else:
            answer_permissions = 1
        if Question_Follow.query.is_following( question_id, g.user.id ):
            is_follow = 1
        if Question_Votes.query.is_voteing( question_id, g.user.id ):
            is_votes = 1        
    return jsonify( uid = uid, answer_permissions = answer_permissions, num_follow = question.num_follow, num_votes = question.votes, is_follow = is_follow, is_votes = is_votes )
'''
问题投票
减少一票
添加问题喜欢关联
'''
@ajax.route("/question_upvote/<int:question_id>/<slug>")
def question_upvote( question_id, slug ):
    question = Question.query.get_or_404(question_id)
    question.votes = question.votes + 1
    question_votes  = Question_Votes( g.user.id, question_id)
    db.session.add( question_votes )
    db.session.commit()
    return jsonify( ok = 1,num_votes = question.votes )
'''
问题取消投票
减少一票
删除问题喜欢关联
'''
@ajax.route("/question_downvote/<int:question_id>/<slug>")
def question_downvote( question_id, slug ):
    question = Question.query.get_or_404(question_id)
    question.votes = question.votes - 1
    Question_Votes.query.filter( Question_Votes.user_id == g.user.id ).filter( Question_Votes.question_id == question_id ).delete()
    db.session.commit()
    return jsonify( ok = 1,num_votes = question.votes )
'''
添加关注
'''
@ajax.route("/question_upfollow/<int:question_id>/<slug>")
def question_upfollow( question_id, slug ):
    question = Question.query.get_or_404(question_id)
    question.num_follow = question.num_follow + 1
    question_follow  = Question_Follow( g.user.id, question_id)
    db.session.add( question_follow )
    db.session.commit()
    queue.push((303,g.user.id,question.id,question.title,question.description[0:100]))#发任务
    return jsonify( ok = 1,num_follow = question.num_follow )
'''
取消关注
'''
@ajax.route("/question_downfollow/<int:question_id>/<slug>")
def question_downfollow( question_id, slug ):
    question = Question.query.get_or_404(question_id)
    question.num_follow = question.num_follow - 1
    Question_Follow.query.filter( Question_Follow.user_id == g.user.id ).filter( Question_Follow.question_id == question_id ).delete()
    db.session.commit()
    return jsonify( ok = 1,num_follow = question.num_follow )

'''
获取答案的评论列表
'''
@ajax.route("/get_answer_comment/<int:answer_id>/<slug>")
def get_answer_comment( answer_id, slug ):
    answer_comment = Answer_Comment.query.filter( Answer_Comment.answer_id == answer_id ).all()
    if answer_comment:
        render_template("ajax/get_answer_comment.html",\
                answer_comment = answer_comment,answer_id=answer_id)
    else:
        return 'no'
'''
提交答案的评论
'''
@ajax.route("/saying_comment", methods=("GET","POST"))
def saying_comment( answer_id, slug ):
    answer_comment = Answer_Comment.query.filter( Answer_Comment.answer_id == answer_id ).all()
    if answer_comment:
        render_template("ajax/get_answer_comment.html",\
                answer_comment = answer_comment,answer_id=answer_id)
    else:
        return 'no'


'''
获取用户关注状态
'''
@ajax.route("/follow_mode/<int:people_id>/<slug>")
def follow_mode( people_id, slug ):
    if g.user:
        is_login = 1;
        user_fo = User_Follow.query.filter(User_Follow.main_id ==  people_id )\
                    .filter(User_Follow.follower_id == g.user.id ).first()
        if user_fo:
            is_follow = 1
        else:
            is_follow = 0
    else:
        is_login = 0;
        is_follow = 0;
    return jsonify( is_login = is_login,is_follow = is_follow )
'''
设置用户关注状态
'''
@ajax.route("/follow_set_mode/<int:people_id>/<slug>")
def follow_set_mode( people_id, slug ):
    if g.user:
        is_login = 1;
        user_fo = User_Follow.query.filter(User_Follow.main_id == people_id )\
                    .filter(User_Follow.follower_id == g.user.id ).first()
        if user_fo:
            User_Follow.query.filter(User_Follow.main_id == people_id ).\
                        filter(User_Follow.follower_id == g.user.id ).delete()
            is_follow = 0
        else:
            uf = User_Follow(people_id,g.user.id)
            db.session.add( uf )
            db.session.commit()
            people = User.query.get_or_404(people_id)
            #消息队列
            queue.push((103,g.user.id,people_id,people.username,people.name))           
            #send_msg(people_id,people.name+u'关注了您',u'<a href="/people/'+apeople.username+u'/">'+apeople.name+u'</a></a>关注了您，快去串个门吧！')
            is_follow = 1
    else:
        is_login = 0;
        is_follow = 0;
    return jsonify( is_login = is_login,is_follow = is_follow )
'''
删除事件
'''
@ajax.route("/event_del/<int:event_id>")
def event_del( event_id ):
    if g.user:
        Event_User.query.filter(Event_User.event_id == event_id ).\
                                filter(Event_User.feed_user_id == g.user.id ).delete()
    return jsonify( ok = 1 )



#动态加载事件内容
@ajax.route("/get_event_more/<viewname>/<int:page>/<slug>", methods=("GET", "POST"))
def get_event_more(viewname,page,slug):

    if viewname == 'all':
        if cache.get('event_list-all-html-page-'+str(page)):
            e_html = cache.get('event_list-all-html-page-'+str(page))
        else:
            a = Event.query.all_list().paginate(page,10)
            e_html = ''
            for e in a.items:
                e_html += render_template( 'event_list.html',e=e)
            cache.set('event_list-all-html-page-'+str(page),e_html,10)
    else:
        if viewname == 'mine':
            event_user_list = Event_User.query.mine_list(g.user.id).paginate(page,10)
        elif viewname == 'talk':
            event_user_list = Event_User.query.talk_list(g.user.id).paginate(page,10)
        elif viewname == 'question':
            event_user_list = Event_User.query.question_list(g.user.id).paginate(page,10)
        elif viewname == 'topic':
            event_user_list = Event_User.query.topic_list(g.user.id).paginate(page,10)
        else:
            abort(404)
        e_html = ''
        #try:
        for eu in event_user_list.items:
            if cache.get('event-id-'+str(eu.event_id)):
                e_html += cache.get('event-id-'+str(eu.event_id))
            else:
                e = Event.query.get(eu.event_id)
                h = render_template('event_list.html',e=e)
                cache.set('event-id-'+str(eu.event_id),h,100)
                e_html += h         
    return e_html

@ajax.route("/!/hello")
@json2
def hello():
    return {'name':'lyping','message':'你好啊'}