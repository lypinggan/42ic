# -*- coding: utf-8 -*-
'''
小组的模型
'''
import random
import time

from datetime import datetime

from werkzeug import cached_property

from flask import url_for, Markup, g, abort
from flaskext.sqlalchemy import BaseQuery
from flaskext.principal import Permission, UserNeed, Denial

from iapp.extensions import db
from iapp.permissions import auth, moderator
from iapp.models.permissions import Permissions
from iapp.models.users import User

'''
小组信息
'''
class GroupQuery(BaseQuery):

    def urlname_get_info(self, urlname):
        info = self.filter(Group.url_name==urlname).\
                filter(Group.closed==0).first()
        if info is None:
            abort(404)
        else:
            return info
    #通过ID获得小组信息
    def id_get_info(self, id):
        info = self.filter(Group.id==id).\
                filter(Group.closed==0).first()
        if info is None:
            abort(404)
        else:
            return info
    #通过ID获得小组信息
    def hot_group_list(self):
        list = self.order_by(Group.num_members.desc()).limit(9).all()
        return list
    #搜索小组
    def search(self, keywords):
        criteria = []
        for keyword in keywords.split():
    
            keyword = '%' + keyword + '%'
    
            criteria.append(db.or_(Group.name.ilike(keyword)))
    
        q = reduce(db.and_, criteria)
        return self.filter(q).order_by(Group.num_members.desc())
    

class Group(db.Model):

    __tablename__ = "group"
    
    PER_PAGE = 10
    query_class = GroupQuery
    
    id = db.Column(db.Integer, primary_key=True)
    #小组名称
    name = db.Column(db.Unicode(256))
    
    #小组UEL名称（只能为英文）
    url_name = db.Column(db.Unicode(256))

    #小组图标地址
    group_icon_url = db.Column(db.Unicode(256))

    #组长
    leader_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    leader = db.relation(User, innerjoin=True, lazy="joined")
    
    #创建时间
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    #小组描述
    description = db.Column(db.UnicodeText)
    
    #成员人数
    num_members = db.Column(db.Integer, default=0)
    
    #成员加入方式（0=允许任何人加入，1=需要小组管理员批准才能加入，2=只能通过邀请加入）
    join_type = db.Column(db.Integer, default=0)

    #=1为关闭
    closed = db.Column(db.Integer, default=0)
   

    def __init__(self,  name, url_name, leader_id, description):
        self.name = name
        self.url_name = url_name
        self.leader_id = leader_id
        self.description = description
        self.num_members = 1

'''
友情小组
'''
class Friendly_GroupQuery(BaseQuery):
    #获取友情小组列表
    def get_friendly_group_list(self,group_id):
        return self.filter(self.group_id == group_id).all()

class Friendly_Group(db.Model):

    __tablename__ = "friendly_group"
    
    query_class = Friendly_GroupQuery
    
    id = db.Column(db.Integer, primary_key=True)
    #小组ID
    group_id = db.Column(db.Integer)
    #友情小组ID
    friendly_group_id = db.Column(db.Integer, 
                          db.ForeignKey(Group.id, ondelete='CASCADE'), 
                          nullable=False)
    friendly_group = db.relation(Group, innerjoin=True, lazy="joined")
  

    def __init__(self,group_id, friendly_group_id ):
        self.group_id = group_id
        self.friendly_group_id = friendly_group_id





'''
小组用户关联
'''
class Group_UserQuery(BaseQuery):
    #获取最近加入小组的用户列表
    def recently_join_user(self,group_id):
        return self.filter(Group_User.group_id == group_id).\
            order_by(Group_User.id.desc()).limit(9).all()
    #获取用户所加入的小组列表(前9)
    def my_join_group(self,user_id):
        return self.filter(Group_User.user_id == user_id).\
            order_by(Group_User.id.desc()).limit(9).all()
    #获取用户所加入的所有小组列表
    def my_join_all_group(self,user_id):
        return self.filter(Group_User.user_id == user_id).\
            order_by(Group_User.id.desc()).all()

    #判断一个用户是否加入
    def is_join(self,group_id,user_id):
        return self.filter(Group_User.group_id == group_id).\
            filter(Group_User.user_id == user_id).first()

class Group_User(db.Model):

    __tablename__ = "group_user"
    
    query_class = Group_UserQuery
    
    id = db.Column(db.Integer, primary_key=True)
    
    #小组ID
    group_id = db.Column(db.Integer, 
                          db.ForeignKey(Group.id, ondelete='CASCADE'), 
                          nullable=False)
    group = db.relation(Group, innerjoin=True, lazy="joined")
    #用户ID
    user_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    user = db.relation(User, innerjoin=True, lazy="joined")
    
    #创建时间
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, group_id, user_id ):
        self.group_id = group_id
        self.user_id  = user_id


