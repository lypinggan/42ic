# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextField, TextAreaField, RadioField, \
        SubmitField, ValidationError, optional, required, url
from flask import g
from flaskext.babel import gettext, lazy_gettext as _

from iapp.models import Question,Answer
from iapp.extensions import db

class Question_AskForm(Form):

    title = TextField(u"问题标题", validators=[
                      required(message=u"问题标题不能为空")])

    description = TextAreaField(u"问题描述")

    tags = TextField(u"标签", validators=[
                      required(message=u"问题标签不能为空")])

    submit = SubmitField(u"提交问题")

    def __init__(self, *args, **kwargs):
        super(Question_AskForm, self).__init__(*args, **kwargs)


class Question_EditForm(Form):

    title = TextField(u"问题标题", validators=[
                      required(message=u"问题标题不能为空")])

    description = TextAreaField(u"问题描述")

    tags = TextField(u"标签", validators=[
                      required(message=u"问题标签不能为空")])

    submit = SubmitField(u"编辑问题")

    def __init__(self, *args, **kwargs):
        super(Question_EditForm, self).__init__(*args, **kwargs)
class Answer_EditForm(Form):

    answer = TextAreaField(u"答案内容", validators=[
                      required(message=u"答案内容不能为空")])

    submit = SubmitField(u"编辑答案")

    def __init__(self, *args, **kwargs):
        super(Answer_EditForm, self).__init__(*args, **kwargs)
