#! /usr/bin/evn python
#coding = utf-8
import sqlite3, re

class renren_sql():
    def __init__(self):
        self.con = sqlite3.connect("renren.db")
        self.cur = self.con.cursor()
        
    def create_table(self,tablename='renren'): 
        self.cur.execute('CREATE TABLE IF NOT EXISTS %s (\
                        u_id INTEGER PRIMARY KEY autoincrement,\
                        name text,\
                        uid integer,\
                        sex text,\
                        birthday text,\
                        mainurl text,\
                        country text,\
                        province text,\
                        city text,\
                        company_name text,\
                        description text,\
                        start_date text,end_date text,\
                        university_name text,university_year text,\
                        hs_name text,hs_year text)' % tablename)
        self.con.commit

    def insert_value(self,data,tablename='renren'):
        #data dict
        #print data
        values = ''
        lists = ''
        for key,value in data.items():
            lists += "%s," % key
            values += "'%s'," % value
        
        sql = "insert into %s(" % tablename +lists[:-1]+ ") values("  + values[:-1]  + ") "
        #print "sql:",type(sql)
        
        self.cur.execute(sql)
        self.con.commit()
    
    def get_part_value(self,name,index,tablename='renren'):
        #print "get..."
        name = "%" + name + "%"
        sql = "select name,uid,sex,province,city from %s where name like '%s'" % (tablename, name)
        self.cur.execute(sql)
        self.con.commit()
        
        if index <> 0:
            self.cur.fetchmany(index)
            
        newretval = []
        retval = self.cur.fetchall()
        for i in range(len(retval)):
            newtuple = []
            for j in range(len(retval[i])):
                if retval[i][j] == None:
                    newtuple.append(u' ')
                else:
                    newtuple.append(retval[i][j])
            newtuple.append("renren.com")
            newretval.append(newtuple)
        return newretval
        
    def get_all_value(self,uid,tablename='renren'):
        sql = "select * from %s where uid='%s'" % (tablename, uid)
        self.cur.execute(sql)
        self.con.commit()
        retval = self.cur.fetchall()
        if retval == [] :return None
        newtuple = []
        for i in range(len(retval[0])):
            if retval[0][i] == None:
                newtuple.append(u' ')
            else:
                newtuple.append(retval[0][i])
                
        retval.append((newtuple))
        return retval[1]      
         
    def delete_all_value(self,tablename='renren'):
        self.cur.execute("delete from %s" % tablename)
        self.con.commit()
        
    def searchByKey(self,name,gender,province,city):
        name="%"+name+"%"
        limit=[name,gender,u" ",province,u" ",city,u" "]
        sqllimit="where name like '%s' and sex in ('%s','%s') and province in ('%s','%s') and city in ('%s','%s')"
        
        if gender == "" or gender == u'<\u7a7a>':
            sqllimit=re.sub(r" and sex in \('%s','%s'\)","",sqllimit)
            del limit[1]
            del limit[1]
        if province == "" or province == u'<\u7a7a>':
            sqllimit=re.sub(r" and province in \('%s','%s'\)","",sqllimit)
            if len(limit) == 7:
                del limit[3]
                del limit[3]
            else:
                del limit[1]
                del limit[1]
                
        if city == "" or city == u'<\u7a7a>':
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
        sql="select name,uid,sex,province,city from renren " + sqllimit % tuple(tup)
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
            newtuple.append("renren.com")
            newretval.append(newtuple)
        return newretval
    
if __name__ == "__main__":
    test = renren_sql()
#    test.create_table("renren")
    #name = raw_input("name: ")
    name = '\xbb\xc6\xbd\xa1\xcf\xe8'
    print test.get_part_value(name, 0)
    #print test.get_all_value(700514594)
    #test.insert_value({"name":"Lee","uid":"2343434","sex":"female"},"renren")

