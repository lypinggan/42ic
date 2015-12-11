# -*- coding: utf-8 -*-
import uuid
import time
from datetime import datetime
import os
import random, string
from flask import Module, flash, request, g, current_app, \
    abort, redirect, url_for, session, jsonify

from flaskext.mail import Message
from flaskext.principal import identity_changed, Identity, AnonymousIdentity

from iapp.models import *
from iapp.forms import Group_New_TopicForm, Group_Topic_New_ReplyForm,\
                        Group_RequisitionForm,Group_EditForm, Group_Edit_TopicForm
from iapp.helpers import render_template, md5
from iapp.extensions import db, mail, cache
from iapp.utils.online import is_login
from iapp.utils import Queue

queue = Queue()

'''
小组应用
'''
group = Module(__name__)
'''
小组首页
'''
@group.route("/")
@group.route("/<int:page>")
def index():
    #如果没有指定就默认为第一页
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1
    page_url = lambda page: '?page='+str(page)
    #热门小组，按加入人数排序
    hot_group = Group.query.hot_group_list()    
    #按是否登陆来处理
    if g.user:
        topic_list = Group_Topic.query.get_my_list(g.user.id).\
            paginate(page, per_page=30)
        #我加入的小组（近9）
        my_join_group = Group_User.query.my_join_group(g.user.id)
        return render_template( 'group/index.html',\
                topic_list=topic_list, page_url=page_url,\
                hot_group=hot_group,my_join_group=my_join_group)
    else:
        #获取该小组的主题列表
        topic_list = Group_Topic.query.get_all_list().\
                        paginate(page, per_page=30)
        
        return render_template( 'group/no_login_index.html',\
                topic_list=topic_list, page_url=page_url,hot_group=hot_group)
'''
小组公共首页
'''
@group.route("/public")
def public():
    #如果没有指定就默认为第一页
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1
    page_url = lambda page: '?page='+str(page)
    topic_list = Group_Topic.query.get_all_list().\
                    paginate(page, per_page=30)
    #热门小组，按加入人数排序
    hot_group = Group.query.hot_group_list()
    return render_template( 'group/no_login_index.html',\
            topic_list=topic_list, page_url=page_url,hot_group=hot_group)

'''
小组首页-我发起的话题
'''
@group.route("/my_topics")
def my_topics():
    is_login()
    #如果没有指定就默认为第一页
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1
    page_url = lambda page: '?page='+str(page)

    topic_list = Group_Topic.query.get_my_topics_list(g.user.id).\
        paginate(page, per_page=30)
    #我加入的小组（近9）
    my_join_group = Group_User.query.my_join_group(g.user.id)
    return render_template( 'group/my_topics.html',\
            topic_list=topic_list, page_url=page_url,my_join_group=my_join_group)

'''
小组首页-我回应的话题
'''
@group.route("/my_replied_topics")
def my_replied_topics():
    pass

'''
浏览小组
'''
@group.route("/<slug>/")
@group.route("/<slug>/<int:page>")
def group_view(slug, page=1):
    groupinfo = Group.query.urlname_get_info(slug)
    #如果没有指定就默认为第一页
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1
    
    #检查是否有发言权限
    if g.user:
        is_join = Group_User.query.is_join(groupinfo.id,g.user.id)
        if is_join is None:
            is_join = 0
    else:
        is_join = 0
    #最近加入小组的用户(有缓存)
    if cache.get('group-'+slug+'recently_join_user'):
        recently_join_user = cache.get('group-'+slug+'recently_join_user')
    else:
        recently_join_user = Group_User.query.recently_join_user(groupinfo.id)
        cache.set('group-'+slug+'recently_join_user',recently_join_user,600)
    
    #获取该小组的主题列表
    topic_list = Group_Topic.query.get_topic_list(groupinfo.id).\
                    paginate(page, per_page=30)
    page_url = lambda page: '?page='+str(page)
    return render_template( 'group/g_index.html',groupinfo=groupinfo,\
            is_join=is_join,recently_join_user=recently_join_user,\
            topic_list=topic_list, page_url=page_url)


'''
小组新建话题
'''
@group.route("/<slug>/new_topic", methods=("GET", "POST"))
def new_topic(slug):
    is_login()
    groupinfo = Group.query.urlname_get_info(slug)
    is_join = Group_User.query.is_join(groupinfo.id,g.user.id)
    if is_join is None:
        flash(u'您还没有加入小组，无权发言!', "error")
        return redirect(url_for("group.group_view", slug=slug))
    else:
        form = Group_New_TopicForm()
        if form.validate_on_submit():
                group_topic = Group_Topic()
                form.populate_obj(group_topic)
                group_topic.group_id = groupinfo.id
                group_topic.ip = request.remote_addr
                db.session.add(group_topic)
                db.session.commit()
                flash(u'话题发布成功', "success")
                queue.push((501,g.user.id,group_topic.id,group_topic.title[0:30],group_topic.description[0:100]))
                queue.push((202,g.user.id,2))#新建主题增加2积分
                return redirect(url_for("group.topic_view", topic_id=group_topic.id))
        return render_template( 'group/new_topic.html',groupinfo=groupinfo,\
                form=form)
    

