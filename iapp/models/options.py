# -*- coding: utf-8 -*-
'''
设置选项
'''

from flaskext.sqlalchemy import BaseQuery

from iapp.extensions import db
'''
配置信息
'''
class OptionsQuery(BaseQuery):
    def get_config(self):
        config = {}
        for c in self.all():
            config[c.name] = c.value
        return config
        
    def jsonify(self):
        for post in self.all():
            yield post.json



class Options(db.Model):

    __tablename__ = "options"

    query_class = OptionsQuery
    
    id = db.Column(db.Integer, primary_key=True)
    #配置名称
    name = db.Column(db.Unicode(256))
    
    #配置内容
    value = db.Column(db.Unicode(256))

 

    def __init__(self, name, value ):
        self.name = name
        self.value = value 
'''
init:
open_signup = 'on'  #开发注册

'''