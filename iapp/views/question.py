# -*- coding: utf-8 -*-
import uuid

from flask import Module, flash, request, g, current_app, \
    abort, redirect, url_for, session, jsonify

from flaskext.mail import Message
from flaskext.babel import gettext as _
from flaskext.principal import identity_changed, Identity, AnonymousIdentity

from iapp.forms import Question_AskForm, Question_EditForm, Answer_EditForm

from iapp.models import User, Question, Tag, Answer, Answer_Thank, Question_Votes,\
                        Question_Follow
from iapp.helpers import render_template
from iapp.extensions import db, mail, cache
from iapp.utils.online import is_login
from iapp.utils import Queue

queue = Queue()
question = Module(__name__)
#首页

@question.route("/", methods=("GET", "POST"))
def index():
    if (request.args.get("view", '').strip()):
        viewname = request.args.get("view", '').strip()
    else:
        viewname = "latest"#如果没有指定就默认为最新
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1#如果没有指定就默认为第一页

    #按规则处理列表数据
    #热门
    if viewname == 'hottest':
        question = Question.query.hottest().paginate(page, per_page=Question.PER_PAGE)
    #本月热门
    elif viewname == 'hotmonth':
        question = Question.query.hotmonth().paginate(page, per_page=Question.PER_PAGE)
    #未解答
    elif viewname == 'unanswered':
        question = Question.query.unanswered().paginate(page, per_page=Question.PER_PAGE)
    #我的提问
    elif viewname == 'my_questions':
        question = Question.query.my_questions().paginate(page, per_page=Question.PER_PAGE)
    #我关注的问题
    elif viewname == 'my_follow_questions':
        question_list = []
        question_follow = Question_Follow.query.filter(Question_Follow.user_id == g.user.id)\
                    .paginate(page, per_page=Question.PER_PAGE)
        for q in question_follow.items:
            question_list.append(q.question_id)
        q = Question.query.filter(Question.id.in_(question_list))
        question = question_follow
        question.items = q
    #我喜欢的问题
    elif viewname == 'my_like_questions':
        question_list = []
        question_like = Question_Votes.query.filter(Question_Votes.user_id == g.user.id)\
                        .paginate(page, per_page=Question.PER_PAGE)
        for q in question_like.items:
            question_list.append(q.question_id)
        q = Question.query.filter(Question.id.in_(question_list))
        question = question_like
        question.items = q
    else:
        question = Question.query.latest().paginate(page, per_page=Question.PER_PAGE)
    page_url = lambda page: '?view='+viewname+'&page='+str(page)#url_for("question.index", page=page)
    return render_template( 'question/list.html', question=question, title = u"所有问题",page_url=page_url,viewname=viewname)
@question.route("/search")
def question_search():
    keywords = request.args.get("q", '').strip()
    if not keywords:
        return redirect(url_for("question.index"))
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1#如果没有指定就默认为第一页
    question = Question.query.search(keywords).paginate(page, per_page=Question.PER_PAGE)
    page_url = lambda page: '?q='+keywords+'&page='+str(page)
    return render_template( 'question/search.html',question=question,\
                                page_url=page_url,keywords=keywords)
 
 #提问
@question.route("/ask", methods=("GET", "POST"))
@question.route("/ask/<slug>/", methods=("GET", "POST"))
def ask(slug=u''):
    is_login()
    form = Question_AskForm()
    if form.validate_on_submit():
        question = Question()
        form.populate_obj(question)
        question.ip = request.remote_addr
        db.session.add(question)
        db.session.commit()
        flash(u'问题发布成功', "success")
        queue.push((301,g.user.id,question.id,question.title,question.description[0:100]))#发任务
        queue.push((202,g.user.id,2))#提问增加2积分
        return redirect(url_for("question.view", question_id=question.id))
    return render_template( 'question/ask.html', form=form, title=slug)

 #浏览问题
@question.route("/<int:question_id>", methods=("GET", "POST"))
#@cache.cached(timeout=3)
def view(question_id):
    #我是否已经回答（用于处理模版的回答输入框）
    have_answered = 0
    if g.user:
        if Answer.query.filter(Answer.question_id==question_id).filter(Answer.author_id==g.user.id).first():
            have_answered = 1
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.answer_list( question_id )
    return render_template( 'question/view.html', question = question, answer = answer,have_answered=have_answered)
 #编辑问题
