# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextField, TextAreaField, RadioField, \
        SubmitField, ValidationError, optional, required, url
from flask import g
from iapp.models import *
from iapp.extensions import db
#新话题
class Group_New_TopicForm(Form):

    title = TextField(u"话题标题", validators=[
                      required(message=u"话题标题不能为空")])

    description = TextAreaField(u"话题内容")

    submit = SubmitField(u"好了,发言")

    def __init__(self, *args, **kwargs):
        super(Group_New_TopicForm, self).__init__(*args, **kwargs)
#编辑话题
class Group_Edit_TopicForm(Form):

    title = TextField(u"话题标题", validators=[
                      required(message=u"话题标题不能为空")])

    description = TextAreaField(u"话题内容")

    submit = SubmitField(u"好了,确认修改")

    def __init__(self, *args, **kwargs):
        super(Group_Edit_TopicForm, self).__init__(*args, **kwargs)

#话题回复        
class Group_Topic_New_ReplyForm(Form):

    content = TextAreaField(u"回复内容", validators=[
                      required(message=u"回复内容不能为空")])

    submit = SubmitField(u"好了,提交")

    def __init__(self, *args, **kwargs):
        super(Group_Topic_New_ReplyForm, self).__init__(*args, **kwargs)
#小组申请表单        
class Group_RequisitionForm(Form):
    name = TextField(u"小组名称", validators=[
                  required(message=u"小组名称不能为空")])
    url_name = TextField(u"小组URL名称", validators=[
              required(message=u"小组URL名称不能为空")])

    description = TextAreaField(u"小组介绍", validators=[
                      required(message=u"小组介绍不能为空")])

    submit = SubmitField(u"好了,提交")

    def __init__(self, *args, **kwargs):
        super(Group_RequisitionForm, self).__init__(*args, **kwargs)
    def validate_name(self, field):
        group = Group.query.filter(Group.name.like(field.data)).first()
        if group:
            raise ValidationError, u"小组名称已经被使用"


    def validate_url_name(self, field):
        group = Group.query.filter(Group.url_name.like(field.data)).first()
        if group:
            raise ValidationError, u"小组URL名称已经被使用"
#小组修改资料表单        
class Group_EditForm(Form):
    name = TextField(u"小组名称", validators=[
                  required(message=u"小组名称不能为空")])

    description = TextAreaField(u"小组介绍", validators=[
                      required(message=u"小组介绍不能为空")])
    submit = SubmitField(u"好了,提交")

    def __init__(self, *args, **kwargs):
        super(Group_EditForm, self).__init__(*args, **kwargs)
