#coding:utf-8
import time
import sys
import MySQLdb
from sql_func import SQLfun



"""
执行方法

功能代码对照表
101=新用户注册
103=谁关注了谁

数据样式
queue.push(q_id,user_id,source_id)
q_id:操作代码
user_id:操作者ID
source_id:操作所需要的ID，比如topic_id等。。
"""

class Event_func:
    def __init__(self):
        self.db = MySQLdb.connect(host="localhost",user="root",passwd="",db="42ic")
        self.cm = self.db.cursor()
        self.sf = SQLfun()
    #通过一个用户ID和一个事件ID，将事件分发给关注他的用户
    #（用户ID，事件ID,事件操作码，事件简码）
    def po(self,user_id,event_id,event_type,event_mini_type):
        sql = self.sf.s_follower_user(user_id)
        self.cm.execute(sql)
        flist = self.cm.fetchall()
        for f in flist:
            sql = self.sf.i_event_user(event_id,event_type,event_mini_type,f[0])
            self.cm.execute(sql)
        #也给自己一条记录
        if self.is_po(user_id,event_id):
            sql = self.sf.i_event_user(event_id,event_type,event_mini_type,user_id)
            self.cm.execute(sql)          
    #关注问题用户分发
    #（用户ID，问题ID，事件ID,事件操作码，事件简码）
    def po_fq(self,user_id,q_id,event_id,event_type,event_mini_type):
        sql = self.sf.s_follower_question_user(q_id)
        self.cm.execute(sql)
        flist = self.cm.fetchall()
        for f in flist:
            if self.is_po(f[0],event_id):
                sql = self.sf.i_event_user(event_id,event_type,event_mini_type,f[0])
                self.cm.execute(sql)           
    #是否已经分发
    #（用户ID，事件ID）
    def is_po(self,user_id,event_id):
        sql = "SELECT  `id` FROM  `event_user` WHERE  `event_id` =%s AND `feed_user_id` =%s;"\
                % (event_id,user_id)
        self.cm.execute(sql)
        flist = self.cm.fetchone()
        if flist:
            return False
        else:
            return True








    #新用户注册通知
    #(101,注册用户的ID)
    def q_101(self,data):
        #插入一条事件记录
        sql = self.sf.i_event(data[1],101,data[1],u'加入42ic.com')  
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        #插入一条feed_user_id = 的公共广播
        sql = self.sf.i_event_user(eid,101,1,0)
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,101,1)
        self.db.commit()
        print 'ok'   
    
    #谁关注了谁
    #（103,关注者ID,被关注者ID，username,name）
    def q_103(self,data):  
        sql = self.sf.i_event(data[1],103,data[2],u'<a href="/people/'+data[3]+u'"title="'+data[4]+u'" class="Yk">'+data[4]+u'</a>')
        self.cm.execute(sql)
        eid = self.db.insert_id()
        #分发一下
        self.po(data[1],eid,103,1)
        #发给我关注的那人
        sql = self.sf.i_event_user(eid,103,1,data[2])
        self.cm.execute(sql)        
        self.db.commit() 
        print 'ok'   
    #增加用户威望
    #（201,用户ID,增加值）
    def q_201(self,data):  
        sql = "SELECT `prestige` FROM  `users` WHERE  `id` =%s;"% (data[1])
        self.cm.execute(sql)
        info = self.cm.fetchone()
        #增加威望
        prestige =info[0] + (data[2])
        #保存
        sql = "UPDATE  `42ic`.`users` SET  `prestige` =  '%s' WHERE  `users`.`id` =%s;"% (prestige,data[1])
        self.cm.execute(sql)        
        self.db.commit() 
        print 'ok' 
    #增加用户积分
    #（202,用户ID,增加值）
    def q_202(self,data):  
        sql = "SELECT `integral` FROM  `users` WHERE  `id` =%s;"% (data[1])
        self.cm.execute(sql)
        info = self.cm.fetchone()
        #增加威望
        integral =info[0] + (data[2])
        #保存
        sql = "UPDATE  `42ic`.`users` SET  `integral` =  '%s' WHERE  `users`.`id` =%s;"% (integral,data[1])
        self.cm.execute(sql)        
        self.db.commit() 
        print 'ok' 

    
    
    #谁提了问
    #（301,提问者,问题ID，问题标题，问题描述）
    def q_301(self,data):  
        sql = self.sf.i_event(data[1],301,data[2],data[3],data[4])
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,301,3)
        self.db.commit()
        print 'ok'   
    #谁回答了谁的问题
    #（302,回答者,问题ID，问题标题，答案描述）
    def q_302(self,data):  
        sql = self.sf.i_event(data[1],302,data[2],data[3],data[4])
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,302,3)
        self.po_fq(data[1],data[2],eid,302,3)
        self.db.commit() 
        print 'ok'   
    #谁关注了某个问题
    #（303,回答者,问题ID，问题标题，答案描述）
    def q_303(self,data):  
        sql = self.sf.i_event(data[1],303,data[2],data[3],data[4])
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,303,3)
        self.po_fq(data[1],data[2],eid,303,3)
        self.db.commit() 
        print 'ok'  


    #谁发布了话题
    #（501,发布者,话题ID，话题标题，话题描述）
    def q_501(self,data):  
        sql = self.sf.i_event(data[1],501,data[2],data[3],data[4])
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,501,5)
        self.db.commit() 
        print 'ok' 
    #谁回复了话题
    #（502,发布者,话题ID，话题标题，内容描述）
    def q_502(self,data):  
        sql = self.sf.i_event(data[1],502,data[2],data[3],data[4])
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,502,5)
        self.db.commit() 
        print 'ok' 
    #谁加入了小组
    #（503,用户ID,小组ID，小组urlname,小组name，小组描述）
    def q_503(self,data):  
        sql = self.sf.i_event(data[1],503,data[2],u'<a href="/group/'+data[3]+u'"title="'+data[4]+u'" class="Yk">'+data[4]+u'</a>',data[5])
        self.cm.execute(sql)
        eid = self.db.insert_id()#获取刚才这行的ID
        self.po(data[1],eid,503,5)
        self.db.commit() 
        print 'ok' 


 


if __name__ == '__main__':
    q = Efun()
    q.q_101(111)
