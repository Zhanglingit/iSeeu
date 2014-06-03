#! /usr/bin/env python
#coding=utf-8

import wx
import wx.richtext as rt
import wx.html as html
import match,iseeuMoreinfo
import time, sys, ConfigParser, os, threading, thread
import sqlite_op,sina_sdk,iseeuthread,menu, sql_renren, twitter, facebook
import baidu, urllib, urllib2
import shutil

timeoutval=0
threadcnt=0
pagecntval=0
pagetmval=0

def Eng2Zh(text):
    return text.decode("utf8").encode("gbk")

def delete_all_sql():
    print "*** start clear sqlite3"
    sinasql=sqlite_op.sqlite_op()
    rensql = sql_renren.renren_sql()
    twsql = twitter.Twitter_Sql()
    fbsql = facebook.Facebook_Sql()
    try:
        sinasql.delete_all()
    except:
        print "sina,No table"
    try:
        twsql.clear_all()
        print "clear twitter sql"
    except Exception,e:
        print "twitter,No table",e
    try:
        fbsql.clear_all()
        print "clear facebook sql"
    except Exception,e:
        print "facebook,No table",e
    try:
        rensql.delete_all_value()
    except:
        print "renren,No table"
    print "*** finish clear sqlite3"

def delete_wb_fd():
    sinasql=sqlite_op.sqlite_op()
    try:
        sinasql.delete_all("friends")           #清空用户好友
    except:
        pass
    try:
        sinasql.delete_all("user_status")       #清空用户微博
    except:
        pass
    try:
        sinasql.delete_all("status")            #清空微博
    except:
        pass
        
class StaticText(wx.StaticText):
    def __init__(self, parent, label):
        wx.StaticText.__init__(self, parent, -1, label=label, style=wx.CLIP_CHILDREN |wx.TRANSPARENT_WINDOW)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        evt.Skip()
        dc = wx.PaintDC(self)
        dc.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,
                              False, u'\u5fae\u8f6f\u96c5\u9ed1'))         
        #dc.SetFont(dc.GetFont())
        dc.DrawText(self.GetLabel(), 0, 0)
        
class AboutDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title=Eng2Zh("关于iSeeu"), size=(300,200))
        self.Center()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        '''
        vbox = wx.BoxSizer(wx.VERTICAL)
        title_stc = StaticText(self, Eng2Zh("iSeeu网络痕迹搜集V1.0"))
        #title_stc.SetFont()
        people_stc = StaticText(self, Eng2Zh("成员: 贺障霖、李龙、贾鹏、兰晓"))
        pow_stc = StaticText(self, Eng2Zh("版权: @2011- ?"))
        
        vbox.AddMany([(title_stc, 2, wx.EXPAND|wx.ALIGN_LEFT,5),
                    (people_stc, 1, wx.EXPAND|wx.ALIGN_LEFT,5),
                    (pow_stc, 1, wx.EXPAND|wx.ALIGN_LEFT,5)])
        self.SetSizer(vbox)'''
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        bk = wx.Image("image/about.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        '''
        dc.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD,False, u'\u5fae\u8f6f\u96c5\u9ed1'))
        dc.DrawText(Eng2Zh("iSeeu网络痕迹搜集V1.0"), 30, 10)
        dc.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,False, u'\u5fae\u8f6f\u96c5\u9ed1'))
        dc.DrawText(Eng2Zh("成员: 贺障霖、李龙、贾鹏、兰晓"), 30, 60)
        dc.DrawLine(65,80,220,80)
        dc.DrawText(Eng2Zh("版权: ")+"2011", 30, 80)
        dc.DrawText(Eng2Zh("功能: "), 30, 100)
        '''
        dc.DrawBitmap(bk, 0, 0)
        evt.Skip()
        
class iSeeu_Main_Frame(wx.Frame):
    def __init__(self, parent, title="iSeeu"):
        #载入配置文件
        self.__CONFIG_FILE="iseeuConfig.ini"
        if not os.path.exists(self.__CONFIG_FILE):
            wx.MessageBox("缺少配置文件，请检查是否.ini文件在软件同级目录下!","错误",wx.OK |wx.ICON_ERROR)
            sys.exit(-1)
        
        #读取config
        self.__config=ConfigParser.RawConfigParser()
        self.__config.read(self.__CONFIG_FILE)
        
        global timeoutval,threadcnt,pagecntval,pagetmval
        timeoutval=int(self.__config.get("settings","timeout"))
        threadcnt=int(self.__config.get("settings","threadcnt"))
        pagecntval=int(self.__config.get("settings","wantpagecnt"))
        pagetmval=int(self.__config.get("settings","pagetimeout"))
        
        
        #清空日志文件
        logfile=file('iseeu.log','w')
        logfile.write("")
        logfile.close()
        #清空数据库表
        #delete_all_sql()  
        print "*** ----iSeeu------"      
        
        wx.Frame.__init__(self, parent, -1, title=title, size=(800,590), style=wx.DEFAULT_FRAME_STYLE)#^(wx.MAXIMIZE_BOX|wx.RESIZE_BORDER)
        self.SetBackgroundColour('white')
        self.Center()
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,
                      False, u'\u5fae\u8f6f\u96c5\u9ed1'))        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetIcon(wx.Icon('image/icon.ico', wx.BITMAP_TYPE_ICO))
        
        self.status = self.CreateStatusBar()
        self.processbar = wx.Gauge(self.status, size=(200,-1), pos=(600,0))
        
        self.menu = menu.iseeuMenu(self)
        #菜单
        self.Bind(wx.EVT_MENU,self.TestNet, self.menu.testnet)
        self.Bind(wx.EVT_MENU,self.OnClose,self.menu.exit)
        self.Bind(wx.EVT_MENU,self.OnAbout,self.menu.about)
        self.Bind(wx.EVT_MENU,self.OnSetTimeOut,self.menu.settimeout)
        self.Bind(wx.EVT_MENU,self.OnSetPageTimeOut,self.menu.setpagetimeout)
        self.Bind(wx.EVT_MENU,self.OnSetThdCnt,self.menu.setthreadcnt)
        self.Bind(wx.EVT_MENU,self.OnSetPageCnt,self.menu.setpagecnt)      
        self.Bind(wx.EVT_MENU,self.OnAFacebook,self.menu.facebook)      
        self.Bind(wx.EVT_MENU,self.OnATwitter,self.menu.twitter)        
        self.Bind(wx.EVT_MENU,self.OnCMOrder, self.menu.order_by_comment) 
        self.Bind(wx.EVT_MENU,self.OnRTOrder, self.menu.order_by_rt) 
        #self.Bind(wx.EVT_MENU,self.OnAnalysis, self.menu.analysis)
        self.Bind(wx.EVT_MENU,self.OnGWMatch, self.menu.gwmatch)
        self.menu.order_by_comment.Enable(False)
        self.menu.order_by_rt.Enable(False)
        #self.menu.analysis.Enable(False)
        #self.menu.gwmatch.Enable(False)
        
        v_0 = wx.BoxSizer(wx.VERTICAL)
        v_0.Add((800,200), 0, wx.ALL, 0)
        #ListBook  nav.png------------------------------------------------
        self.MainListBook = wx.Listbook(self, -1, size=(800,390))
        self.MainListBook.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        nav = wx.Image(r"image/nav.png", wx.BITMAP_TYPE_ANY, -1).ConvertToBitmap()
        il = wx.ImageList(34, 36)
        apiimg = il.Add(nav)
        weiimg = il.Add(nav)
        self.MainListBook.AssignImageList(il)
        
        #API页
        self.ApiPage = wx.Panel(self.MainListBook)
        dc = wx.ClientDC(self.ApiPage)
        dc.DrawBitmap(nav, 0,0)
        v_1_api = wx.BoxSizer(wx.VERTICAL)
        h_1_api = wx.BoxSizer()
        self.ApiKey = StaticText(self.ApiPage, label=Eng2Zh("输入人名"))
        self.ApiKeyVal = wx.TextCtrl(self.ApiPage)
        self.ApiSearch = wx.Button(self.ApiPage, label=Eng2Zh("搜搜"))
        self.ApiMatch = wx.Button(self.ApiPage, label=Eng2Zh("匹配"))
        h_1_api.AddMany([
            (self.ApiKey, 0, wx.LEFT|wx.TOP, 8),
            (self.ApiKeyVal, 0, wx.ALL, 5),
            (self.ApiSearch, 0, wx.ALL, 5),
            (self.ApiMatch, 0, wx.ALL, 5),])
        v_1_api.Add(h_1_api, 0, wx.EXPAND|(wx.ALL^wx.LEFT), 5)    
        self.ApiNoteBook = wx.Notebook(self.ApiPage, -1)
        #API
        self.ApiNoteBook_api = wx.Panel(self.ApiNoteBook)       #API
        self.ApiNoteBook_api_Lc = wx.ListCtrl(self.ApiNoteBook_api, -1, style=wx.LC_REPORT|wx.LC_SORT_ASCENDING)
        self.ApiNoteBook_api_Lc.InsertColumn(0,Eng2Zh("姓名"),wx.LIST_FORMAT_CENTER,width=100)
        self.ApiNoteBook_api_Lc.InsertColumn(1,Eng2Zh("ID"),wx.LIST_FORMAT_CENTER,width=100)
        self.ApiNoteBook_api_Lc.InsertColumn(2,Eng2Zh("性别"), wx.LIST_FORMAT_CENTER,width=100)
        self.ApiNoteBook_api_Lc.InsertColumn(3,Eng2Zh("省"),wx.LIST_FORMAT_CENTER,width=100)
        self.ApiNoteBook_api_Lc.InsertColumn(4,Eng2Zh("城市"),wx.LIST_FORMAT_CENTER,width=100)
        self.ApiNoteBook_api_Lc.InsertColumn(5,Eng2Zh("来源"),wx.LIST_FORMAT_CENTER,width=100)
        
        h_2_api = wx.BoxSizer()
        h_2_api.Add(self.ApiNoteBook_api_Lc, 1, wx.EXPAND, 0)
        self.ApiNoteBook_api.SetSizer(h_2_api)
        
        self.ApiNoteBook_xhw = wx.Panel(self.ApiNoteBook)       #新华网
        self.ApiNoteBook_xhw_rt = rt.RichTextCtrl(self.ApiNoteBook_xhw, -1, style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY)
        h_2_xhw = wx.BoxSizer()
        h_2_xhw.Add(self.ApiNoteBook_xhw_rt, 1, wx.EXPAND, 0)
        self.ApiNoteBook_xhw.SetSizer(h_2_xhw)
        
        self.ApiNoteBook_bk = wx.Panel(self.ApiNoteBook)        #百科
        #self.ApiNoteBook_bk_rt = rt.RichTextCtrl(self.ApiNoteBook_bk, -1, style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY)
        self.ApiNoteBook_bk_rt = rt.RichTextCtrl(self.ApiNoteBook_bk, -1, style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY)
        h_2_bk = wx.BoxSizer()
        h_2_bk.Add(self.ApiNoteBook_bk_rt, 1, wx.EXPAND, 0)
        self.ApiNoteBook_bk.SetSizer(h_2_bk)
        
        self.ApiNoteBook_jj = wx.Panel(self.ApiNoteBook)        #简介
        self.ApiNoteBook_jj_rt = rt.RichTextCtrl(self.ApiNoteBook_jj, -1, style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY)
        h_2_jj = wx.BoxSizer()
        h_2_jj.Add(self.ApiNoteBook_jj_rt, 1, wx.EXPAND, 0)
        self.ApiNoteBook_jj.SetSizer(h_2_jj)

        
        self.ApiNoteBook.AddPage(self.ApiNoteBook_api, Eng2Zh("API"), select=True, imageId=-1)
        self.ApiNoteBook.AddPage(self.ApiNoteBook_xhw, Eng2Zh("新华网"), imageId=-1)
        self.ApiNoteBook.AddPage(self.ApiNoteBook_bk, Eng2Zh("百科"), imageId=-1)
        self.ApiNoteBook.AddPage(self.ApiNoteBook_jj, Eng2Zh("更多"), imageId=-1)
        v_1_api.Add(self.ApiNoteBook, 1, wx.EXPAND|wx.LEFT,0)
        self.ApiPage.SetSizer(v_1_api)
        
        #微博页
        self.WeiboPage = wx.Panel(self.MainListBook)
        #self.WeiboPage.SetBackgroundColour("green")
        v_1_wei = wx.BoxSizer(wx.VERTICAL)
        h_1_wei = wx.BoxSizer()
        #self.WeiKey = StaticText(self.WeiboPage, label=Eng2Zh("输入微博内容"))
        self.WeiKeyVal = wx.SearchCtrl(self.WeiboPage, -1, size=(150,-1), style=wx.TE_PROCESS_ENTER)
        self.WeiKeyVal.SetDescriptiveText(Eng2Zh("输入微博内容"))
        #self.WeiSearch = wx.Button(self.WeiboPage, label=Eng2Zh("搜搜"))
        #self.WeiMatch = wx.Button(self.WeiboPage, label=Eng2Zh("匹配"))
        h_1_wei.AddMany([
            #(self.WeiKey, 0, wx.LEFT|wx.TOP, 8),
            (self.WeiKeyVal, 0, wx.ALL, 5),
            #(self.WeiSearch, 0, wx.ALL, 5),
            #(self.WeiMatch, 0, wx.ALL, 5),
            ])
        v_1_wei.Add(h_1_wei, 0, wx.EXPAND|(wx.ALL^wx.LEFT), 5)
        self.WeiboListCtrl =wx.ListCtrl(self.WeiboPage, -1, style=wx.LC_REPORT)
        self.WeiboListCtrl.InsertColumn(0, Eng2Zh("用户ID"), wx.LIST_FORMAT_CENTER, 60)
        self.WeiboListCtrl.InsertColumn(1, Eng2Zh("姓名"), wx.LIST_FORMAT_CENTER, 60)
        self.WeiboListCtrl.InsertColumn(2, Eng2Zh("微博ID"), wx.LIST_FORMAT_CENTER, 60)
        self.WeiboListCtrl.InsertColumn(3, Eng2Zh("微博"), wx.LIST_FORMAT_CENTER, 280)
        self.WeiboListCtrl.InsertColumn(4, Eng2Zh("省市"), wx.LIST_FORMAT_CENTER, 60)
        self.WeiboListCtrl.InsertColumn(5, Eng2Zh("评论数"), wx.LIST_FORMAT_CENTER, 60)
        self.WeiboListCtrl.InsertColumn(6, Eng2Zh("转发数"), wx.LIST_FORMAT_CENTER, 60)
        self.WeiboListCtrl.InsertColumn(7, Eng2Zh("来源"), wx.LIST_FORMAT_CENTER, 60)
        
        v_1_wei.Add(self.WeiboListCtrl, 1, wx.EXPAND, 0)
        self.WeiboPage.SetSizer(v_1_wei)
        
        #添加
        self.MainListBook.AddPage(self.ApiPage, Eng2Zh("由姓名"), select=True, imageId=apiimg)
        self.MainListBook.AddPage(self.WeiboPage, Eng2Zh("由内容"), imageId=weiimg)
        v_0.Add(self.MainListBook, 1, wx.EXPAND, 0)
        self.MainListBook.SetInternalBorder(0)
        #---------------------------------------------------------------
        
        self.ApiKeyVal.SetFocus()
        self.ApiSearch.SetDefault()
        self.SetSizer(v_0)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnApiNoteChg, self.ApiNoteBook)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChg, self.MainListBook)
        self.Bind(wx.EVT_BUTTON, self.BtnMatch, self.ApiMatch)
        #搜索人名
        self.Bind(wx.EVT_BUTTON, self.OnSearch, self.ApiSearch)
        self.Bind(wx.EVT_TEXT, self.OnGetKey, self.ApiKeyVal)
        self.ApiNoteBook_api_Lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnMoreInfo)
        #微博搜索
        self.Bind(wx.EVT_TEXT_ENTER, self.OnWeiboSearch, self.WeiKeyVal)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnWeiboSearch, self.WeiKeyVal)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnFinishWS, self.WeiKeyVal)
        self.WeiboListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnWeiboDetail)
        self.WeiboListCtrl.Bind(wx.EVT_LIST_COL_CLICK, self.OnOrder)
        
        '''成员变量'''
        self.key = ''
        self.weibokey = ""                          #微博关键字
        self.SDObj=iseeuthread.BeCallByIseeu()      #搜索处理对象
        #self.mysql=sqlite_op.sqlite_op()            #数据库操作对象
        self.bnamechg = False
        self.once=False
        
        self.fbk = False                               #Facebook无效
        self.twr = False                               #Twitter无效
        self.bHasFTPage = False                        #是否有Facebook Twitter页
        
        delete_wb_fd()
        #self.tstnet = wx.Timer(self, -1)
        #self.Bind(wx.EVT_TIMER, self.OnTimer, self.tstnet)
        #self.tstnet.Start(1)
        
    def OnAFacebook(self, evt):
        if self.menu.facebook.IsChecked():
            self.fbk = True
            if not self.bHasFTPage:
                self.bHasFTPage = True
                self.ApiNoteBook_foreign = wx.Panel(self.ApiNoteBook)   
                self.ApiNoteBook_foreign_lc = wx.ListCtrl(self.ApiNoteBook_foreign, -1, style=wx.LC_REPORT|wx.LC_SORT_ASCENDING)
                
                self.ApiNoteBook_foreign_lc.InsertColumn(0,"ID",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(1,"Name",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(2,"Gender",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(3,"Location",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(4,"Status",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(5,"Source",wx.LIST_FORMAT_CENTER,width=100)                 
                
                vbox = wx.BoxSizer()
                vbox.Add(self.ApiNoteBook_foreign_lc, 1, wx.EXPAND, 0)
                self.ApiNoteBook_foreign.SetSizer(vbox)
                
                self.ApiNoteBook.InsertPage(1, self.ApiNoteBook_foreign, "ForeignApi")
                     
        else:
            self.fbk = False  
            if self.bHasFTPage and not self.menu.twitter.IsChecked():
                self.bHasFTPage = False
                self.ApiNoteBook.RemovePage(1)  
                self.ApiNoteBook.SetSelection(0)
                #self.Update()   
        
    def OnATwitter(self, evt):
        if self.menu.twitter.IsChecked():
            self.twr = True
            if not self.bHasFTPage:
                self.bHasFTPage = True
                self.ApiNoteBook_foreign = wx.Panel(self.ApiNoteBook) 
                self.ApiNoteBook_foreign_lc = wx.ListCtrl(self.ApiNoteBook_foreign, -1, style=wx.LC_REPORT|wx.LC_SORT_ASCENDING)
                
                self.ApiNoteBook_foreign_lc.InsertColumn(0,"ID",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(1,"Name",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(2,"Gender",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(3,"Location",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(4,"Status",wx.LIST_FORMAT_CENTER,width=100)
                self.ApiNoteBook_foreign_lc.InsertColumn(5,"Source",wx.LIST_FORMAT_CENTER,width=100) 
                
                vbox = wx.BoxSizer()
                vbox.Add(self.ApiNoteBook_foreign_lc, 1, wx.EXPAND, 0)
                self.ApiNoteBook_foreign.SetSizer(vbox)
                #先boxsizer 再插入就可以显示正常
                self.ApiNoteBook.InsertPage(1, self.ApiNoteBook_foreign, "ForeignApi")
        else:
            self.twr = False 
            if self.bHasFTPage and not self.menu.facebook.IsChecked():
                self.bHasFTPage = False
                self.ApiNoteBook.RemovePage(1)
                self.ApiNoteBook.SetSelection(0)
                #self.Refresh()           
    def OnTimer(self, evt=None):
        if self.tstnet.IsRunning():
            self.tstnet.Stop()
        req = urllib2.Request("http://www.baidu.com")
        try:
            ret = urllib2.urlopen(req)
            #print ret.info()
            print "net is working"
            return True
        except Exception,e:
            #print e
            wx.MessageBox(Eng2Zh("请检查你的网络是否连通，再进行搜索"))
            return False
    
    def TestNet(self, evt=None):
        req = urllib2.Request("http://www.baidu.com")
        try:
            ret = urllib2.urlopen(req)
            #print ret.info()
            if evt:
                wx.MessageBox(Eng2Zh("网络通畅，可以进行搜索"))
            return True
        except Exception,e:
            #print e
            if evt:
                wx.MessageBox(Eng2Zh("请检查你的网络是否连通，再进行搜索"))
            return False

    
    def OnGetKey(self, evt):
        self.key = self.ApiKeyVal.GetValue()
        
    def OnSearch(self,event):
        #if not self.OnTimer():
        #    return False
        if(self.ApiKeyVal.GetValue()==""):
            wx.MessageBox(Eng2Zh("请输入关键字"),"iSeeu")
            self.ApiKeyVal.SetFocus()
            return 
        if(self.ApiSearch.GetLabel()=="搜搜".decode("utf8")):
            self.ApiSearch.SetLabel(Eng2Zh("停止"))
            self.key=self.ApiKeyVal.GetValue().strip(" ")
            self.key=self.key.encode("utf-8")
            #调用其他api函数搜索
            #创建搜索进程
            #nPreApiNun：每种api的线程数,最好是100的约数,self.key关键字'
            #名字改变，清空数据
            delete_all_sql()
            self.DeleteAll()
            self.ApiNoteBook_xhw_rt.SetValue(Eng2Zh("正在加载"))
            self.ApiNoteBook_bk_rt.SetValue(Eng2Zh("正在加载"))
            self.ApiNoteBook_jj_rt.SetValue(Eng2Zh("正在加载"))
            self.isEnd=False   #控制进度条和状态栏线程和超时线程结束
            nPreApiNum=threadcnt
            self.SDObj.SearchByBtn(self.key,nPreApiNum,pagecntval, self.fbk, self.twr)
            self.SDObj.SetChiThdPro(0)
            #添加数据源菜单变灰
            self.menu.testnet.Enable(False)
            self.menu.facebook.Enable(False)
            self.menu.twitter.Enable(False)
            #新华网
            xinhuath = threading.Thread(target=self.xinhua, args=(self.key,))
            xinhuath.setDaemon(True)
            xinhuath.start()
            #百度百科
            baiketd = threading.Thread(target=self.baike, args=(self.key,))
            baiketd.setDaemon(True)
            baiketd.start()
            #clHtm
            baidutd = threading.Thread(target=self.baidu, args=(self.key,))
            baidutd.setDaemon(True)
            baidutd.start()
            
            '''超时线程'''
            chktime=threading.Thread(target=self.__ChkTime)
            chktime.setDaemon(True)
            chktime.start()

            '''数据库中提取数'''
            fromsqlget=threading.Thread(target=self.FromSqlGet)#新浪
            fromsqlget.setDaemon(True)
            fromsqlget.start()
            rsqlget=threading.Thread(target=self.RenrenGet)#人人
            rsqlget.setDaemon(True)
            rsqlget.start()
            if self.twr:
                twsqlget=threading.Thread(target=self.TwitterGet)#Twitter Facebook
                twsqlget.setDaemon(True)
                twsqlget.start()   
            if self.fbk:
                fbsqlget = threading.Thread(target=self.FacebookGet)#Twitter Facebook
                fbsqlget.setDaemon(True)
                fbsqlget.start() 
                
            #进度条
            processThread=threading.Thread(target=self.SetProcessBar)
            processThread.setDaemon(True)
            processThread.start()
        
        elif(self.ApiSearch.GetLabel()=="停止".decode("utf8")):
            #停止则杀死子线程
            self.SDObj.SetChiDeaFlag(True)
            self.isEnd=True
            #稍等待杀死线程
            time.sleep(1.2)
            self.ApiSearch.SetLabel(Eng2Zh("搜搜"))  
    
    def OnWeiboSearch(self, evt):
        global timeoutval,threadcnt,pagecntval,pagetmval
        #检查网络
        #if not self.OnTimer():
        #    return False        
        #添加数据源菜单失效
        self.menu.facebook.Enable(False)
        self.menu.twitter.Enable(False)
        self.menu.testnet.Enable(False)
        
        self.menu.order_by_comment.Enable(False)
        self.menu.order_by_rt.Enable(False)
        #self.menu.analysis.Enable(False)

        self.weibokey = self.WeiKeyVal.GetValue()
        self.weibokey = self.weibokey.encode('utf8')
        #print self.weibokey
        if self.weibokey == "":
            wx.MessageBox(Eng2Zh("请输入微博关键字"))
            return
        key = self.weibokey
        pages = pagecntval              #need weibo pages
        tdnum = threadcnt               #the thread number of getting weibo
        sinasql =  sqlite_op.sqlite_op()
        twsql = twitter.Twitter_Sql()
        fbk_sql = facebook.Facebook_Sql()
        #clear sqlite
        try:
            sinasql.delete_all("status")
            print "delete all sina status "
        except Exception,e:
            print "delete all sina status error:",e
        try:
            twsql.clear_all("twitter_status")
            print "delete all twitter status"
        except Exception,e:
            print "delete all twitter status error:",e
        try:
            fbk_sql.clear_all("facebook_status")
            print "delete all facebook status"
        except Exception,e:
            print "delete all facebook status error:",e
        
        
        self.WeiboListCtrl.DeleteAllItems()                          #清除以前listctrl的数据
        self.WBS = iseeuthread.WeiboMulTd(key, pages, tdnum, 1)         #微博搜索处理对象
        
        #开线程获取数据放入列表中
        GWBTd = thread.start_new_thread(self.GetWB, ())             #新浪
        
        if self.twr:
            self.TWS = iseeuthread.WeiboMulTd(key, 20, tdnum,2)         #twitter搜索处理对象
            TWTD = thread.start_new_thread(self.GetTWRWB, ())           #Twitter
            
        if self.fbk:
            self.FBS = iseeuthread.WeiboMulTd(key, 20, tdnum,3)         #facebook搜索处理对象
            FBTD = thread.start_new_thread(self.GetFBKWB, ())           #Facebook
            
        tmtd = thread.start_new_thread(self.WeiboCheckTimeOut, ())      #check timeout when getting weibo data
        self.WeiKeyVal.ShowCancelButton(True)                        #显示取消按钮
        
        evt.Skip()
    
    def WeiboCheckTimeOut (self):
        global timeoutval,threadcnt,pagecntval,pagetmval
        start_time = time.time()
        time_between_pages = 0
        now_got_pages = 0
        while (threading.currentThread().isAlive() and (time.time()-start_time)<timeoutval and time_between_pages < pagetmval):
            if now_got_pages == iseeuthread.WeiboMulTd.pages_got:           #the got pages do not add
                time_between_pages += 1                         #add 1 s
            else:
                time_between_pages = 0                          #relay zero and add time
                now_got_pages = iseeuthread.WeiboMulTd.pages_got
                print "got weibo pages:",iseeuthread.WeiboMulTd.pages_got
                if now_got_pages >= pagecntval:
                    break                
            time.sleep(1)

        end_time = time.time()
        self.OnFinishWS()
        print "getting weibo is stopped. using time:",end_time - start_time,"between pages time:",time_between_pages
        
    def OnFinishWS(self, evt=None):
        self.WBS.bTmExit = True
        self.menu.order_by_comment.Enable(True)
        self.menu.order_by_rt.Enable(True)
        #self.menu.analysis.Enable(True)
        
        if self.twr:
            self.TWS.bTmExit = True         #Twitter
        if self.fbk:
            self.FBS.bTmExit = True         #Facebook Finish
        self.WeiKeyVal.ShowCancelButton(False) 
        print "Weibo Search must be stopped."
        if evt <> None:
            evt.Skip()
    
    def GetWB(self):
        weibosql = sqlite_op.sqlite_op()
        data = []
        index = 0
        while not self.WBS.bTmExit:
            try:
                #weibosql.delete_repeat_user("status")       #删除重复项
                data = weibosql.get_sinaweibo(index)
                if data == []:continue
                index += len(data)
                self.WriteWBData(data)
            except:
                time.sleep(0.1)
#        try:
#            weibosql.delete_repeat_user("status")       #删除重复项
#        except:
#            pass
        while 1:
            try:
                data = weibosql.get_sinaweibo(index)
                self.WriteWBData(data)
                break
            except Exception,e:
                print "get sina weibo error:",e
            
        self.WeiKeyVal.ShowCancelButton(False) 

        #添加数据源菜单恢复
        self.menu.facebook.Enable(True)
        self.menu.twitter.Enable(True)
        self.menu.testnet.Enable(True)
    
    def GetTWRWB(self):
        twr_sql = twitter.Twitter_Sql()
        index = 0
        while not self.TWS.bTmExit:
            try:
                data = twr_sql.get_status(self.weibokey , index)
                if data == []:continue
                index += len(data)
                self.WriteWBData(data)
            except Exception,e:
                print "Get Twitter error:",e
        while 1:
            try:
                data = twr_sql.get_status(self.weibokey , index)
                self.WriteWBData(data)
                break
            except Exception,e:
                print "Last Get Twitter error:",e   
        print "Get Twitter Finish"
        
    def GetFBKWB(self):
        fbk_sql = facebook.Facebook_Sql()
        index = 0
        while not self.FBS.bTmExit:
            try:
                data = fbk_sql.get_status(index)
                if data == []:continue
                index += len(data)
                self.WriteWBData(data)
            except Exception,e:
                print "Get Facebook error:",e
        while 1:
            try:
                data = fbk_sql.get_status(index)
                self.WriteWBData(data)
                break
            except Exception,e:
                print "Last Get Facebook error:",e   
        print "Get Facebook Finish"        
                
    def OnWeiboDetail(self, evt):
        uid = self.WeiboListCtrl.GetItem(evt.GetIndex(),0).GetText()
        sid = self.WeiboListCtrl.GetItem(evt.GetIndex(),2).GetText()
        source = self.WeiboListCtrl.GetItem(evt.GetIndex(), 7).GetText()
        #print uid, sid, source
        if source == "twitter.com" or source == "facebook.com" or source == "":
            wx.MessageBox(Eng2Zh("由于获取数据不足，无法显示详细信息"))
            return False
        self.WBDetail = iseeuMoreinfo.MoreInfo(self, uid, source, sid) 
        evt.Skip()
        
    def WriteWBData(self, data):
        #print data
        if data==[]:return
        for i in range(len(data)):
            index = self.WeiboListCtrl.InsertStringItem(sys.maxint, str(data[i][0]))
            for j in range(1, len(data[i])):
                dain = data[i][j]
                if j == 2 or j == 5 or j==6:
                    dain = str(dain)
                self.WeiboListCtrl.SetStringItem(index, j, dain)
            #self.WeiboListCtrl.SetStringItem(index, 5, "sina.com.cn")
        
    def OnOrder (self, evt=None):
        otype = evt.GetColumn()
        if otype == 5 or otype == 6:
            try:
                if not self.WBS.bTmExit:
                    wx.MessageBox(Eng2Zh("获取微博信息还没有结束，不能进行排序。请稍等或主动停止获取开始排序！"))
                    return False
            except Exception, e:
                print "order error:",e
                return False
            
            if otype == 5:intype = "comment"
            elif otype == 6:intype = "rt"
            sina_sql = sina_sdk.Sina_Sqlite()
            data = sina_sql.order(intype)
            if data <> False:
                self.WeiboListCtrl.DeleteAllItems()
                self.WriteWBData(data)
                # add facebook twitter
                if self.fbk:
                    fbsql = facebook.Facebook_Sql()
                    fb = fbsql.get_status(0)
                    self.WriteWBData(fb)
                if self.twr:
                    twsql = twitter.Twitter_Sql()
                    tw = twsql.get_status(self.weibokey, 0)
                    self.WriteWBData(tw)
        else:
            return False
        
    def OnCMOrder(self, evt):
        try:
            if not self.WBS.bTmExit:
                wx.MessageBox(Eng2Zh("获取微博信息还没有结束，不能进行排序。请稍等！"))
                return False
        except Exception, e:
            print "menu order error:",e
            return False
        sina_sql = sina_sdk.Sina_Sqlite()
        data = sina_sql.order("comment")
        if data <> False:
            self.WeiboListCtrl.DeleteAllItems()
            self.WriteWBData(data)

    def OnRTOrder(self, evt):
        try:
            if not self.WBS.bTmExit:
                wx.MessageBox(Eng2Zh("获取微博信息还没有结束，不能进行排序。请稍等！"))
                return False
        except Exception, e:
            print "menu order error:",e
            return False
        sina_sql = sina_sdk.Sina_Sqlite()
        data = sina_sql.order("rt")
        if data <> False:
            self.WeiboListCtrl.DeleteAllItems()
            self.WriteWBData(data)

#    def OnAnalysis(self, evt):
#        selstatus = self.WeiboListCtrl.GetFocusedItem()
#        selid = self.WeiboListCtrl.GetItem(selstatus, 0).GetText()
#        print selid
        
    def OnGWMatch(self, evt):
        import matchtable
        self.GWMatch = matchtable.Match_Table(self)
        self.GWMatch.Show()
        
    def xinhua(self, key):
        key = Eng2Zh(key)
        nctn = 0
        while not self.isEnd:
            if baidu.xinhua(key):
                self.ApiNoteBook_xhw_rt.SetValue("")
                if os.path.exists('data/xh'+key+"1.jpg"):
                    print "---------",'data/xh',key,"1.jpg"
                    self.ApiNoteBook_xhw_rt.WriteImageFile('data/xh'+key+"1.jpg", wx.BITMAP_TYPE_JPEG)
                path = 'data/xh'+key+".txt"
                f = file(path, 'r')
                data = f.read()
                f.close()
                try:
                    title = data[:data.find('\n')]
                    data = data[data.find('\n'):]
                    print "title:",title
                    self.ApiNoteBook_xhw_rt.Newline()
                    self.ApiNoteBook_xhw_rt.BeginBold()
                    self.ApiNoteBook_xhw_rt.BeginFontSize(16)
                    self.ApiNoteBook_xhw_rt.WriteText(title)
                    self.ApiNoteBook_xhw_rt.EndFontSize()
                    self.ApiNoteBook_xhw_rt.EndBold()
                    self.ApiNoteBook_xhw_rt.Newline()
                    self.ApiNoteBook_xhw_rt.AppendText(data)
                except Exception,e:
                    print "xihua write error:",e
                    self.ApiNoteBook_xhw_rt.SetValue(Eng2Zh("没有找到你要的信息"))
                break
            else:
                self.ApiNoteBook_xhw_rt.SetValue(Eng2Zh("没有找到你要的信息"))
                break                
              
    def baike(self, key):
        key = Eng2Zh(key)
        nctn = 0
        #self.ApiNoteBook_bk_rt.LoadFile('data/baikems.html')
        #return 
        while not self.isEnd:
            if baidu.baike(key):
                self.ApiNoteBook_bk_rt.SetValue("")
                bmp = 'data/baikems'+key+".jpg"
                if os.path.exists(bmp):
                    self.ApiNoteBook_bk_rt.WriteImageFile(bmp, wx.BITMAP_TYPE_JPEG)
                path = 'data/baikems'+key+".txt"
                f = file(path, 'r')
                data = f.read()
                f.close()
                self.ApiNoteBook_bk_rt.AppendText(str(data))
                break
            else:
                self.ApiNoteBook_bk_rt.SetValue(Eng2Zh("没有找到你要的信息"))
                break
                
    def baidu(self, key):
        key = Eng2Zh(key)
        nctn = 0
        while not self.isEnd:
            if baidu.baidu(key):
                path = 'data/'+key+"jianli.txt"
                f = file(path, 'r')
                data = f.read()
                f.close()
                self.ApiNoteBook_jj_rt.SetValue(data)
                break
            else:
                self.ApiNoteBook_jj_rt.SetValue(Eng2Zh("没有找到你要的信息"))
                break
                
                    
    def BtnMatch(self, evt):
        if self.key == '':
            wx.MessageBox(Eng2Zh("没有关键字，请输入！"))
            return 
        self.ApiMatchFrame = match.iSeeu_Match_Frame(self.key, self)
        self.ApiMatchFrame.Show()    
        
    def OnMoreInfo(self,event):
        #调用详细信息的窗口
        id=self.ApiNoteBook_api_Lc.GetItem(event.GetIndex(),1).GetText()
        source = self.ApiNoteBook_api_Lc.GetItem(event.GetIndex(),5).GetText()
        if source == "twitter.com" or source == "facebook.com" or source=="":
            wx.MessageBox(Eng2Zh("获取信息时丢包，无法显示详细信息。请检查您的网络是否正常!"))
            return         
        one_more_info=iseeuMoreinfo.MoreInfo(self,id,source) 
    
    def __ChkTime(self):
        '检测超时'
        bgn=time.time()
        self.nowtime=0
        ps = 0
        pst = 0
        while ((time.time()-bgn<=timeoutval) and (not self.isEnd) and (pst<pagetmval)):
            time.sleep(1)
            if self.SDObj.GetChiThdPro()<>ps:
                ps = self.SDObj.GetChiThdPro()
                if ps == self.div:
                    self.isEnd = True
                    break
                pst = 0
            else: 
                pst += 1
            #print "now:",time.time()-bgn
            self.nowtime = time.time()-bgn
        self.SDObj.SetChiDeaFlag(True)
        self.isEnd=True
        print "timeout pst:",pst, "get data:",self.SDObj.GetChiThdPro(),"need data：",self.div
        
    def FromSqlGet(self):
        getsql=sqlite_op.sqlite_op()
        index=0
        while(threading.currentThread().isAlive()):
            if self.isEnd:            
                break            
            try:
                #新浪
                #getsql.delete_repeat_user("search1")
                data=getsql.searchByNameIndex(self.key,index)
                if(data==None or len(data)==0):
                    continue                    
                index += len(data)
                #print "sina write","data",len(data),Eng2Zh("第"),index   
                self.WriteData(data)                
            except:
                time.sleep(0.1)
        print "sina exit write"
        time.sleep(1)
#        try:
#            #getsql.delete_repeat_user("search1")
#        except:
#            pass
        data=getsql.searchByNameIndex(self.key, index)  
        self.WriteData(data)
        txt = " "*43+Eng2Zh(" 停止  已完成 ")+ "100" #str(self.SDObj.GetChiThdPro())
        num = str(self.ReadData())
        txt += "%" +" "*10 + Eng2Zh("一共搜到") + num + Eng2Zh("条数据")
        nowtime = str(self.nowtime)
        nowtime = nowtime[:nowtime.find('.')]        
        txt += " "*5 + Eng2Zh("用时：") + nowtime+"s"     
        self.status.SetStatusText(txt)
        self.processbar.SetValue(self.div)
        print "sina last write"
        #添加数据源菜单恢复
        #添加数据源菜单恢复
        self.menu.facebook.Enable(True)
        self.menu.twitter.Enable(True)
        self.menu.testnet.Enable(True)
        
    
    def RenrenGet(self):
        rensql = sql_renren.renren_sql()
        renindex = 0
        while(threading.currentThread().isAlive()):
            if self.isEnd:            
                break            
            try:
                #人人
                data = rensql.get_part_value(self.key, renindex)
                if(data==None or len(data)==0):
                    continue                    
                renindex += len(data)
                #print "renren write","data",len(data),Eng2Zh("第"),renindex   
                self.WriteData(data)
            except:
                time.sleep(0.1)
        print "renren exit write"
        while 1:
            try:
                data = rensql.get_part_value(self.key, renindex)
                self.WriteData(data)
                break
            except Exception,e:
                print "renren write error:",e
        print "renren last write"        
        
    def TwitterGet(self):
        twsql = twitter.Twitter_Sql()
        index = 0
        while(threading.currentThread().isAlive()):
            if self.isEnd:            
                break            
            try:
                data = twsql.get_users(self.key, index)
                if(data==None or len(data)==0):
                    continue                    
                index += len(data)
                #print "twitter write","data",len(data),Eng2Zh("第"),index   
                self.ForWriteData(data)
            except Exception,e:
                print "error:",e
                time.sleep(0.1)
        print "twitter exit write"
        while 1:
            try:
                data = twsql.get_users(self.key, index)
                self.ForWriteData(data)
                break
            except Exception,e:
                print "twitter write error:",e
        print "twitter last write" 
        
    def FacebookGet(self):
        fbsql = facebook.Facebook_Sql()
        index = 0
        while(threading.currentThread().isAlive()):
            if self.isEnd:            
                break            
            try:
                data = fbsql.get_users(self.key, index)
                if(data==None or len(data)==0):
                    continue                    
                index += len(data)
                #print "facebook write","data",len(data),Eng2Zh("第"),index   
                self.ForWriteData(data)
            except:
                time.sleep(0.1)
        print "facebook exit write"
        while 1:
            try:
                data = fbsql.get_users(self.key, index)
                self.ForWriteData(data)
                break
            except Exception,e:
                print "facebook write error:",e
        print "facebook last write"

    def ForWriteData(self, data):
        '写入ForeignApi'
        for values in data:
            index=self.ApiNoteBook_foreign_lc.InsertStringItem(sys.maxint,str(values[0]))
            for i in range(len(values)):    
                try:
                    self.ApiNoteBook_foreign_lc.SetStringItem(index,i,values[i])
                except:
                    self.ApiNoteBook_foreign_lc.SetStringItem(index,i,str(values[i]))
        
    def SetProcessBar(self):
        global pagecntval
        div = pagecntval+50              #新浪、人人
        if self.twr:div += 20            #Twitter
        #if self.fbk:div += 50            #Facebook
        self.div = div
        print "DIV:",div
        statustext=" "*43+"提示：正在进行搜索...完成"
        self.status.SetStatusText(Eng2Zh(statustext))
        self.processbar.SetRange(range=div)
        while(threading.currentThread().isAlive() and (not self.isEnd)):
                time.sleep(0.1)
                statustext=" "*43+"提示：正在进行搜索...完成"
                pc = self.SDObj.GetChiThdPro()
            
                proc = ""
                proc += "%f" % (pc*100/float(div))
                #print "proc:",pc,div, proc
                proc = proc[:proc.find('.')+3]
                nowtime = str(self.nowtime)
                nowtime = nowtime[:nowtime.find('.')]
                statustext +=  str(proc) +"%"+ " "*5 +"用时："+ nowtime+"s"
                self.status.SetStatusText(Eng2Zh(statustext))                
                self.processbar.SetValue(pc)
        self.ApiSearch.SetLabel(Eng2Zh("搜搜"))
    
    def WriteData(self,data):
        for values in data:
            index=self.ApiNoteBook_api_Lc.InsertStringItem(sys.maxint,values[0])
            for i in range(1,6):    
                try:
                    self.ApiNoteBook_api_Lc.SetStringItem(index,i,values[i])
                except:
                    self.ApiNoteBook_api_Lc.SetStringItem(index,i,str(values[i]))
                    
    def ReadData(self):
        return self.ApiNoteBook_api_Lc.GetItemCount()
             
    def DeleteAll(self):
        self.ApiNoteBook_api_Lc.DeleteAllItems()
        if self.bHasFTPage:
            self.ApiNoteBook_foreign_lc.DeleteAllItems()
    
    def OnSetTimeOut(self,event):
        '设置超时时间'
        global timeoutval,threadcnt,pagecntval,pagetmval
        tmout=wx.TextEntryDialog(self,Eng2Zh("设置最长搜索时间(10~1000s)："),Eng2Zh("设置"),str(timeoutval))
        if tmout.ShowModal()==wx.ID_OK:
            try:
                temp=int(tmout.GetValue())
                if temp<10 or temp >1000:
                    wx.MessageBox(Eng2Zh("输入值超过范围，请输入10~1000的整数!"))
                    return
                timeoutval = temp
            except:
                wx.MessageBox(Eng2Zh("错误字符，请输入10~1000的整数!"))
                return
            self.__config.set("settings","timeout",tmout.GetValue())
            self.__config.write(open(self.__CONFIG_FILE,'w'))
        tmout.Destroy()
        
    def OnSetPageTimeOut(self,event):
        '设置页间超时'
        global timeoutval,threadcnt,pagecntval,pagetmval
        pagetm=wx.TextEntryDialog(self,Eng2Zh("设置页间最大间隔时间(10~50s):"),Eng2Zh("设置"),str(pagetmval))
        if pagetm.ShowModal()==wx.ID_OK:
            try:
                temp=int(pagetm.GetValue())
                if temp<10 or temp >50:
                    wx.MessageBox(Eng2Zh("输入值超过范围，请输入10~50的整数!"))
                    return
                pagetmval =temp
            except:
                wx.MessageBox(Eng2Zh("错误字符，请输入10~50的整数!"))
                return
                
            self.__config.set("settings","pagetimeout",pagetm.GetValue())
            self.__config.write(open(self.__CONFIG_FILE,'w'))
        pagetm.Destroy()
        
    def OnSetThdCnt(self,event):
        '设置线程数'
        global timeoutval,threadcnt,pagecntval,pagetmval
        thdcnt=wx.TextEntryDialog(self,Eng2Zh("设置搜索线程数(2-10):"),Eng2Zh("设置"),str(threadcnt))
        if thdcnt.ShowModal() == wx.ID_OK:
            try:
                temp=int(thdcnt.GetValue())
                if temp<2 or temp >10:
                    wx.MessageBox(Eng2Zh("输入值超过范围，请输入2-10的整数!"))
                    return
                threadcnt =temp
            except:
                wx.MessageBox(Eng2Zh("错误字符，请输入2-10的整数!"))
                return
            
            self.__config.set("settings","threadcnt",thdcnt.GetValue())
            self.__config.write(open(self.__CONFIG_FILE,'w'))
        thdcnt.Destroy()
        
    def OnSetPageCnt(self,event):
        '设置所需返回的页数'
        global timeoutval,threadcnt,pagecntval,pagetmval
        pagecnt=wx.TextEntryDialog(self,Eng2Zh("设置所需返回数据页数(20-200):"),Eng2Zh("设置"),str(self.__config.get("settings","wantpagecnt")))
        if pagecnt.ShowModal() == wx.ID_OK:
            try:
                temp =int(pagecnt.GetValue())
                if temp<20 or temp >200:
                    wx.MessageBox(Eng2Zh("输入值超过范围，请输入20-200的整数!"))
                    return
                pagecntval =temp
            except:
                wx.MessageBox(Eng2Zh("错误字符，请输入20-200的整数!"))
                return
            
            self.__config.set("settings","wantpagecnt",pagecnt.GetValue())
            self.__config.write(open(self.__CONFIG_FILE,'w'))
            
    def OnAbout(self,event):
        #wx.MessageBox(Eng2Zh("iSeeu 1.0 \n==>by ---"),Eng2Zh("关于"))
        abtDlg = AboutDlg(self)
        abtDlg.ShowModal()
    
    def OnClose(self,event):
        self.Close()
                
    def OnPageChg(self, evt):
        self.Refresh()
        
    def OnApiNoteChg(self, evt):
        sel = evt.GetSelection()
        if sel <> 0:
            self.ApiMatch.Enable(False)
        else:
            self.ApiMatch.Enable()
        
    def OnSize(self, evt):
        evt.Skip()
        self.Refresh()
#        size = self.status.GetSize()
#        psize= self.processbar.GetSize()
#        self.processbar.SetPosition((size[0]-psize[0], size[1]-psize[1]))
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        bk = wx.Image(r"image/mainbk.jpg", wx.BITMAP_TYPE_ANY, -1)
        size = self.GetSize()
        bk = bk.Scale(size[0], size[1])
        bk = bk.ConvertToBitmap()
        dc.DrawBitmap(bk, 0, 0, True)
        
        size = self.ApiPage.GetSize()
        lbdc = wx.PaintDC(self.ApiPage)
        memDC = wx.MemoryDCFromDC(lbdc)
        memDC.SelectObject(bk)
        lbdc.Blit(0,0,size[0],size[1],memDC,80,200)
        memDC.SelectObject(wx.NullBitmap)        
        
        weidc = wx.PaintDC(self.WeiboPage)
        memDC1 = wx.MemoryDCFromDC(weidc)
        memDC1.SelectObject(bk)
        weidc.Blit(0,0,size[0],size[1],memDC1,80,200)
        memDC1.SelectObject(wx.NullBitmap)  
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
        brush = wx.Brush("#000000",wx.TRANSPARENT)
        dc.SetBackground(brush)
        evt.Skip()       
        
    

        
class iSeeu_App(wx.App):
    def OnInit(self):
        frame = iSeeu_Main_Frame(None)
        if not os.path.exists("data"):
            os.mkdir("data")
        frame.Show()
        return True
    def OnExit(self):
        #杀死子线程
        try:
            shutil.rmtree("data")
            os.rmdir("data")
            os.mkdir("data")
        except Exception,e:
            #sys.exit(0)
            print "delete data failed:",e
    
if __name__ == "__main__":
    app = iSeeu_App()
    app.MainLoop()