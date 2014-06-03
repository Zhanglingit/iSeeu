#! /usr/bin/env python
#coding=utf-8

import threading,time,wx,thread,sys
import sina_sdk,sqlite_op
import api_163_usage,iseeu_renren_api
import twitter, facebook

class searchThread():
    lock=threading.RLock()
    def __init__(self,key,index,nPreApiNun,nWhichThread,getPageCnt,nPageCnt):
        'key:关键字；index：判断用哪个网站的api；nPreApiNun：每种api的线程数;\
        nWhichThread:第几个线程;getPageCnt:已获得页数'
        self.bIsChiThreadDead = False
        self.key=key
        self.index=index
        self.nPreApiNun=nPreApiNun
        self.nWhichThread=nWhichThread
        self.curpage= 1
        
        
        self.getPageCnt=getPageCnt
        self.nPageCnt=nPageCnt
        
        #开线程
        self.sth=thread.start_new_thread(self.run ,(index,))
        
    def run(self, index):
        if index==0:
            self.api=sina_sdk.myapi()
        elif index==2:
            self.api_twitter=twitter.Api()
        elif index==3:
            self.api_facebook = facebook.FacebookApi()
        elif index==1:
            self.renren = iseeu_renren_api.iseeu_api_xn()
            self.curpage= 0
        
        nAllPageCount = self.nPageCnt      
        self.nPreThPageCount=int(nAllPageCount / self.nPreApiNun) #每个线程处理多少页
        if self.index == 1:   
            self.nPreThPageCount = 50 / self.nPreApiNun
        if self.index == 2:
            self.nPreThPageCount = 10 / self.nPreApiNun

        while self.curpage <= self.nPreThPageCount:
            now=time.time()
            
            if self.index == 0:                                  #sina_api
                if self.api.imputdata(self.key,self.curpage + (self.nWhichThread - 1)*self.nPreThPageCount)=="iseeu_nodata_again":
                    self.getPageCnt[0] += (self.nPreThPageCount - self.curpage)+1
                    break
                
            elif self.index == 1:                                #renren
                #if self.nWhichThread == 2:time.sleep(1)
                self.renren.users_search(self.key,self.curpage+(self.nWhichThread - 1)*self.nPreThPageCount)
                
                
            elif self.index == 2:                                #twitter_api
                try:
                    self.api_twitter.Search_users(q=self.key,page=self.curpage+(self.nWhichThread - 1)*self.nPreThPageCount)
                except Exception,e:
                    print "-------------------twitter error",e
                    pass
            
            if(self.bIsChiThreadDead==True): 
                print "kill","api",self.index,"thread",self.nWhichThread
                thread.exit()
            searchThread.lock.acquire()
            self.getPageCnt[0] += 1
            searchThread.lock.release()
            last=time.time()
            #print "Api",self.index,"Thread",self.nWhichThread,"page",self.curpage,"use time",last-now,'all page:',self.getPageCnt[0] 
            self.curpage += 1
            #print "api",self.index,"thread",self.nWhichThread,"exit"
        #Facebook 
        if self.index == 3:                                #facebook_api
            try:
                self.api_facebook.get_users(self.key)
            except Exception,e:
                print "-------------------facebook error",e     
    

class BeCallByIseeu():
    def __init__(self):
        self.nAllChiTh=0      #所有子线程的数目
        self.sqlOp=sqlite_op.sqlite_op()    #创建sql对象用以最后删除重复项
        self.getPageCnt=[0]     #保存返回页数     
        self.errTime=140
        
    def __del__(self):
        pass  
    
    def SearchByBtn(self,key,nPreApiNum=4,nPageCnt=100, fb=False, tw=False):
        'nThreadNum:总线程数；nPreApiNun：每种api的线程数'
        #创建多个线程
        self.thSeas=[]
        itd = 0
        for i in range(1,nPreApiNum+1):
            #新浪
            thSea=searchThread(key,0,nPreApiNum,i,self.getPageCnt,nPageCnt)
            self.thSeas.append(thSea)
            itd += 1
            #网易
            #thSea=searchThread(key,2,nPreApiNum,i,self.getPageCnt,nPageCnt)
            #thSea.start()
            #可添加其他api的线程
            #人人网
            thSea = searchThread(key,1,nPreApiNum,i,self.getPageCnt,nPageCnt)
            self.thSeas.append(thSea)
            itd += 1
            #twitter
            if tw:
                thSea = searchThread(key,2,nPreApiNum,i,self.getPageCnt,nPageCnt)
                self.thSeas.append(thSea)
                itd += 1
        if fb:     #Facebook
            thSea = searchThread(key,3,nPreApiNum,i,self.getPageCnt,nPageCnt)
            self.thSeas.append(thSea)
            itd += 1
        print "All Td:",itd
        self.nAllChiTh = itd                #nPreApiNum*itd
        #等待线程结束,超时退出
        
    def SetChiThdPro(self,cnt):
        self.getPageCnt[0]=0
    def GetChiThdPro(self):
        return self.getPageCnt[0]
            
    def SetChiDeaFlag(self,flag):
        '设置子线程是否结束参数，True为结束，False为Alive'
        for i in range(0,self.nAllChiTh):     
            self.thSeas[i].bIsChiThreadDead= flag
            

