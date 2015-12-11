#coding:utf-8
import time
from datetime import datetime
"""
sql产生方法
"""
class SQLfun:
    def __init__(self):
        pass
    '''
    插入事件信息
    '''
    def i_event(self,user_id,event_type,event_msg_id,title='',description=''):
        title = title.replace(u"'",u'.')
        title = title.replace(u"`",u'.')
        description = description.replace(u"'",u'.')
        description = description.replace(u"`",u'.')

        sql = "INSERT INTO  `42ic`.`event` ( `id` , `user_id` , `event_type` , `event_msg_id` ,\
                    `title` , `description` , `date_created` )\
                    VALUES ( NULL ,  '%s',  '%s',  '%s',  '%s',  '%s',  '%s');"\
                    % (user_id,event_type,event_msg_id,title,description,datetime.now())
        return sql
    
    '''
    插入事件与用户的关联信息
    '''
    def i_event_user(self,event_id,event_type,event_type_mini,feed_user_id):
        sql = "INSERT INTO  `42ic`.`event_user` (`id` ,`event_id`,`event_type`,`event_type_mini`,`feed_user_id`)\
                    VALUES (NULL , '%s', '%s', '%s', '%s');" % (event_id,event_type,event_type_mini,feed_user_id)
        return sql
    
    
    '''
    根据用户ID，检索出关注他的人
    '''
    def s_follower_user(self,user_id):
        sql = "SELECT  `follower_id` FROM  `user_follow` WHERE  `main_id` =%s;"\
                % (user_id)
        return sql
    '''
    根据问题ID，检索出关注问题的人
    '''
    def s_follower_question_user(self,q_id):
        sql = "SELECT  `user_id` FROM  `question_follow` WHERE  `question_id` =%s;"\
                % (q_id)
        return sql

    





if __name__ == '__main__':
    pass
