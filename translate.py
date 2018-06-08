# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:00:53 2018

@author: hp
"""
import threading
import requests
from bs4 import BeautifulSoup
import pymysql
import json

def insert():#信息插入数据库
    global sqls
    while True:
        if len(sqls['info'])>50:#当待插入信息多于50条时，将表中信息插入数据库
            db=connect()
            cursor=db.cursor()
            sqlss=sqls
            for s in sqlss['info']:
                print(s)
                try:
                    cursor.execute(s)
                except:
                    pass
                sqls['info'].remove(s)#删除已插入信息
            db.commit()
            for s in sqlss['ot']:
                print(s)
                try:
                    cursor.execute(s)
                except:
                    pass
                sqls['ot'].remove(s)
            db.commit()
            db.close()
def getinfo(nm):#获取用户详细信息
    url='https://www.zhihu.com/api/v4/members/{name}?include=locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    urls=url.format(name=nm)
    sql="insert into info value('"
    req=requests.get(url=urls,headers=headers)
    rj=req.json()
    sql+=rj['id']+"',"
    sql+="'"+rj['name']+"',"
    try:
        sql+="'"+BeautifulSoup(rj['description'],'lxml').get_text()+"',"
    except:
        sql+='null,'
    try:
        sql+="'"+rj['headline']+"',"
    except:
        sql+='null,'
    sql+=str(rj['following_count'])+","
    sql+=str(rj['answer_count'])+","
    sql+=str(rj['gender'])+","
    sql+=str(rj['thanked_count'])+","     
    sql+=str(rj['question_count'])+","
    sql+=str(rj['favorited_count'])+","
    sql+=str(rj['articles_count'])+","
    try:
        sql+="'"+rj['locations'][0]['name']+"',"
        cjd=[]
        for k in rj['locations'][1:]:
            cjd.append(k['name'])
        if cjd!=[]:
            sql+="'"+'/'.join(cjd)+"',"
        else:
            sql+="null,"
    except:
        sql+='null,'
        sql+='null,'
    sql+=str(rj['follower_count'])+","
    try:
        sql+="'"+rj['business']['name']+"',"
    except:
        sql+='null,'
    sql+=str(rj['voteup_count'])+")"
    global sqls
    try:
        sqls['info'].append(sql)#将信息放入待插入数据库的列表中
        #insert(sql)
        try:
            for k in rj['educations']:
                sql="insert into jyjl value('"+rj['id']+"','"+k['school']['name']+"','"+k['major']['name']+"')"
                #insert(sql)
                sqls['ot'].append(sql)
        except:
            pass
        try:
            for k in rj['employments']:
                sql="insert into zyjl value('"+rj['id']+"','"+k['company']['name']+"','"+k['job']['name']+"')"
                #insert(sql)
                sqls['ot'].append(sql)
        except:
            pass
        offset=0
        gz=rj['following_count']
        fs=rj['follower_count']
        flurl='https://www.zhihu.com/api/v4/members/{name}/{tp}?offset={start}&limit=20'
        global fltb
        while offset<gz:
            fltb.append(flurl.format(name=nm,start=offset,tp='followees'))#将粉丝列表放入待爬取粉丝列表中
            offset+=20
        offset=0
        while offset<fs:
            fltb.append(flurl.format(name=nm,start=offset,tp='followers'))
            offset+=20   
    except:
        pass
def getfl(fu):
    flreq=requests.get(url=fu,headers=headers)
    flrj=flreq.json()['data']
    for fl in flrj:#遍历列表用户
        global ts
        print(len(ts),'\n')
        t=threading.Thread(target=getinfo,args=(fl['url_token'],))#获取用户详细信息
        t.setDaemon(False)
        t.start()
        ts.append(t)
        if len(ts)>40:#如果线程列表过大则清理已结束线程
            tts=[]
            for k in ts:
                if k.is_alive():
                    tts.append(k)
            ts=tts
        if len(ts)>60:#若清理后线程仍很多 则对后加入的线程进行阻塞处理，防止线程过多
            t.join()
def scra():#逐个进行用户粉丝列表信息的爬取
    global fltb
    while True:
        if len(fltb)>0:
            getfl(fltb[0])#获得粉丝列表
            fltb.pop(0)#删去已爬取的列表
def builddb(db):
    t="show tables like 'jyjl' "
    t1="show tables like 'zyjl' "
    t2="show tables like 'info' "#查询各个数据库是否已创建
    cursor = db.cursor()#0--flight  1--train
    a='create table info(mid varchar(50) primary key,姓名 varchar(20),个人简介 text,个性签名 text,关注数 int,回答数 int,性别 tinyint,感谢数 int, 提问数 int,收藏数 int,文章数 int,现居地 varchar(20),曾居地 varchar(40),粉丝数 int,行业 varchar(10),赞同数 int)'#用户基础信息
    b='create table zyjl(mid varchar(50),公司 varchar(30),职位 varchar(20),foreign key(mid) references info(mid))'#用户职业经历
    c='create table jyjl(mid varchar(50),学校 varchar(30),专业 varchar(20),foreign key(mid) references info(mid))'#用户教育经历 
    k=cursor.execute(t2)
    if(k==0):
        cursor.execute(a)
    k=cursor.execute(t)
    if(k==0):
        cursor.execute(c)
    k=cursor.execute(t1)
    if(k==0):
        cursor.execute(b)
    db.commit()
    db.close()
def connect():
    return pymysql.connect("127.0.0.1", "zhihu", "123456", "zhihu", charset='utf8' )
if __name__ == '__main__':
    global fltb
    fltb=[]#待爬取的用户粉丝信息url列表
    ts=[]#线程列表
    global sqls
    sqls={'info':[],'ot':[]}#存放sql语句
    db=connect()#连接数据库
    builddb(db)#创建数据库
    t=threading.Thread(target=insert)#开启定量插入数据库的线程
    t.start()
    t=threading.Thread(target=scra)#开启逐个获取用户粉丝列表的线程
    t.start()
    headers={
        'cookie':'_zap=2e16236b-aa8b-439a-afd0-45ad1270c724; __DAYU_PP=qBqQ2m7ranYyF7ZNiQUa201481a9452b; q_c1=e29bcd49132f4c698d86b9f0b76f3948|1525529299000|1508927675000; d_c0="ABAgSCM9jA2PTpC6dmuoJzyq-qyvtZLj4IM=|1525529567"; _xsrf=eca94ea7-4295-46e1-8fd4-2d011eedcf1f; l_n_c=1; l_cap_id="YWQ0Y2Q2NTI3MzgzNDkzYWJmODFiOGRlZDMyMzIxNTg=|1526792953|575e9d3378634db93d6b976d087f7985d683ef8d"; r_cap_id="MDg2YjExZmMyNzU5NDJkM2IwYTZlNmU1NzU0NGNmNGI=|1526792953|03c116345ec46afcb163beef3ae2ec96cf4601bd"; cap_id="MDliZDQzOWE0NzE1NDRjNjk5ZjFmNDE4YWJkNjNmMjE=|1526792953|f3d2b2a9e0da1a2ec35e9234db65aa4cb12f98e7"; n_c=1; tgw_l7_route=170010e948f1b2a2d4c7f3737c85e98c; capsion_ticket="2|1:0|10:1526815239|14:capsion_ticket|44:NDViMDE4YWI0MTAwNDcyYzg0YmNmZWYyM2U0ZjQwYjU=|ab5e96e1e383c860ca56979ab4ec022bbaff9c22cb9d7a0e23889e1a9bb7b212"; z_c0="2|1:0|10:1526815283|4:z_c0|92:Mi4xTkVEZEJRQUFBQUFBRUNCSUl6Mk1EU1lBQUFCZ0FsVk5NNmp1V3dCZS1lV2drSnlidDk5SzRxMUNBNVdyalJsZzdB|9db3daee9cf3a2862bb520aee61e45f902718fcb05fe6b491f3a82e28e78dedc"; unlock_ticket="ADCCyUzcUgwmAAAAYAJVTTthAVunC6XtqO71L_3fqSa5vVsMvOrGsg=="; appeal_cap_id=f2680de0eec04eb69e8faec0872f06b9',
        'user-agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
    getinfo('zhang-jia-wei')#从知乎上粉丝最多的张佳玮的个人信息开始爬取