'''
浏览主题
'''
@group.route("/topic/<int:topic_id>")
def topic_view(topic_id):
    topic = Group_Topic.query.get_or_404(topic_id)
    groupinfo = Group.query.id_get_info(topic.group_id)
    #如果已经删除,判断是否显示
    if topic.deleteed:
        if topic.author_id == g.user.id or groupinfo.leader_id == g.user.id\
            or g.user.role >=300:
            pass
        else:
            abort(404)
    
    #检查是否有发言权限
    if g.user:
        is_join = Group_User.query.is_join(groupinfo.id,g.user.id)
        if is_join is None:
            is_join = 0
    else:
        is_join = 0
    #如果具有发言权，生成回复表单
    if is_join:
        reply_form = Group_Topic_New_ReplyForm()
    else:
        reply_form = None
    #获取回应列表
    reply_list = Group_Reply.query.get_reply_list(topic_id)
    return render_template( 'group/topic_view.html',groupinfo=groupinfo,\
                topic=topic, reply_form=reply_form, reply_list=reply_list)    
'''
编辑主题
'''
@group.route("/topic/<int:topic_id>/edit", methods=("GET", "POST"))
def topic_edit(topic_id):
    is_login()
    topic = Group_Topic.query.get_or_404(topic_id)
    groupinfo = Group.query.id_get_info(topic.group_id)
    #只有小组管理员或作者有权限修改
    if groupinfo.leader_id == g.user.id or topic.author_id == g.user.id:
        pass
    else:
        flash(u'无权操作！', "error")
        return redirect(url_for("group.topic_view",topic_id=topic_id))
    form = Group_Edit_TopicForm(obj=topic)
    if form.validate_on_submit():
        form.populate_obj(topic)
        db.session.commit()
        flash(u'修改成功！', "success")
        return redirect(url_for("group.topic_view",topic_id=topic_id))
    return render_template('group/edit_topic.html', form = form,topic=topic)
 
'''
删除主题
'''
@group.route("/topic/<int:topic_id>/delete")
def topic_delete(topic_id):
    is_login()
    topic = Group_Topic.query.get_or_404(topic_id)
    groupinfo = Group.query.id_get_info(topic.group_id)
    #只有作者本人或组长才能删除
    if topic.author_id == g.user.id or groupinfo.leader_id == g.user.id:
        topic.deleteed = 1
        db.session.commit()
        flash(u'删除话题成功', "success")
        return redirect(url_for("group.group_view", slug=groupinfo.url_name))
    else:
        flash(u'无权操作!', "error")
        return redirect(url_for("group.topic_view", topic_id=topic_id))
 

'''
回复主题
'''
@group.route("/topic/<int:topic_id>/reply", methods=("GET", "POST"))
def topic_reply(topic_id):
    is_login()
    topic = Group_Topic.query.get_or_404(topic_id)
    groupinfo = Group.query.id_get_info(topic.group_id)
    #检查是否有发言权限
    is_join = Group_User.query.is_join(groupinfo.id,g.user.id)
    if is_join is None:
        is_join = 0
    else:
        is_join = 1
    #如果还么有加入，是不能回复的
    if not is_join:
        flash(u'您还没有加入小组，无权发言!', "error")
        return redirect(url_for("group.group_view", slug=slug))
    
    form = Group_Topic_New_ReplyForm()
    if form.validate_on_submit():
        group_reply = Group_Reply()
        form.populate_obj(group_reply)
        group_reply.topic_id = topic_id
        db.session.add(group_reply)
        #话题回复次数更新
        group_topic = Group_Topic.query.get_or_404(topic_id)
        group_topic.num_comment = group_topic.num_comment + 1
        group_topic.date_last_response  = datetime.now()
        group_topic.sort  = int(time.time())#用于排序
        db.session.commit()
        flash(u'话题回复成功', "success")
        queue.push((502,g.user.id,topic_id,group_topic.title[0:30],group_reply.content[0:100]))
        queue.push((202,g.user.id,1))#回复主题增加1积分
        return redirect(url_for("group.topic_view", topic_id=topic_id))
    else:
        return redirect(url_for("group.topic_view", topic_id=topic_id))
'''
删除回复
'''
@group.route("/topic-reply/<int:reply_id>/delete")
def topic_reply_delete(reply_id):
    is_login()
    reply = Group_Reply.query.get_or_404(reply_id)
    topic = Group_Topic.query.get_or_404(reply.topic_id)
    groupinfo = Group.query.id_get_info(topic.group_id)
    #只有作者本人或组长才能删除
    if topic.author_id == g.user.id or groupinfo.leader_id == g.user.id\
        or reply.author_id == g.user.id or g.user.role >=300:
        reply.deleteed = 1
        topic.num_comment = topic.num_comment - 1
        db.session.commit()
        flash(u'删除回复成功', "success")
        return redirect(url_for("group.topic_view", topic_id=reply.topic_id))
    else:
        flash(u'无权操作!', "error")
        return redirect(url_for("group.topic_view", topic_id=reply.topic_id))
 