@question.route("/edit/<int:question_id>", methods=("GET", "POST"))
def edit(question_id):
    is_login()
    ed_question = Question.query.get_or_404(question_id)
    #需要权限大于等于200或本人才能修改问题
    if not ((g.user.role >= 200) or (g.user.id == ed_question.author_id)) :
        flash(u'您没有权限编辑问题', "error")
        return redirect(url_for("question.view", question_id=question_id))
    form = Question_EditForm(obj=ed_question)
    if form.validate_on_submit():
        form.populate_obj(ed_question)
        db.session.commit()
        #cache.delete(url_for("question.view", question_id=question_id))
        flash(u'问题保存成功', "success")
        return redirect(url_for("question.view", question_id=question_id))
    return render_template( 'question/edit.html', form =form,question = ed_question)
#回答问题
@question.route("/<int:question_id>/new_answer", methods=("GET","POST"))
def new_answer(question_id):
    is_login()
    ed_question = Question.query.get_or_404(question_id)
    if request.method == 'POST' and request.form['answer']:
        if ed_question.author_id == g.user.id:
            flash(u'自己不能回答自己问题的哦，有问题可以追问或编辑!', "error")
        else:
            ed_question = Question.query.get_or_404(question_id)
            ed_answer = Answer()
            ed_answer.answer = request.form['answer']
            ed_answer.ip = request.remote_addr
            ed_answer.question_id = question_id
            db.session.add( ed_answer )
            ed_question.num_answer = ed_question.num_answer + 1
            db.session.commit()
            flash(u'您的答案已经提交成功!', "success")
            #消息队列
            queue.push((302,g.user.id,ed_question.id,ed_question.title,ed_answer.answer[0:100]))
            queue.push((202,g.user.id,3))#回答问题增加3积分
            #cache.delete(url_for("question.view", question_id=question_id))
    return redirect(url_for("question.view", question_id=question_id))
#编辑答案
@question.route("/edit_answer/<int:answer_id>", methods=("GET","POST"))
def edit_answer(answer_id):
    is_login()
    ed_answer = Answer.query.get_or_404(answer_id)
    ed_question = Question.query.get_or_404(ed_answer.question_id)
    #需要权限大于等于200或本人才能修改问题
    if not ((g.user.role >= 200) or (g.user.id == ed_answer.author_id)) :
        flash(u'您没有权限编辑这个答案', "error")
        return redirect(url_for("question.view", ed_answer.question_id))
    form = Answer_EditForm(obj=ed_answer)
    if form.validate_on_submit():
        form.populate_obj(ed_answer)
        db.session.commit()
        flash(u'这个答案保存成功', "success")
        queue.push((202,g.user.id,1))#编辑问题增加1积分
        return redirect(url_for("question.view", question_id=ed_answer.question_id))
    return render_template( 'question/edit_answer.html', form =form,question = ed_question,answer=ed_answer)
#设置答案为满意答案
@question.route("/make_the_right_answer/<int:answer_id>", methods=("GET","POST"))
def make_the_right_answer(answer_id):
    is_login()
    #获取答案信息
    ed_answer = Answer.query.get_or_404(answer_id)
    question = Question.query.filter_by( id = ed_answer.question_id ).first()
    if question.author_id ==g.user.id or g.user.role>300:
        #检查是否已经有正确答案,
        if question.answer_id:
            flash(u'操作失败，一个问题只能有一个满意答案!', "error")
        else:
            #设置答案为满意答案
            this_answer = Answer.query.filter_by( id = answer_id ).first()
            #return str(this_answer)
            this_answer.answer_ok = 1
            #设置问题的满意答案ID
            question.answer_id = answer_id
            user = User.query.filter_by( id = ed_answer.author_id ).first()
            #答案作者威望+3
            user.prestige = user.prestige + 3
            #答案作者答案采纳数+1
            user.best_answer_number = user.best_answer_number + 1
            db.session.commit()
            queue.push((202,g.user.id,5))#找到正确增加5积分
            flash(u'恭喜您找到满意答案，问题状态已更新成功!', "success")
    else:
        flash(u'您没有权限操作!', "error")
    return redirect(url_for("question.view", question_id=ed_answer.question_id))
#感谢他
@question.route("/thankhim/<int:answer_id>", methods=("GET","POST"))
def thankhim(answer_id):
    is_login()
    #获取答案信息
    ed_answer = Answer.query.get_or_404(answer_id)
    if ed_answer.author_id ==g.user.id:
        return jsonify(status =0,value = u'不能感谢自己')
    else:
        athink = Answer_Thank.query.filter(Answer_Thank.answer_id==answer_id).filter(Answer_Thank.user_id==g.user.id).first()
        if athink:
            return jsonify(status = 0,value = u'已经感谢过了')
        else:
            athink = Answer_Thank(g.user.id,answer_id)
            db.session.add(athink)
            user = User.query.filter_by( id = ed_answer.author_id ).first()
            #答案作者威望+1
            user.prestige = user.prestige + 1
            db.session.commit()
            return jsonify(status = 1,value = u'操作成功！')

