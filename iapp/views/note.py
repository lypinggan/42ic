# -*- coding: utf-8 -*-
import uuid
import time
import os
import random, string
from flask import Module, flash, request, g, current_app, \
    abort, redirect, url_for, session, jsonify

from flaskext.mail import Message
from flaskext.babel import gettext as _
from flaskext.principal import identity_changed, Identity, AnonymousIdentity


from iapp.forms import ChangePasswordForm, EditAccountForm, \
    DeleteAccountForm, LoginForm, SignupForm, RecoverPasswordForm, EditNameCardForm
from iapp.models import User,Users_icon
from iapp.helpers import render_template, md5
from iapp.extensions import db, mail
from iapp.utils.online import is_login
'''
笔记应用
'''
note = Module(__name__)
'''
笔记首页
显示公开的所有笔记
'''
@note.route("/")
@note.route("/<int:page>/")
def index():
    return u"笔记功能正在开发中，各位敬请期待。"
