#! /usr/bin/env python
#coding=utf-8

import sqlite3
import re
def delete_repeat_user(table_name="search1"):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("Delete from '%s' where u_id not in (select max(u_id) from '%s' group by id)" % (table_name,table_name))
    con.commit()
    
    cur.close()
    con.close()
    #print "success!"
    
def deapSearch(gender,province="",city=""):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("select name,id,gender,location,province,city from search1 where gender='%s'and province='%s'and city='%s' " % (gender,province,city))
    con.commit()
    data=cur.fetchall()
    return data

def searchByName(name):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    name="%"+name+"%"
    #print name.decode("utf-8").encode("gb2312")
    cur.execute("select name,id,gender,province,city from search1 where name like '%s' " % name)
    con.commit()
    data=cur.fetchall()
    cur.close()
    con.close()
    return data

def searchByKey(name,gender,province,city):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    name="%"+name+"%"

    limit=[name,gender,u" ",province,u" ",city,u" "]

    #sqllimit="where name like '%s' and gender = '%s' and province='%s' and city='%s'"
    sqllimit="where name like '%s' and gender in ('%s','%s') and province in ('%s','%s') and city in ('%s','%s')"
    if gender == "" or gender == u"<空>":
        sqllimit=re.sub(r" and gender in \('%s','%s'\)","",sqllimit)
        del limit[1]
        del limit[1]
    if province == "" or province == u"<空>":
        sqllimit=re.sub(r" and province in \('%s','%s'\)","",sqllimit)
        if len(limit) == 7:
            del limit[3]
            del limit[3]
        else:
            del limit[1]
            del limit[1]
            
    if city == "" or city == u"<空>":
        sqllimit=re.sub(r" and city in \('%s','%s'\)","",sqllimit)
        if len(limit) ==7:
            del limit[5]
            del limit[5]
        elif len(limit) ==5:
            del limit[3]
            del limit[3]            
        else:
            del limit[1]
            del limit[1]
    '''
    tup=[name]
    limit=limit[1:]
    for value in limit:
        tup.append(value.encode("utf-8"))
        print
    '''
    sql="select name,id,gender,province,city from search1 " + sqllimit % tuple(limit)
    cur.execute(sql)
    con.commit()
    data=cur.fetchall()
    cur.close()
    con.close()    
    return data
    
#delete_repeat_user()
#print searchByKey("李龙","m","f",'')




    
