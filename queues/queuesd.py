# -*- coding: utf-8 -*-
#一个守护进程
#关闭方法：ps -ef 查看进程PID，然后再kill pid
#守护进程类
#from mydaemon import daemonize
from queue import Queue

#引入事件处理函数库
from event_func import Event_func

import time
import sys
q = Queue()

'''
函数分发
data:传入任务列表的数据
fun_id:函数功能码
'''
efun = Event_func()
def queue_run(data, fun_id):                              
    f = getattr(efun, "q_%s" % str(fun_id)) 
    return f(data)
'''
写错误日志
'''
def wlog(value):
    from time import localtime,strftime
    date=strftime("%Y%m%d",localtime())
    strLogfileName="/home/42ic/iapp/logs/queue-"+date+'.log'
    fp=open(strLogfileName,'w')
    fp.write('%s:::::%s/n'%(str(time.time()),value))
    fp.close()

def runapp():
    while 1:
        #获取记录
        qv = q.pop()
        if qv:
            print str(qv)
            try:
                queue_run(qv,qv[0])
            except:
                try:
                    global efun
                    efun = Event_func()
                    queue_run(qv,qv[0])
                except:
                    wlog(str(qv))

            '''
            try:
                print queue_run(qv,qv[0])
                print qv[0]
            except:
                print 'python error'
                print qv[0]
            '''
        #延时3秒
        
        time.sleep(1)
if __name__ == '__main__':

    runapp()




"""
def runapp():
    while 1==1:
        #获取记录
        q = queue.pop()
        if q:
            try:
                #按功能码运行函数
                queue_run(q,q[0])
            except:
                now = time.time()
                sys.stderr.write('ERROR: %s at:%s\n' % (str(q),now))
        #延时3秒
        time.sleep(3)
        '''
        now = time.time()
        if int(now) % 5 == 0:
            sys.stderr.write('Mod 5 at %s\n' % now)
        else:
            sys.stdout.write('No mod 5 at %s\n' % now)
        time.sleep(1)
        '''
if __name__ == '__main__':
    daemonize(stdout='/tmp/stdout.log', stderr='/tmp/stderr.log')
    runapp()
"""