class WeiboMulTd():
    lock=threading.RLock()
    pages_got = 0
    def __init__ (self, key, pages, tdnum, type):
        'pages:总页数,tdnum:线程数'
        print "need pages",pages, "using thread:",tdnum, "type:", type
        self.pages = pages
        self.key = key                  #关键字
        self.bTmExit = False            #是否退出线程
        WeiboMulTd.pages_got = 0                  #以获取到的页数
        page_pre_td = pages/tdnum       #每个线程页数
        self.prepg = page_pre_td
        page_ls_td = page_pre_td        #最后一个线程处理页数
        if pages%tdnum <> 0:
            page_ls_td = pages - (page_pre_td*tdnum)
            tdnum += 1
        print "pre thread pages",page_pre_td, "last thread pages:",page_ls_td
        if type == 3:                   #Facebook
            tdnow = thread.start_new_thread(self.run, (1, page_ls_td, type))
        else:
            for i in range(tdnum):
                if i < tdnum-1:
                    tdnow = thread.start_new_thread(self.run, (i+1, page_pre_td, type))
                else:
                    tdnow = thread.start_new_thread(self.run, (i+1, page_ls_td, type))
    
    def run (self, index, page_pre_td, type):
        if type == 1:
            sina_api = sina_sdk.myapi()
            start = 1 + (index-1)*self.prepg
            end = start + page_pre_td
            for i in range(start, end):
                if self.bTmExit:
                    print "*** weibo: td", index, "is dead." 
                    WeiboMulTd.pages_got += end-start-i
                    thread.exit()
                print "*** weibo: td", index, "page ", i, "is working." 
                if sina_api.trends_status(self.key, i) == 'iseeu_nodata_again':
                    print "*** weibo: td", index, "is dead." 
                    WeiboMulTd.pages_got += end-start-i
                    thread.exit()
                WeiboMulTd.lock.acquire()
                WeiboMulTd.pages_got += 1
                if(self.pages <= WeiboMulTd.pages_got): self.bTmExit = True
                WeiboMulTd.lock.release()
            print "*** weibo: td", index, "finish it's work." 
        elif type == 2:
            twitter_api = twitter.Api()
            start = 1 + (index-1)*self.prepg
            end = start + page_pre_td
            for i in range(start, end):
                if self.bTmExit:
                    print "***twitter_status: td", index, "is dead." 
                    thread.exit()
                print "*** twitter_status: td", index, "page ", i, "is working." 
                twitter_kong = None
                try:
                    #print repr(self.key)
                    twitter_kong=twitter_api.Search_status(q=self.key,page=i)
                except Exception,e:
                    print "twitter failed error:",e
                    pass
                if twitter_kong=="kong":
                    WeiboMulTd.pages_got += end-start-i
                    thread.exit()
                WeiboMulTd.lock.acquire()
                WeiboMulTd.pages_got += 1
                if(self.pages <= WeiboMulTd.pages_got): self.bTmExit = True
                WeiboMulTd.lock.release()
            print "*** twitter_status: td", index, "finish it's work." 
            
        elif type == 3:
            facebook_api = facebook.FacebookApi()
            if self.bTmExit:thread.exit()
            try:
                facebook_api.get_status(self.key)
            except Exception,e:
                print "facebook get status error:",e
            
        return True
       
    def GetProcess (self):
        return WeiboMulTd.pages_got        
        
    
if __name__=="__main__":
    #'''
    test=BeCallByIseeu()
    test.SearchByBtn('李龙',4)
    time.sleep(40)
    #'''
    #test = WeiboMulTd('西藏', 4, 2)
    #time.sleep(40)
    

 

