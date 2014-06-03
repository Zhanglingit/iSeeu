#! /usr/bin/env python
#coding=utf-8

from tiny_blog.tblog import *
import json
import sqlite_op

class api163():
    def __init__(self):
        self.app_key="TxWifxpJMI1INSF5"
        self.app_secret="eIRGAlCK0xUEqjf0OsmRmt1iLSLVaaCQ"
        self.oauth_token_secret="12a32762e9bc278fccad84f6d4fd6d02"
        self.oauth_token="e58d3a2be45edd7fcad5e4c19d5608c1"
        
        self.t = TBlog(self.app_key, self.app_secret)
        self.t.set_access_token(self.oauth_token_secret,self.oauth_token)
        
        self.sql_op=sqlite_op.sqlite_op()
        
    def users_search(self,q,page=1,per_page=20):
        params={"q":q,
                "page":str(page),
                "per_page":str(per_page)}
        data= json.loads(self.t.users_search(params))
        self.sql_op.insert_163_data(data)
        return data
    
        
if __name__=="__main__":
    test=api163()
    test.sql_op.delete_all()
    #key=raw_input("key: ")
    for i in range(1,2):
        res=test.users_search(q="df",page=i)
        test.sql_op.insert_163_data(res)
        res=json.dumps(res)
        f=file("get_result_"+str(i)+".txt","w")
        f.write(res)
        f.close()
    print "end"