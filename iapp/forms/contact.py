# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextField, TextAreaField, SubmitField, \
        required, email

from flaskext.babel import lazy_gettext as _

class ContactForm(Form):

    name = TextField(u"name", validators=[
                     required(message=u"A valid name is required")])

    email = TextField(u"Your email address", validators=[
                      required(message=u"Email address required"),
                      email(message=u"A valid email address is required")])

    subject = TextField(u"Subject", validators=[
                        required(message=u"Subject required")])

    message = TextAreaField(u"Message", validators=[
                            required(message=u"Message required")])

    submit = SubmitField(u"Send")

class MessageForm(Form):

    subject = TextField(u"Subject", validators=[
                        required(message=u"Subject required")])

    message = TextAreaField("Message", validators=[
                            required(message=u"Message required")])

    submit = SubmitField(u"Send")


