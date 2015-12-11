# -*- coding: utf-8 -*-
"""
用户会话以及在线信息方法

"""
import os
import logging, time
import uuid

from flask import Flask, Response, request, g, \
        jsonify, redirect, url_for, flash, session, abort

from iapp.extensions import db, cache
from iapp.models import User

'''
如果用户登陆了
通过session_id获取该用户的信息给g.user
if session['user_id']:
    g.user = login_session()
'''
def login_session():
    if cache.get('session_login_uid_'+str(session['user_id'])):
        g.user =  cache.get('session_login_uid_'+str(session['user_id']))
    else:
        g.user = User.query.filter_by( id = session['user_id'] ).first()
        cache.set('session_login_uid_'+str(session['user_id']), g.user, 900)
'''
如果是访客
缓存时间为15分钟，用于显示15分钟在线人数
'''
def guest_session():
    g.user = False
    if 'id' not in session:
        session['id'] = uuid.uuid4()
    if not cache.get('session_guest_user_'+str(session['id'])):
        cache.set('session_guest_user_'+str(session['id']), 'online', 900)
'''
用于判断是否登陆
'''
def is_login():
    if 'user_id' in session:
        pass
    else:
        abort(401)
    
    