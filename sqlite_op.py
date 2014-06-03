#! /usr/bin/env python
#coding=utf-8

import sqlite3,time
import re
class sqlite_op():
    def __init__(self):
        #self.logfile=log_stream.log_stream("sqlite_op")
        self.con = sqlite3.connect('./sina.db')
        self.cur = self.con.cursor()
        
    def __del__(self):
        #self.cur.execute("DROP table IF EXISTS sina_users")
        #self.con.commit()
        
        self.cur.close()
        self.con.close()
        
        
    def searchByKey(self,name,gender,province,city):
        name="%"+name+"%"
        limit=[name,gender,u" ",province,u" ",city,u" "]
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
        #'''
        tup=[name]
        limit=limit[1:]
        for value in limit:
            tup.append(value.encode("utf-8"))
        #'''
        sql="select name,id,gender,province,city from sina_users " + sqllimit % tuple(tup)
        self.cur.execute(sql)
        self.con.commit()
        retval=self.cur.fetchall()
        newretval = []
        for i in range(len(retval)):
            newtuple = []
            for j in range(len(retval[i])):
                if retval[i][j] == None:
                    newtuple.append(u' ')
                else:
                    newtuple.append(retval[i][j])
            newtuple.append("sina.com.cn")
            newretval.append(newtuple)
        return newretval
        
    
    def delete_repeat_user(self,table_name="sina_users"):
        self.cur.execute("Delete from '%s' where u_id not in (select min(u_id) from '%s' group by id)" % (table_name,table_name))
        self.con.commit()
        '''
        bIsSuc = False
        while not False:
            try:
                self.cur.execute("Delete from '%s' where u_id not in (select min(u_id) from '%s' group by id)" % (table_name,table_name))
                self.con.commit()
                bIsSuc = True
            except:
                time.sleep(1)'''
        #print "success!"
    
    def deapSearch(self,gender,province="",city=""):
        self.cur.execute("select name,id,gender,location,province,city from sina_users where gender='%s'and province='%s'and city='%s' " % (gender,province,city))
        self.con.commit()
        data=self.cur.fetchall()
        return data

    def searchByName(self,name):
        name="%"+name+"%"
        #print name.decode("utf-8").encode("gb2312")
        self.cur.execute("select name,id,gender,province,city from sina_users where name like '%s' " % name)
        self.con.commit()
        retval=self.cur.fetchall()
        newretval = []
        for i in range(len(retval)):
            newtuple = []
            for j in range(len(retval[i])):
                if retval[i][j] == None:
                    newtuple.append(u' ')
                else:
                    newtuple.append(retval[i][j])
            newtuple.append("sina.com.cn")
            newretval.append(newtuple)
        return newretval
        
    def searchByNameIndex(self,name,index):
        name="%"+name+"%"
        #print name.decode("utf-8").encode("gb2312")
        #self.cur.execute("select name,id,gender,province,city from sina_users where name like '%s' and u_id > %s" % (name,index))
        self.cur.execute("select name,id,gender,province,city from sina_users where name like '%s'" % (name))
        self.con.commit()
        if index <> 0 :
            self.cur.fetchmany(index)
        retval=self.cur.fetchall()
        
        newretval = []
        for i in range(len(retval)):
            newtuple = []
            for j in range(len(retval[i])):
                if retval[i][j] == None:
                    newtuple.append(u' ')
                else:
                    newtuple.append(retval[i][j])
            newtuple.append("sina.com.cn")
            newretval.append(newtuple)
        return newretval
    
    def searchById(self,id):
        self.cur.execute("select name,id,gender,province,city,profile_image_url,domain,description,status,created_at,friends_count from sina_users where id = %s" % id)
        self.con.commit()
        retval=self.cur.fetchall()
            
        return retval
        
    
    def insert_163_data(self,data,dbname='sina_users'):
        #data列表中的字典
        if data==None:return
        try:
            print data[u'error_code']
            return 
        except:
            for value in data:
                try:
                    print value["error"]
                    return
                except:
                    location=['','']
                    if value['location']<>"":
                        location[0],location[1]=value['location'].split(',')   #列表
                    gender=""
                    if value["gender"] == '1':
                        gender="男"
                    elif value["gender"]=='2':
                        gender="女"
                    for key,val in value.items():
                        if val==None:
                            value[key]=""                        
                    self.cur.execute("insert into sina_users(id,name,location,description,gender,domain,\
                                    province,city,statuses_count,friends_count,profile_image_url,created_at,status) \
                                    values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (value["id"],
                                    value["name"],value["location"],value["description"],gender.decode('utf8'),value["url"],
                                    location[0],location[1],value["statuses_count"],value["friends_count"],value["profile_image_url"],value["created_at"],value["status"]))
                    self.con.commit()   
        
    def delete_all(self,dbname='sina_users'):
        self.cur.execute('delete from %s' % dbname)
        self.con.commit()

    def delete_bytype(self,dbname='user_status', type="host_id", value=""):
        try:
            sql = "delete from %s where %s=%d" % (dbname, type, int(value))
            self.cur.execute(sql)
            self.con.commit()
        except Exception,e:
            #print e
            sql = "delete from %s where %s='%s'" % (dbname,type,value)
            print sql
            self.cur.execute(sql)
            self.con.commit()

    #新浪微博数据获取
    def get_sinaweibo (self, index):
        sql = "select user_id,user_name,id,status,user_location,comment,rt from status"
        self.cur.execute(sql)
        self.con.commit()
        result = []
        if index <> 0:
            self.cur.fetchmany(index)
        result = self.cur.fetchall()
        newret = []
        for i in range(len(result)):
            new = []
            for j in range(len(result[i])):
                new.append(result[i][j])
            new.append("sina.com.cn")
            newret.append(new)
        return newret
        
    def get_sina_userwb (self, index, id):
        sql = "select status, created_at from user_status where user_id =%d" % int(id)
        self.cur.execute(sql)
        self.con.commit()
        if index >0:
            self.cur.fetchmany(index)
        ret = self.cur.fetchall()
        newret =[]
        for i in range(len(ret)):
            new = []
            new.append(ret[i][0] + "(" + ret[i][1] + ")")
            newret.append(new)

        return newret
        
    def get_sina_userfd (self, index, id):
        #sql = "select profile_image_url,id,name,gender,location,friends_count,status_text from friends where host_id =%d" % int(id)
        sql = "select id,name,gender,location,friends_count,status_text from friends where host_id =%d" % int(id)
        #print sql
        self.cur.execute(sql)
        self.con.commit()
        if index <>0:
            self.cur.fetchmany(index)
        return self.cur.fetchall()
    #根据id获取
    def get_sinawb_byid (self, sid):
        sql = "select status from status where id = %s" % sid
        #print sql
        self.cur.execute(sql)
        self.con.commit()
        return self.cur.fetchall()        
    