'''
小组主题
'''
class Group_TopicQuery(BaseQuery):

    #获取主题的列表
    def get_topic_list(self,group_id ):
        return self.filter(Group_Topic.group_id  == group_id ).\
                filter(Group_Topic.deleteed  == 0 ).\
                order_by(Group_Topic.set_top.desc(),Group_Topic.sort.desc())
    #获取所有主题的列表
    def get_all_list(self):
        return self.filter(Group_Topic.deleteed  == 0 ).\
                order_by(Group_Topic.sort.desc())
    #获取属于我的主题的列表（我加入小组的主题）
    def get_my_list(self, user_id):
        my_group = Group_User.query.filter(Group_User.user_id  == user_id ).all()
        grouplist = []
        for m in my_group:
            grouplist.append(m.group_id)
        return self.filter(Group_Topic.group_id.in_(grouplist)).filter(Group_Topic.deleteed  == 0 ).\
                order_by(Group_Topic.sort.desc(),Group_Topic.id.desc())
    #获取我的发起的话题列表
    def get_my_topics_list(self, user_id):
        return self.filter(Group_Topic.author_id == user_id ).filter(Group_Topic.deleteed  == 0 ).\
                order_by(Group_Topic.sort.desc(),Group_Topic.id.desc())

    #获取主题回收站的列表
    def get_topic_trash_list(self,group_id ):
        return self.filter(Group_Topic.group_id  == group_id ).\
                filter(Group_Topic.deleteed  == 1 ).\
                order_by(Group_Topic.set_top.desc(),Group_Topic.sort.desc())
    #获取作者的主题回收站的列表
    def get_my_topic_trash_list(self,group_id,author_id ):
        return self.filter(Group_Topic.group_id  == group_id ).filter(Group_Topic.author_id  == author_id ).\
                filter(Group_Topic.deleteed  == 1 ).\
                order_by(Group_Topic.set_top.desc(),Group_Topic.sort.desc())
    #搜索话题
    def search(self, keywords):
        criteria = []
        for keyword in keywords.split():

            keyword = '%' + keyword + '%'

            criteria.append(db.or_(Group_Topic.title.ilike(keyword),\
                                    Group_Topic.description.ilike(keyword)))

        q = reduce(db.and_, criteria)
        return self.filter(q).order_by(Group_Topic.num_comment.desc())





class Group_Topic(db.Model):

    __tablename__ = "group_topic"
    

    PER_PAGE = 20
    query_class = Group_TopicQuery
    
    id = db.Column(db.Integer, primary_key=True)
    
    #作者
    author_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    author = db.relation(User, innerjoin=True, lazy="joined")
    
    #所属小组ID
    group_id = db.Column(db.Integer, 
                          db.ForeignKey(Group.id, ondelete='CASCADE'), 
                          nullable=False)

    group = db.relation(Group, innerjoin=True, lazy="joined")
    
    #主题标题
    title = db.Column(db.Unicode(256))
    
    #主题具体内容
    description = db.Column(db.UnicodeText)
    
    #创建时间
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    #评论次数
    num_comment = db.Column(db.Integer, default=0)
    
    #最后回复
    date_last_response = db.Column(db.DateTime, default=datetime.now)
    #最后排序，从大到小
    sort = db.Column(db.Integer)
    #查看次数
    num_views = db.Column(db.Integer, default=0)
    
    #喜欢人数
    num_like = db.Column(db.Integer, default=0)
    
    #=1为置顶主题
    set_top = db.Column(db.Integer, default=0)
    
    #=1为关闭
    closed = db.Column(db.Integer, default=0)
    #=1为删除
    deleteed = db.Column(db.Integer, default=0)
    
    ip = db.Column(db.Unicode(20))

    def __init__(self, *args, **kwargs):
        self.author_id = g.user.id
        self.sort = int(time.time())
        super(Group_Topic, self).__init__(*args, **kwargs)


'''
主题回复信息
'''
class Group_ReplyQuery(BaseQuery):

    #获取主题回复的列表
    def get_reply_list(self,topic_id ):
        return self.filter(Group_Reply.topic_id  == topic_id ).\
                filter(Group_Reply.deleteed  == 0 ).order_by(Group_Reply.id).all()
    

class Group_Reply(db.Model):

    __tablename__ = "group_reply"
    

    PER_PAGE = 10
    query_class = Group_ReplyQuery
    
    id = db.Column(db.Integer, primary_key=True)
    
    #作者
    author_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    author = db.relation(User, innerjoin=True, lazy="joined")
    
    #所属话题ID
    topic_id = db.Column(db.Integer)
    
    #创建时间
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    #回复内容
    content = db.Column(db.UnicodeText)
    
    #=1为删除
    deleteed = db.Column(db.Integer, default=0)
   

    def __init__(self, *args, **kwargs):
        self.author_id = g.user.id
        super(Group_Reply, self).__init__(*args, **kwargs)


'''
小组申请表
'''
class Group_RequisitionQuery(BaseQuery):

    def jsonify(self):
        for post in self.all():
            yield post.json

class Group_Requisition(db.Model):

    __tablename__ = "group_requisition"
    

    PER_PAGE = 10
    query_class = Group_RequisitionQuery
    
    id = db.Column(db.Integer, primary_key=True)
    
    #申请人
    author_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    author = db.relation(User, innerjoin=True, lazy="joined")
    
    #申请时间
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    #小组名称
    name = db.Column(db.Unicode(256))

    #小组UEL名称（只能为英文）
    url_name = db.Column(db.Unicode(256))
    

    #小组描述
    description = db.Column(db.UnicodeText)
    
    #申请状态0=未处理，1=通过，2、未通过
    status = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        self.author_id = g.user.id
        super(Group_Requisition, self).__init__(*args, **kwargs)

