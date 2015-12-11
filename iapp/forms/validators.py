from flaskext.wtf import regexp

from flaskext.babel import lazy_gettext as _

USERNAME_RE = r'^[\w.+-]+$'

is_username = regexp(USERNAME_RE, 
                     message=u'您只能使用字母，数字或破折号')