class MatchSql():
    def __init__ (self):
        self.scon = sqlite3.connect('./sina.db')            #sina
        self.fcon = sqlite3.connect('./facebook.db')        #facebook
        self.tcon = sqlite3.connect('./twitter.db')         #twitter

        self.scur = self.scon.cursor()
        self.fcur = self.fcon.cursor()
        self.tcur = self.tcon.cursor()
        
        self.NAME_DATA = []
        self.NAME_SEX_DATA = []        
        self.STATUS_DATA = []
        self.STATUS_NAME_DATA = []
        
    def __del__ (self):
        self.scur.close()
        self.fcur.close()
        self.tcur.close()

        self.scon.close()
        self.fcon.close()
        self.tcon.close()

    def match_name (self):
        #{"name":'Lee', 'sina':1, 'facebook':1, 'twitter':1}
        #{"name":'Lee', 'sex':'female', 'sina':1, 'facebook':1, 'twitter':1}
        sql = "select name, gender from sina_users"
        try:
            self.scur.execute(sql)
            self.scon.commit()
        except Exception,e:
            print "match name get sina data error:", e
        sina_data = self.scur.fetchall()
        #print "sina_data:",sina_data
        #print "--------------------------------------"
        sql = "select name,gender from facebook_users"
        try:
            self.fcur.execute(sql)
            self.fcon.commit()
        except Exception,e:
            print "match name get facebook data error:", e
        facebook_data = self.fcur.fetchall()
        #print "facebook_data",facebook_data
        #print "--------------------------------------"
        sql = "select name from twitter_users"
        try:
            self.tcur.execute(sql)
            self.tcon.commit()
        except Exception,e:
            print "match name get twitter data error:", e
        twitter_data = self.tcur.fetchall()
        #print "twitter_data",twitter_data
        #print "--------------------------------------"
        
        for i in range(len(sina_data)):
            name_data_dict = dict()
            name_sex_data_dict = dict()  
            namecnt = 0
            namesexcnt = 0
            namecnt_tw = 0            
                      
            sina_one_data = sina_data[i]        #only one sina_data

            for fb in facebook_data:            #fb one data
                if sina_one_data[0] == fb[0]:                       
                    namecnt += 1
                    #print "sina and facebook match name", namecnt, 'times'
                    if sina_one_data[1] == fb[1]:                            
                        namesexcnt += 1
                        #print "sina and facebook  match name and sex", namesexcnt, 'times'
                        
            for tw in twitter_data:
                if sina_one_data[0] == tw[0]:
                    namecnt_tw += 1
                    #print "sina and twitter match name", namecnt_tw, 'times'
            
            if namecnt > 0 or namesexcnt > 0:
                name_data_dict['name']=sina_one_data[0]
                name_data_dict['sina'] = 1
                name_data_dict['facebook'] = namecnt
                name_data_dict['twitter'] = namecnt_tw
                
            if namesexcnt > 0:
                name_sex_data_dict['name']=sina_one_data[0]
                name_sex_data_dict['sex']=sina_one_data[1]
                name_sex_data_dict['sina'] = 1
                name_sex_data_dict['facebook'] = namesexcnt
                name_sex_data_dict['twitter'] = 0
            if name_data_dict <> {}:
                self.NAME_DATA.append(name_data_dict)
            if name_sex_data_dict <> {}:
                self.NAME_SEX_DATA.append(name_sex_data_dict)
    
    def match_status (self):
        #{"status":'i will kill you', 'sina':1, 'facebook':1, 'twitter':1}
        #{"name":'Lee', 'status':'i will kill you', 'sina':1, 'facebook':1, 'twitter':1}
        sql = "select status, user_name from status"
        try:
            self.scur.execute(sql)
            self.scon.commit()
        except Exception,e:
            print "match name get sina data error:", e
        sina_data = self.scur.fetchall()
        #print "sina_data:",sina_data
        #print "--------------------------------------"
        sql = "select message, user_name from facebook_status"
        try:
            self.fcur.execute(sql)
            self.fcon.commit()
        except Exception,e:
            print "match name get facebook data error:", e
        facebook_data = self.fcur.fetchall()
        #print "facebook_data",facebook_data
        #print "--------------------------------------"
        sql = "select status, user_name from twitter_status"
        try:
            self.tcur.execute(sql)
            self.tcon.commit()
        except Exception,e:
            print "match name get twitter data error:", e
        twitter_data = self.tcur.fetchall()
        #print "twitter_data",twitter_data
        #print "--------------------------------------"
        
        for i in range(len(sina_data)):
            name_data_dict = dict()
            name_sex_data_dict = dict()  
            namecnt = 0
            namesexcnt = 0
            namecnt_tw = 0            
            namesexcnt_tw = 0
            sina_one_data = sina_data[i]        #only one sina_data

            for fb in facebook_data:            #fb one data
                if sina_one_data[0] == fb[0]:                       
                    namecnt += 1
                    #print "sina and facebook match status", namecnt, 'times'
                    if sina_one_data[1] == fb[1]:                            
                        namesexcnt += 1
                        #print "sina and facebook  match name and status", namesexcnt, 'times'
                        
            for tw in twitter_data:
                if sina_one_data[0] == tw[0]:
                    namecnt_tw += 1
                    #print "sina and twitter match status", namecnt_tw, 'times'
                    if sina_one_data[1] == tw[1]:
                        namesexcnt_tw += 1
                        #print "sina and twitter  match name and status", namesexcnt, 'times'
            
            if namecnt > 0 or namesexcnt > 0:
                name_data_dict['status']=sina_one_data[0]
                name_data_dict['sina'] = 1
                name_data_dict['facebook'] = namecnt
                name_data_dict['twitter'] = namecnt_tw
                
            if namesexcnt > 0 or namesexcnt_tw > 0:
                name_sex_data_dict['status']=sina_one_data[0]
                name_sex_data_dict['name']=sina_one_data[1]
                name_sex_data_dict['sina'] = 1
                name_sex_data_dict['facebook'] = namesexcnt
                name_sex_data_dict['twitter'] = 0
            if name_data_dict <> {}:
                self.STATUS_DATA.append(name_data_dict)
            if name_sex_data_dict <> {}:
                self.STATUS_NAME_DATA.append(name_sex_data_dict)
        
        
if __name__=="__main__":
    '''
    mysql=sqlite_op()
    result=mysql.searchByNameIndex("李龙",10)
    print result
    for da in result:
        print da[0].encode("gbk")
        
    print len(result)
    '''
    #test = sqlite_op()
    #print test.get_sina_userwb(0,1865518130)
    
    test = MatchSql()
    #test.match_name()
    #print test.NAME_DATA
    #print test.NAME_SEX_DATA
    #print "--------------------------------"
    test.match_status()
    print test.STATUS_DATA
    print test.STATUS_NAME_DATA




    
