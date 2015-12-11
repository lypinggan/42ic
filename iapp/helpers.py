# -*- coding: utf-8 -*-
"""
    helpers.py
    ~~~~~~~~
    Helper functions for 42ic
    :copyright: (c) 2010 by lyping gan
    :license: BSD, see LICENSE for more details.
"""
import markdown2
import re
import hashlib
import urlparse
import functools

from datetime import datetime

from flask import current_app, g, render_template as rt, url_for

from flaskext.babel import gettext, ngettext

from iapp.extensions import cache
from iapp.utils.dbc import get_attachment_file_url, get_mini_attachment_file_url
from iapp.utils.time_format import friendly_time 

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug. From http://flask.pocoo.org/snippets/5/"""
    result = []
    for word in _punct_re.split(text.lower()):
        #word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))

"""
markdown = functools.partial(markdown.markdown,
                             safe_mode='remove',
                             output_format="html")
"""
def markdown(value):
    value = markdown2.markdown( value )
    value = value.replace(u'<code>',u'<div class="code"><pre class="prettyprint">')
    value = value.replace(u'</code>',u'</pre></div>')
    return value
    '''
    strlt = re.compile('<')
    html = strlt.sub( '&lt;',value )
    html = mkdown.markdown(html)
    #strbr = re.compile('\r\n')
    #html = strbr.sub( '<br/>',html )
    #strnb = re.compile(' ')
    #html = strnb.sub( '&nbsp;',html )
    #html.replace(' ' , '&nbsp;')
    #print html
    return html
    '''
"""
表单里的内容转换为html
"""
def tohtml(value):
    #处理<实现过滤HTML已经安全标签
    value = value.replace(u'<',u'&lt;')

    value = value.replace(u' ',u'&nbsp;')
    value = value.replace(u'	',u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
    value = value.replace(u'\n',u'<br/>')

    #加粗
    value = value.replace(u'[b]',u'<b>')
    value = value.replace(u'[/b]',u'</b>')
    #图片
    pattern = re.compile( r'\[img\](.+?)\[/img\]')
    value = pattern.sub( r'<img src="\1">',value)
    pattern = re.compile( r'\[img=(.+?)\](.+?)\[/img\]')
    value = pattern.sub( r'<img src="\1" alt="\2">',value)    
    #url
    pattern = re.compile( r'\[url\](.+?)\[/url\]')
    value = pattern.sub( r'<a href="\1">\1</a>',value)
    pattern = re.compile( r'\[url=(.+?)\](.+?)\[/url\]')
    value = pattern.sub( r'<a href="\1">\2</a>',value)
    #引用
    pattern = re.compile( r'\[quote\](.+?)\[/quote\]')
    value = pattern.sub( r'<blockquote>\1</blockquote>',value)
    
    #附件
    file = re.compile(r'\[file\](.+?)\[/file\]')
    value = re.sub( file, get_attachment_file_url,value )
    #代码高亮
    value = value.replace(u'[code]',u'<div class="code"><pre class="prettyprint">')
    value = value.replace(u'[/code]',u'</pre></div>')
    
    
    return value
"""
预览方式内容转换为html
"""
def minitohtml(value):
    #处理<实现过滤HTML已经安全标签
    value = value.replace(u'<',u'&lt;')


    #加粗
    value = value.replace(u'[b]',u'<b>')
    value = value.replace(u'[/b]',u'</b>')
    #图片
    pattern = re.compile( r'\[img\](.+?)\[/img\]')
    value = pattern.sub( r'<img src="\1">',value)
    pattern = re.compile( r'\[img=(.+?)\](.+?)\[/img\]')
    value = pattern.sub( r'<img src="\1" alt="\2">',value)    
    #url
    pattern = re.compile( r'\[url\](.+?)\[/url\]')
    value = pattern.sub( r'<a href="\1">\1</a>',value)
    pattern = re.compile( r'\[url=(.+?)\](.+?)\[/url\]')
    value = pattern.sub( r'<a href="\1">\2</a>',value)
    #引用
    pattern = re.compile( r'\[quote\](.+?)\[/quote\]')
    value = pattern.sub( r'<blockquote>\1</blockquote>',value)
    
    #附件
    file = re.compile(r'\[file\](.+?)\[/file\]')
    value = re.sub( file, get_mini_attachment_file_url,value )
    
    
    return value



cached = functools.partial(cache.cached,
                           unless= lambda: g.user is not None)



def render_template(template, **context):
    context = rt( template, **context)
    context = re.sub(r'>\s+?<', '><', context)
    context = re.sub(r'>\s+', '>', context)
    context = re.sub(r'\s+<', '<', context)
    return context


def timesince(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    NB: when/if Babel 1.0 releaseduse format_timedelta/timedeltaformat instead
    """
    
    if default is None:
        default = u""

    now = datetime.utcnow()
    diff = now - dt
    '''
    years = dt.days / 365
    months = dt.days / 30
    weeks = dt.days / 7
    days = dt.days
    hours = dt.seconds / 3600
    minutes = dt.seconds / 60
    seconds = dt.seconds 
    if diff.days > 3:
        default = dt
    '''
    
    return friendly_time( dt )


def domain(url):
    """
    Returns the domain of a URL e.g. http://reddit.com/ > reddit.com
    """
    rv = urlparse.urlparse(url).netloc
    if rv.startswith("www."):
        rv = rv[4:]
    return rv
def md5( str ):
    """
    MD5加密字符串函数
    """
    m = hashlib.md5()
    m.update( str )
    return m.hexdigest()
"""
MD5加密字符串函数
"""
def for_tags( str ):
    tag = str.split(",")
    html = ''
    for t in tag:
        if t != '':#去除最后一个逗号产生的空TAG
            html += "<a href='"+url_for("tags.view", slug=t)+"'class='post-tag' title='"+t+"' rel='tag'>"+t+"</a>"
    return html
"""
获取头像路径
"""
def avatar_url( str ):
    return "/static/avatar/"+str
