# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~~~

    Default configuration

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

from iapp import views

class DefaultConfig(object):
    """
    Default configuration for a newsmeme application.
    """
    
    DEBUG = True

    # change this in your production settings !!!

    SECRET_KEY = "secret"

    # keys for localhost. Change as appropriate.

    RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
    RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'

    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/42ic?charset=utf8"

    SQLALCHEMY_ECHO = False

    MAIL_DEBUG = DEBUG

    ADMINS = ()

    ADMINS = ('11939053@qq.com',)

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEBUG = DEBUG
    MAIL_USERNAME = '42ic.com'
    MAIL_PASSWORD = '42icb7y4g3'
    DEFAULT_MAIL_SENDER = '42ic.com@gmail.com'

    
    #ACCEPT_LANGUAGES = ['en_gb', 'zh']
    ACCEPT_LANGUAGES = ['en_gb', 'fi']
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

    DEBUG_LOG = 'logs/debug.log'
    ERROR_LOG = 'logs/error.log'
    
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = ''
	#统计
    GOOGLE_TRACKING_CODE = 'UA-24331000-1'
    #cache
    CACHE_REDIS_SERVERS = 'localhost'
    #CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB = 0
    #静态文件路径
    WEB_PATH = '/home/lyping/data/42ic/'
    if DEBUG:
        #路径
        #网站文件路径
        WEB_PATH = '/home/lyping/data/42ic/'
        STATIC_PATH = WEB_PATH+'static/'
        IMG_PATH = WEB_PATH+'img/'
        UPFILE_PATH = WEB_PATH+'iapp/static/uploads/'
        AVATAR_PATH = WEB_PATH+'iapp/static/avatar/'
        AVATAR_IMAGE_PATH = WEB_PATH+'iapp/static/avatar/'
        #各种URL
        APP_URL = 'http://127.0.0.1:5000/'
        IMG_URL = 'http://127.0.0.1:5000/static/img/'
        FILE_URL = 'http://127.0.0.1:5000/static/file/'
        #普通静态文件
        STATIC_DOMAIN = 'http://127.0.0.1:5000/static/'
        AVATAR_URL = 'http://127.0.0.1:5000/static/avatar/'
        UPFILE_URL = STATIC_DOMAIN+'uploads/'
    
    else:
        #路径
        #网站文件路径
        WEB_PATH = '/home/lyping/data/42ic/'
        STATIC_PATH = WEB_PATH+'static/'
        IMG_PATH = WEB_PATH+'img/'
        UPFILE_PATH = WEB_PATH+'iapp/static/uploads/'
        AVATAR_PATH = WEB_PATH+'iapp/static/avatar/'
        AVATAR_PATH = WEB_PATH+'iapp/static/avatar/'
        AVATAR_IMAGE_PATH = WEB_PATH+'iapp/static/avatar/'
        #各种URL
        APP_URL = 'http://www.42ic.com/'
        IMG_URL = 'http://www.42ic.com/static/img/'
        FILE_URL = 'http://www.42ic.com/static/file/'
        #普通静态文件
        STATIC_DOMAIN = 'http://www.42ic.com/static/'
        AVATAR_URL = 'http://www.42ic.com/static/avatar/'
        UPFILE_URL = STATIC_DOMAIN+'uploads/'
    

class TestConfig(object):

    TESTING = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ECHO = False




