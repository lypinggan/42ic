# -*- coding: utf-8 -*-
import random, string, time, os
from flask import Module, url_for, \
    redirect, g, flash, request, current_app, abort
from werkzeug import secure_filename
from flaskext.mail import Message
from flaskext.babel import gettext as _

from iapp.models import User, Question, Tag, Answer,Event, Event_User\
                        ,Group,Group_Topic, Attachment
from iapp.extensions import mail, db, cache
from iapp.forms import ChangePasswordForm, EditAccountForm, \
    DeleteAccountForm, LoginForm, SignupForm, RecoverPasswordForm, EditNameCardForm

from iapp.helpers import render_template, cached
#from iapp.forms import PostForm, ContactForm
from iapp.decorators import keep_login_url
from iapp.utils.online import is_login
from iapp.utils import Queue

queue = Queue()

frontend = Module(__name__)

'''
首页
'''
#首页
@frontend.route("/", methods=("GET", "POST"))
def index():
    if not g.user:
        loginform = LoginForm()
        signupform = SignupForm()
        return render_template( 'hi.html',loginform=loginform,signupform=signupform)
    if (request.args.get("view", '').strip()):
        viewname = request.args.get("view", '').strip()
    else:
        viewname = "mine"#如果没有指定就默认为全部

    if viewname == 'all':
        if cache.get('event_list-all-html'):
            e_html = cache.get('event_list-all-html')
        else:
            a = Event.query.all_list().paginate(1,20)
            e_html = ''
            for e in a.items:
                e_html += render_template( 'event_list.html',e=e)
            cache.set('event_list-all-html',e_html,20)
    else:
        if viewname == 'mine':
            event_user_list = Event_User.query.mine_list(g.user.id).paginate(1,20)
        elif viewname == 'talk':
            event_user_list = Event_User.query.talk_list(g.user.id).paginate(1,20)
        elif viewname == 'question':
            event_user_list = Event_User.query.question_list(g.user.id).paginate(1,20)
        elif viewname == 'topic':
            event_user_list = Event_User.query.topic_list(g.user.id).paginate(1,20)
        else:
            abort(404)
        e_html = ''
        #try:
        for eu in event_user_list.items:
            if cache.get('event-id-'+str(eu.event_id)):
                e_html += cache.get('event-id-'+str(eu.event_id))
            else:
                e = Event.query.get(eu.event_id)
                h = render_template('event_list.html',e=e)
                cache.set('event-id-'+str(eu.event_id),h,100)
                e_html += h         
            '''
            if cache.get('event-id-'+str(eu.id)):
                event_list.append(cache.get('event-id-'+str(eu.id)))
            else:
                event = Event.query.get(eu.id)
                #cache.set('event-id-'+str(eu.id),event,6000)
                event_list.append(event)
            '''
        #except:
        #    event_list = None
    #return ''
    return render_template( 'index.html',viewname=viewname,e_html=e_html)



@frontend.route("/search")
@keep_login_url
def search():
    keywords = request.args.get("q", '').strip()
    group_submit = request.args.get("group_submit", '').strip()
    topic_submit = request.args.get("topic_submit", '').strip()
    if not keywords:
        return redirect(url_for("frontend.index"))
    if group_submit == u'搜索小组':
        viewname = 'group_submit'
        group_list = Group.query.search(keywords).all()
        return render_template( 'group/search.html',viewname=viewname\
                                ,group_list=group_list,keywords=keywords)
    if topic_submit == u'搜索发言':
        viewname = 'topic_submit'
        topic_list = Group_Topic.query.search(keywords).all()
        return render_template( 'group/search.html',viewname=viewname\
                                ,topic_list=topic_list,keywords=keywords)
    return redirect(url_for("frontend.index"))
@frontend.route("/search/ajax_question")
@keep_login_url
def ajax_question_search():
    keywords = request.args.get("q", '').strip()
    html = ''
    if cache.get("/search/ajax"+keywords):
        html = cache.get("/search/ajax"+keywords)
    else:
        question_list = Question.query.search(keywords).limit(9).all()
        html += '<ul>'
        for q in question_list:
            html += '<li><a href="/question/'+str(q.id)+'">'+q.title+'</a></li>'
        html += '</ul>'
        cache.set("/search/ajax"+keywords,html,60)

    return html

