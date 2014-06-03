#coding=utf-8

import urllib,urllib2,time,json,os
import api_xn,sql_renren
import ConfigParser
class iseeu_api_xn():
    def __init__ (self):
        
        self.API_KEY='9c7c640dda6845669c44231b3761e962'#'b24be2445dd94ab0a99d917e6a88c993'
        self.SECRET_KEY='6375b763e5f2420a98f66342d4b0d00d'#'690dec5d66b6410cbbf3a9c40d972743'
        
        #初始化
        api_xn.init_info(api_key=self.API_KEY,secret_key=self.SECRET_KEY)

        self.ren_sql = sql_renren.renren_sql()
        self.ren_sql.create_table("renren")
        #self.bGetId = [False]

        self.SESSION_KEY=api_xn.get_session_key(username='iseeu_deve@163.com',password='123456789iseeu')
        #api_xn.logout()
        
    def __del__(self):
        pass
        '''
        for i in range(0,51):
            if os.path.exists("data/renrenid"+str(i)+".txt"):
                os.remove("data/renrenid"+str(i)+".txt")
        '''
            
    def users_search(self,name,page):
        #获得ID,全部写入
        result=api_xn.searchonRenren(name,page)
        #下面实现请求分页
        #self.SESSION_KEY=api_xn.get_session_key(username='iseeu_deve@163.com',password='123456789isee')
        #f = file("data/renren.txt","a")    
        
        id = self.read_id(page)
        if os.path.exists("data/renrenid"+str(page)+".txt"):
            os.remove("data/renrenid"+str(page)+".txt")
            pass

        count = 0 
        ren_sql = sql_renren.renren_sql()
        for i in range(len(id)):
            result=api_xn.users_getInfo(api_key=self.API_KEY,session_key=self.SESSION_KEY,uids=id[i])
            
            if result.find(u'error_code'.encode('utf8')) >= 0:
                print "error_code"
                continue
            if result == '[]':
                continue            
            result = self.format_data(id[i],json.loads(result))                
            while 1:
                try:
                    ren_sql.insert_value(result,"renren")
                    break
                except:
                    time.sleep(1)
                    
            count += 1
            #print count 
        #f.close()
        return result

    def read_id (self,page):
        pathval="data/renrenid"+str(page)+".txt"
        while not os.path.exists(pathval):
            time.sleep(1)

        f = file("data/renrenid"+str(page)+".txt",'r')
        id = f.readlines()
        f.close()
        for i in range(len(id)):
            id[i] = id[i][:-1]
        return id
    
    def format_data(self,id,data):
        #print data
        if data==[]:
            return []
        data = data[0]      #dict
        newdata = {}
        del_list = "vip,headurl,star,tinyurl,zidou,email_hash"
        #print "dict len:",len(data)
        for key,value in data.items():
            if del_list.find(key) >= 0:
                #print '1',key
                continue
            elif key == 'sex':
                if value == 1:
                    newdata.setdefault(key,'男'.decode("utf8"))
                elif value == 0:
                    newdata.setdefault(key,'女'.decode('utf8'))
            elif key == "hometown_location" :
                #print '2',key
                for k,val in value.items():
                    newdata.setdefault(k,val)
            else:
                #print '3',key                
                newdata.setdefault(key,value)
        
        #cfg = ConfigParser.RawConfigParser()
        #cfg.read('data/idimg.temp')
        idimg = file('idimg.temp', 'r')
        url = idimg.read()
        idimg.close()
        urls = url.split('\n')
        url = {}
        for i in range(1,len(urls)):
            key = urls[i].split('=')
            #print "key1: ",key
            if key[0]<>'' and len(key) >= 2:
                #print "key2: ",key
                url.setdefault(key[0].strip(),key[1].strip())
                
#        print id, type(id)
        if str(id) in url.keys():
            url = url[str(id)]
            #print "renren-id:",url
        newdata.setdefault('mainurl',url)
        return newdata


if __name__ == "__main__":
    test = iseeu_api_xn()
    x=raw_input("name: ")
    for i in range(3):
        print "i:",i
        test.users_search(x.decode('gbk').encode('utf8'),i)
    '''
    data =[{"uid":221609669,
            "tinyurl":"http://hdn.xnimg.cn/photos/hdn411/20090724/2015/tiny_VRVP_29773b204234.jpg",
            "birthday":"1985-05-23","vip":1,"hometown_location":{"province":"吉林","city":"四平市"},
            "sex":0,"name":"黄茜",
            "mainurl":"http://hdn.xnimg.cn/photos/hdn111/20090724/2015/main_EYjL_29766b204234.jpg",
            "star":0,"email_hash":'null',
            "headurl":"http://hdn.xnimg.cn/photos/hdn111/20090724/2015/head_aOVo_29766b204234.jpg","zidou":0}]
    data =[{"uid":221609669,"tinyurl":"http://hdn.xnimg.cn/photos/hdn411/20090724/2015/tiny_VRVP_29773b204234.jpg","birthday":"1985-05-23","vip":1,"hometown_location":{},"sex":0,"name":"黄茜","mainurl":"http://hdn.xnimg.cn/photos/hdn111/20090724/2015/main_EYjL_29766b204234.jpg","star":0,"email_hash":"null","headurl":"http://hdn.xnimg.cn/photos/hdn111/20090724/2015/head_aOVo_29766b204234.jpg","zidou":0}]
    print test.format_data(data)
    '''