# -*- coding: utf-8 -*-
from flask import Module, redirect, flash, g, jsonify, current_app

from flaskext.mail import Message
from flaskext.babel import gettext as _

from iapp import signals
from iapp.helpers import render_template
from iapp.utils.online import is_login
from iapp.models import Comment
from iapp.forms import CommentForm, CommentAbuseForm
from iapp.extensions import db, mail

comment = Module(__name__)

@comment.route("/<int:comment_id>/edit/", methods=("GET", "POST"))
def edit(comment_id):
    is_login()
    comment = Comment.query.get_or_404(comment_id)
    comment.permissions.edit.test(403)

    form = CommentForm(obj=comment)

    if form.validate_on_submit():
        
        form.populate_obj(comment)

        db.session.commit()

        flash(_("Your comment has been updated"), "success")

        return redirect(comment.url)
    
    return render_template("comment/edit_comment.html",
                           comment=comment,
                           form=form)

@comment.route("/<int:comment_id>/delete/", methods=("POST",))
def delete(comment_id):
    is_login()
    comment = Comment.query.get_or_404(comment_id)
    comment.permissions.delete.test(403)

    db.session.delete(comment)
    db.session.commit()

    signals.comment_deleted.send(comment.post)

    return jsonify(success=True,
                   comment_id=comment_id)

@comment.route("/<int:comment_id>/abuse/", methods=("GET", "POST",))
def report_abuse(comment_id):
    is_login()
    comment = Comment.query.get_or_404(comment_id)
    form = CommentAbuseForm()
    if form.validate_on_submit():

        admins = current_app.config['ADMINS']

        if admins:

            body = render_template("emails/report_abuse.html",
                               comment=comment,
                               complaint=form.complaint.data)
            
            message = Message(subject="Report Abuse",
                              body=body,
                              sender=g.user.email,
                              recipients=admins)

            mail.send(message)
            
        flash(_("Your report has been sent to the admins"), "success")

        return redirect(comment.url)

    return render_template("comment/report_abuse.html",
                           comment=comment,
                           form=form)

@comment.route("/<int:comment_id>/upvote/", methods=("POST",))
def upvote(comment_id):
    is_login()
    return _vote(comment_id, 1)


@comment.route("/<int:comment_id>/downvote/", methods=("POST",))
def downvote(comment_id):
    is_login()
    return _vote(comment_id, -1)


def _vote(comment_id, score):

    comment = Comment.query.get_or_404(comment_id)
    comment.permissions.vote.test(403)
    
    comment.score += score
    comment.author.karma += score

    if comment.author.karma < 0:
        comment.author.karma = 0

    comment.vote(g.user)

    db.session.commit()

    return jsonify(success=True,
                   comment_id=comment_id,
                   score=comment.score)