'''
文件上传
'''
'''
@frontend.route( "/upload", methods = ['GET', 'POST'] )
@auth.require(401)
def user_up_load():
    if (request.args.get("page", '').strip()):
        page = int(request.args.get("page", '').strip())
    else:
        page = 1
    page_url = lambda page: '?page='+str(page)
    
    file_list = Upload_File.query.filter(Upload_File.user_id == g.user.id)\
                    .order_by(Upload_File.id.desc()).paginate(page, per_page=30)
    
    
    return render_template("upload.html",page_url=page_url,file_list=file_list)
@frontend.route( "/user_up_file", methods = ['GET', 'POST'] )
def user_up_file():
    if request.method == 'POST':
        UPLOAD_FOLDER = '/home/lyping/data/42ic/iapp/static/uploads'
        tmp = str(random.randrange(0,9))
        upload_path = UPLOAD_FOLDER+'/'+tmp
        try:
            os.makedirs(upload_path)
        except:
            pass
        file = request.files['upfile']
        if file and g.user and allowed_file( file.filename ):
            filename = str( g.user.id ) + "-" + str( int(time.time()) ) + "." + file.filename.rsplit( '.', 1 )[1]
            file.save(os.path.join(upload_path, filename))
            info = Upload_File(g.user.id,file.filename.rsplit( '.', 1 )[1],file.filename,tmp+'/'+filename)
            db.session.add(info)
            db.session.commit()
            flash(u"文件上传成功", "success")
    return redirect(url_for("frontend.user_up_load"))
    #my_file = request.files['picfile']
    #my_file = None

@frontend.route( "/upload", methods = ['GET', 'POST'] )
@auth.require(401)
def upload_file():
    file_path = '/home/lyping/data/42ic/iapp/static/uploads'
    ALLOWED_EXTENSIONS = set( ['bmp', 'png', 'jpg', 'jpeg', 'gif', 'BMP', 'PNG', 'JPG', 'JPEG', 'GIF'] )    
    file = request.files['Filedata']
    if g.user and file and allowed_file( file.filename ):
        #0-9是随机的目录
        tmp = str(random.randrange(0,9))
        filename = tmp+'/42ic-'+str( g.user.id ) + "-" + str( int(time.time()) ) + "." + file.filename.rsplit( '.', 1 )[1]
        file.save( os.path.join( file_path, filename ) )
        info = Upload_File(g.user.id,file.filename.rsplit( '.', 1 )[1],file.filename,filename)
        db.session.add(info)
        db.session.commit()
        return 'ok'
    return render_template("upload.html")

@frontend.route("/saved/")
@frontend.route("/saved/<int:page>/")
@auth.require(401)
def saved(page=1):

    page_obj = Post.query.saved().as_list().paginate(page, per_page=Post.PER_PAGE)

    page_url = lambda page: url_for("frontend.saved", page=page)

    return render_template("saved.html", 
                           page_obj=page_obj, 
                           page_url=page_url)


@frontend.route("/submit/", methods=("GET", "POST"))
@auth.require(401)
def submit():

    form = PostForm()
    
    if form.validate_on_submit():

        post = Post(author=g.user)
        form.populate_obj(post)

        db.session.add(post)
        db.session.commit()

        flash(_("Thank you for posting"), "success")

        return redirect(url_for("frontend.latest"))

    return render_template("submit.html", form=form)


@frontend.route("/search/")
@frontend.route("/search/<int:page>/")
@keep_login_url
def search(page=1):

    keywords = request.args.get("keywords", '').strip()

    if not keywords:
        return redirect(url_for("frontend.index"))

    page_obj = Post.query.search(keywords).restricted(g.user).as_list().\
                          paginate(page, per_page=Post.PER_PAGE)

    if page_obj.total == 1:

        post = page_obj.items[0]
        return redirect(post.url)
    
    page_url = lambda page: url_for('frontend.search', 
                                    page=page,
                                    keywords=keywords)

    return render_template("search.html",
                           page_obj=page_obj,
                           page_url=page_url,
                           keywords=keywords)



@frontend.route("/contact/", methods=("GET", "POST"))
@keep_login_url
def contact():

    if g.user:
        form = ContactForm(name=g.user.username,
                           email=g.user.email)

    else:
        form = ContactForm()

    if form.validate_on_submit():

        admins = current_app.config.get('ADMINS', [])

        from_address = "%s <%s>" % (form.name.data, 
                                    form.email.data)

        if admins:
            message = Message(subject=form.subject.data,
                              body=form.message.data,
                              recipients=admins,
                              sender=from_address)

            mail.send(message)
        
        flash( u"感谢您的意见！", "success")

        return redirect(url_for('frontend.index'))

    return render_template("contact.html", form=form)


@frontend.route("/tags/")
@cached()
@keep_login_url
def tags():
    tags = Tag.query.cloud()
    return render_template("tags.html", tag_cloud=tags)


@frontend.route("/tags/<slug>/")
@frontend.route("/tags/<slug>/<int:page>/")
@cached()
@keep_login_url
def tag(slug, page=1):
    tag = Tag.query.filter_by(slug=slug).first_or_404()

    page_obj = tag.posts.restricted(g.user).as_list().\
                    paginate(page, per_page=Post.PER_PAGE)

    page_url = lambda page: url_for('frontend.tag',
                                    slug=slug,
                                    page=page)

    return render_template("tag.html", 
                           tag=tag,
                           page_url=page_url,
                           page_obj=page_obj)
    
@frontend.route("/tags/filter/<int:tag_id>/", methods=("POST",))
@auth.require(401)
def filter_tag(tag_id):

    tag = Tag.query.get_or_404(tag_id)
    g.user.filters.add(tag.id)
    db.session.commit()

    return jsonify(success=True)

@frontend.route("/help/")
@keep_login_url
def help():
    return render_template("help.html")


@frontend.route("/rules/")
@keep_login_url
def rules():
    return render_template("rules.html")
@frontend.route("/about/")
@keep_login_url
def rules():
    return render_template("about.html")
'''
