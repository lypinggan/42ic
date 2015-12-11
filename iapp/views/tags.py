# -*- coding: utf-8 -*-
from flask import Module, url_for, \
    redirect, g, flash, request, current_app

from flaskext.mail import Message
from flaskext.babel import gettext as _
from iapp.utils.jsonify import jsonify
from iapp.extensions import mail, db
from iapp.helpers import render_template, cached
#from iapp.forms import PostForm, ContactForm
from iapp.decorators import keep_login_url
from iapp.utils.online import is_login
from iapp.models import User, Question, Tag, Answer
tags = Module(__name__)
'''
过滤标签
'''
@tags.route("/filter")
@keep_login_url
#@jsonify
def tags_filter():
    keywords = request.args.get("q", '').strip()
    callback = request.args.get("callback", '').strip()
    #return "jQuery15109137110933661461_1317046196452('android|35\njavascript|26\njava|24\nmatlab|17\najax|4\napi|3\nbase64|3\ndate|3\ndjango|3\nasp|2\ncache|2\ndatetime|2\naccount|1\nalert|1\nbash|1\nbeta|1\nbinary|1\nbitmap|1\nboolean|1\nclipboard|1\n')"
    t = Tag.query.tags_search( keywords ).all()
    h = ''
    for i in t:
        h += i.slug+'|'+str(i.num_question)+str('//n')
    return callback + '("'+h+'")'
    '''
    for i in t:
        j['id_'+str(i.id)] = i.slug
    #return h
    #j = {'foo': t, 'baz': [1,2,3]}
    return j#{'foo': t, 'baz': [1,2,3]}
    '''
'''
标签查看
'''
@tags.route("/<slug>")
@keep_login_url
def view(slug):
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1

    tag = Tag.query.filter_by(slug=slug).first_or_404()

    page_obj = tag.question.\
                    paginate(page, per_page=Question.PER_PAGE)

    page_url = lambda page: '?page='+str(page)

    return render_template("tag.html", 
                           tag=tag,
                           page_url=page_url,
                           page_obj=page_obj)