'''
申请小组
'''
@group.route("/new_group", methods=("GET", "POST"))
def new_group():
    is_login()
    form = Group_RequisitionForm()
    if form.validate_on_submit():
        group_requisition = Group_Requisition()
        form.populate_obj(group_requisition)
        db.session.add(group_requisition)
        db.session.commit()
        flash(u'申请提交成功,审核通过后会站内信息通知您', "success")
        return redirect(url_for("group.index"))
    return render_template('group/new_group.html', form = form)
'''
编辑小组资料
'''
@group.route("/<slug>/edit_group", methods=("GET", "POST"))
def edit_group(slug):
    is_login()
    group = Group.query.urlname_get_info(slug)
    form = Group_EditForm(obj=group)
    #判断权限
    if group.leader_id != g.user.id:
        flash(u'对不起，您无权操作！', "error")
        return redirect(url_for("group.group_view",slug=slug))
    if form.validate_on_submit():
        form.populate_obj(group)
        try:
            file = request.files['group_icon']
        except:
            file = None        
        #获取图标文件
        if file:
            image_path = '/home/lyping/data/42ic/' + 'iapp/static/groupicon/image'
            icon_path = '/home/lyping/data/42ic/' + 'iapp/static/groupicon'
            ALLOWED_EXTENSIONS = set( ['bmp', 'png', 'jpg', 'jpeg', 'gif', 'BMP', 'PNG', 'JPG', 'JPEG', 'GIF'] )            
            #存储原文件
            filename = str( group.id ) + "-" + str( int(time.time()) ) + "." + file.filename.rsplit( '.', 1 )[1]
            file.save( os.path.join( image_path, filename ) )
            #产生缩略图
            import Image
            from iapp.utils.pic import picopen, pic_square
            iconname = str( group.id ) + "-"+ str( int(time.time()) ) + file.filename.rsplit( '.', 1 )[1]
            im = Image.open( image_path + "/" + filename )
            image2 = pic_square( im, 48 )
            image2.save( os.path.join( icon_path, filename ) )
            #存储图标名称
            group.group_icon_url = filename
        db.session.commit()
        flash(u'资料修改成功！', "success")
        return redirect(url_for("group.group_view",slug=slug))
    return render_template('group/edit_group.html', form = form,group=group)


'''
申请加入小组
'''
@group.route("/<slug>/join", methods=("GET", "POST"))
def group_join(slug):
    is_login()
    groupinfo = Group.query.urlname_get_info(slug)
    is_join = Group_User.query.is_join(groupinfo.id,g.user.id)
    if not is_join:
        group_user = Group_User(groupinfo.id,g.user.id)
        db.session.add(group_user)
        #小组成员人数+1
        groupinfo.num_members = groupinfo.num_members + 1
        db.session.commit()
        queue.push((503,g.user.id,groupinfo.id,groupinfo.url_name,groupinfo.name[0:30],groupinfo.description[0:100]))
        flash(u'成功加入小组', "success")
    else:
        flash(u'已经加入了这个小组', "error")
    return redirect(url_for("group.group_view", slug=groupinfo.url_name))
'''
申请退出小组
'''
@group.route("/<slug>/quit", methods=("GET", "POST"))
def group_quit(slug):
    is_login()
    groupinfo = Group.query.urlname_get_info(slug)
    #组长不能退出本组
    if groupinfo.leader_id == g.user.id:
        flash(u'组长不能提前退出小组哦！', "error")
        return redirect(url_for("group.group_view", slug=groupinfo.url_name))
    is_join = Group_User.query.is_join(groupinfo.id,g.user.id)
    if is_join:
        Group_User.query.filter( Group_User.user_id == g.user.id ).\
            filter( Group_User.group_id == groupinfo.id ).delete()
        #小组成员人数-1
        groupinfo.num_members = groupinfo.num_members - 1
        db.session.commit()
        flash(u'成功退出小组', "success")
    else:
        flash(u'您还不是小组成员呢', "error")
    return redirect(url_for("group.group_view", slug=groupinfo.url_name))


'''
小组回收站
'''
@group.route("/<slug>/trash", methods=("GET", "POST"))
def group_trash(slug):
    is_login()
    groupinfo = Group.query.urlname_get_info(slug)
    #如果没有指定就默认为第一页
    action = request.args.get("action", '').strip()
    if action == 'restore':
        if groupinfo.leader_id == g.user.id or g.user.role >=300:
            id = int(request.args.get("id", '').strip())
            topic = Group_Topic.query.get_or_404(id)
            topic.deleteed = 0
            db.session.commit()
            flash(u'主题恢复成功', "success")
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1
    #判断是不是组长
    if groupinfo.leader_id == g.user.id:
        topic_list = Group_Topic.query.get_topic_trash_list(groupinfo.id).\
                 paginate(page, per_page=30)
    else:
        topic_list = Group_Topic.query.get_my_topic_trash_list(groupinfo.id,g.user.id).\
            paginate(page, per_page=30)
   
    page_url = lambda page: '?page='+str(page)

    return render_template( 'group/group_trash.html',groupinfo=groupinfo,\
         topic_list=topic_list, page_url=page_url)
 