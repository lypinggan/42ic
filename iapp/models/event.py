# -*- coding: utf-8 -*-
import hashlib

from datetime import datetime

from flaskext.sqlalchemy import BaseQuery

from iapp.extensions import db
from iapp.permissions import null
from iapp.models.permissions import Permissions
from iapp.models import User




class EventQuery(BaseQuery):
    def all_list(self):
        return self.order_by(Event.id.desc())

'''
事件表:广播系统的主表
插入使用原生SQL
'''
class Event(db.Model):
    
    __tablename__ = "event"
    query_class = EventQuery

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
                          db.ForeignKey(User.id, ondelete='CASCADE'), 
                          nullable=False)
    user = db.relation(User, innerjoin=True, lazy="joined")
    
    #发生时间
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    #事件属性代号
    event_type = db.Column(db.Integer)

    #属性所需要的ID，比如问题ID，话题ID等
    event_msg_id = db.Column(db.Integer)
    
    #事件标题
    title = db.Column(db.String(250),default=u'')
    
    #事件详细描述
    description = db.Column(db.UnicodeText)

    #发生时间
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        
        
class Event_UserQuery(BaseQuery):
    def mine_list(self,user_id):
        return self.filter(Event_User.feed_user_id == user_id ).order_by(Event_User.id.desc())

    def talk_list(self,user_id):
        return self.filter(Event_User.feed_user_id == user_id )\
                    .filter(Event_User.event_type_mini == 2 ).order_by(Event_User.id.desc())

    def question_list(self,user_id):
        return self.filter(Event_User.feed_user_id == user_id )\
                    .filter(Event_User.event_type_mini == 3 ).order_by(Event_User.id.desc())

    def topic_list(self,user_id):
        return self.filter(Event_User.feed_user_id == user_id )\
                    .filter(Event_User.event_type_mini == 5 ).order_by(Event_User.id.desc())

'''
事件关系表，存储与用户有关的事件记录
插入使用原生SQL
'''
class Event_User(db.Model):
    
    __tablename__ = "event_user"
    query_class = Event_UserQuery

    id = db.Column(db.Integer, primary_key=True)
    
    #关联的事件ID
    event_id = db.Column(db.Integer)

    #操作代号100等
    event_type = db.Column(db.Integer)
    #事件分类：1、用户；3、问答；5、小组
    event_type_mini = db.Column(db.Integer)

    #事件影响到的用户ID，=0表示是全局
    feed_user_id = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(Event_User, self).__init__(*args, **kwargs)
