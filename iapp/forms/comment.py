# -*- coding: utf-8 -*-
from flaskext.wtf import Form, TextAreaField, SubmitField, required
from flaskext.babel import lazy_gettext as _

class CommentForm(Form):

    comment = TextAreaField(validators=[
                            required(message=_("Comment is required"))])

    submit = SubmitField(u"保存")
    cancel = SubmitField(u"取消")

   
class CommentAbuseForm(Form):

    complaint = TextAreaField("Complaint", validators=[
                              required(message=\
                                       _("You must enter the details"
                                         " of the complaint"))])


    submit = SubmitField(u"OK,发送!")
