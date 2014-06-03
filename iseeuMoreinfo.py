#! /usr/bin/env python
#coding=utf-8
import wx
import wx.richtext as rt
import os, sys
import sqlite_op,sina_sdk, sql_renren
import urllib2
import thread, time, threading
import renrenfd

def Eng2Zh(text):
    return text.decode("utf8").encode("gbk")

class StaticText(wx.StaticText):
    def __init__(self, parent, label):
        wx.StaticText.__init__(self, parent, -1, label=label, size=(-1,-1), style=wx.CLIP_CHILDREN |wx.TRANSPARENT_WINDOW)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, evt):
        size = self.GetSize()
        evt.Skip()
        dc = wx.PaintDC(self)
        dc.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL,
                              False, u'\u5fae\u8f6f\u96c5\u9ed1'))         
        dc.DrawText(self.GetLabel(), 0, 0)
        self.SetSize(size)

class MySBitmap(wx.StaticBitmap):
    def __init__(self, parent, bmp, size):
        wx.StaticBitmap.__init__(self, parent, -1, size=size, style=wx.CLIP_CHILDREN |wx.TRANSPARENT_WINDOW)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.bmp = bmp
        
    def SetBitmap(self, bmp):
        self.bmp = bmp
        self.Show()
    
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

class MoreInfo(wx.Frame):
    class iSeeuMoreLB(wx.Listbook):
        def __init__(self, parent, index=1):
            self.index = index
            wx.Listbook.__init__(self, parent, -1, size=(700,400), style=wx.BK_DEFAULT)
            newweibo = wx.Image("image/newweibo.jpg",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            friend = wx.Image("image/friend.jpg",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            tj = wx.Image("image/tj.jpg",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            
            il = wx.ImageList(50,50)
            opts = ["最近微博","朋友关系","统计信息"]
            imglist = []
            imglist.append(il.Add(newweibo))
            imglist.append(il.Add(friend))
            imglist.append(il.Add(tj))
            self.AssignImageList(il)
            
            for i in range(3):
                if i==2 and self.index==2:break
                panel = self.makePanel(self, i)
                self.AddPage(panel, Eng2Zh(opts[i]), imageId = imglist[i])
        
        def makePanel(self, parent, id):
            if id == 0:
                self.weibo = panel = MoreInfo.newWeibo(parent)
            elif id == 1:
                self.fship = panel = MoreInfo.friendShip(parent,self.index)
            elif id == 2:
                self.tj = panel = MoreInfo.TjIn(parent)
            return panel
    
    class newWeibo(wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent)
            box = wx.BoxSizer()
            self.rt = rt.RichTextCtrl(self, -1, style=wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY)
            box.Add(self.rt, 1, wx.EXPAND, 0)
            self.SetSizer(box)
            
    class friendShip(wx.Panel):
        def __init__(self, parent, index=1):
            wx.Panel.__init__(self, parent)
            box = wx.BoxSizer()
            if(index == 1):
                self.rt = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SORT_ASCENDING)
                box.Add(self.rt, 1, wx.EXPAND, 0)
                #id,name,location,friends_count,status_text
                #self.rt.InsertColumn(0, Eng2Zh(""), wx.LIST_FORMAT_CENTER, 50)
                self.rt.InsertColumn(0, Eng2Zh("I D"), wx.LIST_FORMAT_CENTER, 100)
                self.rt.InsertColumn(1, Eng2Zh("姓名"), wx.LIST_FORMAT_CENTER, 100)
                self.rt.InsertColumn(2, Eng2Zh("性别"), wx.LIST_FORMAT_CENTER, 100)
                self.rt.InsertColumn(3, Eng2Zh("省市"), wx.LIST_FORMAT_CENTER, 100)
                self.rt.InsertColumn(4, Eng2Zh("朋友个数"), wx.LIST_FORMAT_CENTER, 100)
                self.rt.InsertColumn(5, Eng2Zh("状态"), wx.LIST_FORMAT_CENTER, 100)
            elif index == 2:
                #画背景图
                self.Bind(wx.EVT_PAINT, self.OnPaint)
                self.pic = []
                self.name = []
                for i in range(0, 15):
                    bmp = wx.Image("image/newweibo.jpg",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                    pic = MySBitmap(self, bmp, size=(100,100))
                    namet = StaticText(self, label="")
                    self.pic.append(pic)
                    self.name.append(namet)
                    pic.Hide()
                    #name.Hide()
                for i in range(15):
                    if i == 1 or i==2:
                        self.pic[i].SetSize((60,90))
                    else:
                        self.pic[i].SetSize((90,60))
                #设置位置
                self.pic[0].SetPosition((220,191))  #90,60     
                self.pic[1].SetPosition((314,159))  #60,90
                self.pic[2].SetPosition((252,252))  #60,90
                self.pic[3].SetPosition((314,252))  #90,60
                self.pic[4].SetPosition((176,26))   #90,60
                self.pic[5].SetPosition((268,26))
                self.pic[6].SetPosition((360,26))
                self.pic[7].SetPosition((115,104))
                self.pic[8].SetPosition((440,104))
                self.pic[9].SetPosition((57,203))
                self.pic[10].SetPosition((505,204))
                self.pic[11].SetPosition((114,284))
                self.pic[12].SetPosition((440,281))
                self.pic[13].SetPosition((175,373))
                self.pic[14].SetPosition((363,374))
        
                self.name[0].SetPosition((180,251))       
                self.name[1].SetPosition((376,219))
                self.name[2].SetPosition((252,342))
                self.name[3].SetPosition((315,315))
                self.name[4].SetPosition((176,86))
                self.name[5].SetPosition((268,86))
                self.name[6].SetPosition((356,86))
                self.name[7].SetPosition((113,164))
                self.name[8].SetPosition((437,164))
                self.name[9].SetPosition((55,263))
                self.name[10].SetPosition((499,264))
                self.name[11].SetPosition((113,344))
                self.name[12].SetPosition((437,341))
                self.name[13].SetPosition((174,433))
                self.name[14].SetPosition((360,434))
                
            self.SetSizer(box)    
                
                
        def OnPaint(self, evt):  
            size = self.GetSize()
            bk = wx.Image("image/fdbk.png",wx.BITMAP_TYPE_ANY)
            bk = bk.Scale(size[0], size[1])
            self.bk = wx.BitmapFromImage(bk)
            pDC = wx.PaintDC(self)
            pDC.DrawBitmap(self.bk, 0, 0, True)
            evt.Skip()
        

    class TjIn(wx.Panel):
        def __init__(self, parent):
            wx.Panel.__init__(self, parent)
            self.SetBackgroundColour('white')
            self.ylabel = wx.StaticText(self, size=(1,400), pos=(20,60))
            self.ylabel.SetBackgroundColour('black')
            self.xlabel = wx.StaticText(self, size=(560,1), pos=(20,460))
            self.xlabel.SetBackgroundColour('black')
            self.stas = []
            self.stav = []
            wx.StaticText(self, label=Eng2Zh("时间段/小时"), pos=(562,465))
            for i in range(12):
                sta = wx.StaticText(self,label="", size=(40, 2), pos=(i*45+20+5,458))
                cnt = i+1
                text = "%2d~%2d" % (cnt*2-1,cnt*2)
                sv = wx.StaticText(self, label=text,pos=(i*45+24,465))
                sa = wx.StaticText(self, label ='', pos=(i*45+25,400-13), size=(-1,-1))
                self.stav.append(sa)
                self.stas.append(sta)
                sta.SetBackgroundColour("red") 
            wx.StaticText(self, label=Eng2Zh("活跃时间统计"), pos=(200,10))
            wx.StaticText(self, label=Eng2Zh("百分比/%"), pos=(30,35))
            for i in range(1,6):
                sv = wx.StaticText(self, label=str(i*20), pos=(4,450-400*i/5))
        
    def __init__(self,parent,id,source, sid=None):    
        wx.Frame.__init__(self,parent,title=Eng2Zh("iSeeu详细信息"),size=(750,650),pos=(300,50), style=wx.DEFAULT_FRAME_STYLE^(wx.MAXIMIZE_BOX|wx.RESIZE_BORDER))
        self.SetBackgroundColour((250,250,250))
        self.SetIcon(wx.Icon('image/icon.ico', wx.BITMAP_TYPE_ICO))
        if source == "sina.com.cn":
            self.moreinfoLB = MoreInfo.iSeeuMoreLB(self) 
        elif source == "renren.com":
            self.moreinfoLB = MoreInfo.iSeeuMoreLB(self, 2)

        self.name=wx.StaticText(self,label=Eng2Zh("姓名:"))
        self.nameval=wx.StaticText(self)
        self.ID=wx.StaticText(self,label="I D:")
        self.idval=wx.StaticText(self)
        self.sex=wx.StaticText(self,label=Eng2Zh("性别:"))
        self.sexval=wx.StaticText(self)
        self.province=wx.StaticText(self,label=Eng2Zh("省份:"))
        self.provinceval=wx.StaticText(self)
        self.city=wx.StaticText(self,label=Eng2Zh("城市:"))
        self.cityval=wx.StaticText(self)
        self.domain = wx.StaticText(self,label=Eng2Zh("网站:"))
        self.domainval = wx.StaticText(self)
        
        #self.Bind(wx.EVT_CLOSE, self.__repr__, self)
        #不同
        if source == "sina.com.cn":
            self.description = wx.StaticText(self,label=Eng2Zh("描述:"))
            self.descriptionval = wx.StaticText(self)
            self.status = wx.StaticText(self,label=Eng2Zh("状态:"))
            self.statusval = wx.StaticText(self)
            self.regtime = wx.StaticText(self,label=Eng2Zh("注册于:"))
            self.regtimeval = wx.StaticText(self)
            
            self.friendcnt = 0
            
        elif source == "renren.com":
            self.birth = wx.StaticText(self,label=Eng2Zh("生    日:"))
            self.birthval = wx.StaticText(self)
            self.country = wx.StaticText(self,label=Eng2Zh("国    家:"))
            self.countryval = wx.StaticText(self)
            self.workplace = wx.StaticText(self,label=Eng2Zh("工作地点:"))
            self.workplaceval = wx.StaticText(self)            
            self.workdes = wx.StaticText(self,label=Eng2Zh("工作描述:"))
            self.workdesval = wx.StaticText(self)
            self.wstime = wx.StaticText(self,label=Eng2Zh("开始时间:"))
            self.wstimeval = wx.StaticText(self)
            self.wetime = wx.StaticText(self,label=Eng2Zh("结束时间:"))
            self.wetimeval = wx.StaticText(self)
            self.gsch = wx.StaticText(self,label=Eng2Zh("毕业学校:"))
            self.gschval = wx.StaticText(self)
            self.gtime = wx.StaticText(self,label=Eng2Zh("毕业时间:"))
            self.gtimeval = wx.StaticText(self)
        
        #获得数据
        if sid:
            #获取数据
            sinaapi = sina_sdk.myapi()
            sinaapi.search_user_byid(id)
        self.data = None
        #print "data",self.data
        if source == "sina.com.cn":
            self.sqlite_op=sqlite_op.sqlite_op()
            self.data=self.sqlite_op.searchById(id)
            self.data=self.data[0]
            
            self.domainval.SetLabel(self.data[6])
            des = self.data[7]
            if len(des)>41: des=des[:41]+"..."
            self.descriptionval.SetLabel(des)
            #print type(self.data[8]),self.data[8]
            sta = self.data[8]
            if sta==None:
                sta=' '
            else:
                if len(sta)>41: sta=sta[:41]+"..."                
            self.statusval.SetLabel(sta)
            self.regtimeval.SetLabel(self.data[9])
            self.friendcnt = self.data[10]
            
            self.nameval.SetLabel(self.data[0])
            self.idval.SetLabel(str(self.data[1]))
            self.sexval.SetLabel(self.data[2])            
            self.provinceval.SetLabel(self.data[3])
            self.cityval.SetLabel(self.data[4])
            self.domainval.SetLabel(Eng2Zh('新浪网')+'sina.com.cn')
            
        elif source == "renren.com":
            rensql = sql_renren.renren_sql()
            self.data = rensql.get_all_value(id)
            self.domainval.SetLabel(Eng2Zh('人人网')+'renren.com')
            self.nameval.SetLabel(self.data[1])
            self.idval.SetLabel(str(self.data[2]))
            self.sexval.SetLabel(self.data[3])
            
            self.birthval.SetLabel(self.data[4])
            
            self.countryval.SetLabel(self.data[6])
            self.provinceval.SetLabel(self.data[7])
            self.cityval.SetLabel(self.data[8])
            
            self.workplaceval.SetLabel(self.data[9])
            self.workdesval.SetLabel(self.data[10])
            self.wstimeval.SetLabel(self.data[11])
            self.wetimeval.SetLabel(self.data[12])
            self.gschval.SetLabel(self.data[13])
            self.gtimeval.SetLabel(self.data[14])
            
        #print "data",self.data
        
        
        
        img = wx.Image("image/python_kj.jpg",wx.BITMAP_TYPE_ANY)
        self.img=wx.StaticBitmap(self,-1,wx.BitmapFromImage(img))
        
        #---------------1 行----------------
        #---------------1 行 1 列-----------
        hbox1 = wx.BoxSizer()
        hbox1.Add(self.img, 0, wx.ALL, 5)
        
        #---------------1 行 2 列-----------
        if source == "sina.com.cn":
            box_all = wx.BoxSizer(wx.VERTICAL)
            hbox12=wx.FlexGridSizer(2,6,5,5)   #wx.BoxSizer()
        
            hbox12.AddMany([(self.name,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.nameval,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM),
                        (self.ID,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.idval,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM),
                        (self.sex,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.sexval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                        (self.province,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.provinceval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                        (self.city,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.cityval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                        (self.domain,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.domainval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT)
                        ])
        
        
            box_cd = wx.BoxSizer()
            box_cd.AddMany([(self.description,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.descriptionval,1,wx.ALIGN_LEFT|wx.ALIGN_RIGHT|wx.EXPAND,5)])
            box_cs = wx.BoxSizer()
            box_cs.AddMany([(self.status,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.statusval,1,wx.ALIGN_LEFT|wx.ALIGN_RIGHT|wx.EXPAND,5)])
            box_cr = wx.BoxSizer()
            box_cr.AddMany([(self.regtime,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.regtimeval,1,wx.ALIGN_LEFT|wx.ALIGN_RIGHT|wx.EXPAND,5)])

            box_all.AddMany([(hbox12,0,(wx.ALL^wx.TOP)|wx.EXPAND,5),(box_cd,0,wx.ALL|wx.EXPAND,5),
                            (box_cs,0,wx.ALL|wx.EXPAND,5),(box_cr,0,wx.ALL|wx.EXPAND,5)])
                            
            hbox1.Add(box_all, 0, wx.EXPAND | wx.ALL,5)
        elif source == "renren.com":
            hbox12=wx.FlexGridSizer(5,6,5,5)
            hbox12.AddMany([(self.name,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.nameval,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM),
                            (self.ID,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.idval,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM),
                            (self.sex,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.sexval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            
                            (self.country,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.countryval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.province,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.provinceval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.city,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.cityval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            
                            (self.birth,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.birthval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.domain,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.domainval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.workdes,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.workdesval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            
                            (self.workplace,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.workplaceval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.wstime,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.wstimeval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.wetime,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.wetimeval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            
                            (self.gsch,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.gschval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            (self.gtime,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),(self.gtimeval,0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),
                            ((1,1),0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT),((1,1),0,wx.ALIGN_BOTTOM|wx.ALIGN_LEFT)                          
                            
                            ])
            hbox1.Add(hbox12, 0, wx.EXPAND | wx.ALL,5)
        #---------------2 行----------------
        vbox=wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1,proportion=0,flag=wx.ALL|wx.EXPAND,border=5)
        vbox.Add(self.moreinfoLB,proportion=1,flag=wx.EXPAND | wx.ALL,border=0)
        self.SetSizer(vbox)
        
        self.sid = sid
        self.id = id
        self.sur = source
        self.timer = wx.Timer(self,10)
        self.timer.Start(1)
        self.Bind(wx.EVT_TIMER,self.GetImage)
        
        self.Show()
    
    def GetImage(self,evt):
        if self.timer.IsRunning():
            self.timer.Stop()
        
        imtd = thread.start_new_thread(self.OnGetImg, ())
        #清空前次数据
        sinasql = sqlite_op.sqlite_op()
        try:
            print "clear table value"
            sinasql.delete_bytype('user_status', "user_id", int(self.id))
            sinasql.delete_bytype('friends', "host_id", int(self.id))
        except:
            pass  
        
        '''---------------------------------------------------------'''
        #微博信息
        if self.sur == "sina.com.cn":
            if self.sid:
                #微博点击过来的
                weibo = self.sqlite_op.get_sinawb_byid(self.sid)
                self.moreinfoLB.weibo.rt.BeginBold()
                self.moreinfoLB.weibo.rt.BeginFontSize(16)
                self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("微博搜索对应详细内容"))
                self.moreinfoLB.weibo.rt.EndFontSize()
                self.moreinfoLB.weibo.rt.EndBold()
                self.moreinfoLB.weibo.rt.Newline()
                self.moreinfoLB.weibo.rt.WriteText("     "+weibo[0][0])
            #user_status
                self.moreinfoLB.weibo.rt.Newline()
                self.moreinfoLB.weibo.rt.Newline()
            self.moreinfoLB.weibo.rt.BeginBold()
            self.moreinfoLB.weibo.rt.BeginFontSize(16)
            self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("下面是最近微博列表"))
            self.moreinfoLB.weibo.rt.EndFontSize()
            self.moreinfoLB.weibo.rt.EndBold()
            
            self.moreinfoLB.weibo.rt.Newline()
            self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("微博数据正在加载中..."))
            
            #写微博入界面
            self.wbtdflag= False
            self.fdtdflag = False
            self.wbtdflags = [False,False,False,False,False]
            for i in range(1,6):
                td = thread.start_new_thread(self.OnGWeibo,(i,))
                
            tdwb = thread.start_new_thread(self.OnWWeibo, ())
            tdfd = thread.start_new_thread(self.OnGFriend,())
            self.tdfdw = thread.start_new_thread(self.OnWFriend, ())  
            #朋友列表写入界面
        elif self.sur == "renren.com":
            #获取朋友
            td = thread.start_new_thread(self.GRenFriend, ())
            
        
    def GRenFriend(self):
        print "start get renren friend "
        try:
            renrenfd.renrenhaoyouimg(int(self.id))
        except:
            print "net error"
        
        #写状态
        path = "data/renrenzt"+ str(self.id) + ".txt"
        f = file(path, 'r')
        status = f.read()
        f.close()
        if len(status) > 0:
            try:
                self.moreinfoLB.weibo.rt.BeginBold()
                self.moreinfoLB.weibo.rt.BeginFontSize(16)
                self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("最近微博："))
                self.moreinfoLB.weibo.rt.EndFontSize()
                self.moreinfoLB.weibo.rt.EndBold()
                self.moreinfoLB.weibo.rt.Newline()
                self.moreinfoLB.weibo.rt.AppendText("     "+status.decode('utf8'))
            except Exception,e:
                print "write renren weibo error:",e
        else:
            self.moreinfoLB.weibo.rt.BeginBold()
            self.moreinfoLB.weibo.rt.BeginFontSize(16)
            self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("没有人人微博"))
            self.moreinfoLB.weibo.rt.EndFontSize()
            self.moreinfoLB.weibo.rt.EndBold()
            
        #写好友
        path = "data/renren"+ str(self.id) + ".txt"
        #print path
        if not os.path.exists(path):
            return
        f = file(path, 'r')
        names = f.readlines()
        f.close()
        picurl=[]
        for i in range(len(names)):
            namest = self.moreinfoLB.fship.name[i]
            namest.SetLabel(names[i][:-1].decode('utf8'))
            path = "data/" + str(self.id) +"dhy"+ str(i+1) + ".jpg"
            picurl.append(path)
        #显示朋友
        self.ShowFdPic(picurl)
        #统计信息
        print "finish get renren firend"
        
    def ShowFdPic(self, picurl):
        print "renren pic num:", len(picurl)
        for i in range(len(picurl)):
            picst = self.moreinfoLB.fship.pic[i]
            size = picst.GetSize()
            pic = picurl[i]
            if os.path.exists(pic):
                bmp = wx.Image(pic, wx.BITMAP_TYPE_ANY, -1)
                bmp = bmp.Scale(size[0], size[1])
                bmp = bmp.ConvertToBitmap()
                picst.SetBitmap(bmp)                    #填图，显示
        print "end show pic"
        
    def OnGetImg(self):
        #getimgth = threading.start_new_thread(target = self.Image,args=(self.data[5]))
        self.Image(self.data[5])
        #print 'img_url: ',self.data[5]
        if os.path.exists("image/python.png"):
            img=wx.Image("image/python.png",wx.BITMAP_TYPE_ANY,-1)
        else:
            img = wx.Image("image/python_wt.jpg",wx.BITMAP_TYPE_ANY)
        img = img.Scale(100,100)
        img = wx.BitmapFromImage(img)
        self.img.SetBitmap(img)        
        
    def OnGWeibo(self, i):
        '获取数据写入数据库'
        sinaapi = sina_sdk.myapi()
        while not self.wbtdflag:
            try:
                sinaapi.user_status(int(self.id), page=i)
                break
            except:
                pass
        print "x weibo ",i,"page",(i-1)*40,"end"
        self.wbtdflags[i-1] = True
        if(i == 1):
            flags = False
            while not flags:        #线程全部结束
                truecnt = 0
                for j in range(5):
                    if self.wbtdflags[j]:truecnt+=1
                    #print "truecnt:", truecnt, self.wbtdflags
                    if truecnt>=5:
                        flags=True       #线程全部结束
                time.sleep(0.1)
            try:
                print "*** count..."
                self.OnCount()          #'''统计信息'''
            except Exception, e:
                print e
            self.wbtdflag = True
        print "x weibo ",i,"exit"
        
    def OnGFriend(self):
        '获取朋友信息写入数据库'
        sinaapi = sina_sdk.myapi()
        #while not self.wbtdflag:
        try:
            sinaapi.imputfriends(int(self.id))
        except:
            pass
        self.fdtdflag = True
            
    def OnWWeibo(self):
        print "*** start write weibo"
        sinasql = sqlite_op.sqlite_op()
        index = 0
        data=[]
        f = file('data/temp'+str(self.id)+'.tm', 'w')
        f.write("")
        f.close()
        
        while not self.wbtdflag:
            try:
                data = sinasql.get_sina_userwb(index, self.id)
                if data==[]:continue
                self.WrWeibo(data, index)
                index += len(data)
            except:
                time.sleep(0.1)
        while 1:
            try:
                data = sinasql.get_sina_userwb(index, self.id)
                #print "weibo data:",data,index
                self.WrWeibo(data, index)
                break
            except Exception, e:
                print "write weibo error:",e
        print "wb---------------************************"
        f = file('data/temp'+str(self.id)+'.tm', 'r')
        temp = f.read()
        f.close()
        self.moreinfoLB.weibo.rt.Newline()
        self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("微博数据加载完成"))
        if len(temp)==0 and self.sid==None:
            self.moreinfoLB.weibo.rt.Newline()
            self.moreinfoLB.weibo.rt.WriteText(Eng2Zh("没有微博数据"))  
                      
        self.moreinfoLB.weibo.rt.AppendText(temp)
        
        
    def OnWFriend(self):
        sinasql = sqlite_op.sqlite_op()
        index = 0
        while not self.fdtdflag:
            try:
                data = sinasql.get_sina_userfd(index, self.id)
                if(data==None or len(data)==0):continue
                #print "--------------cnt:",len(data)
                index += len(data)
                self.WrFriend(data)
                #print "write ",index,"------",data[0][0]
            except:
                time.sleep(0.1)
        print "fd---------------************************"
        while 1:
            try:
                data = sinasql.get_sina_userfd(index, self.id)
                self.WrWeibo(data, index)
                break
            except Exception, e:
                print "write weibo error:",e
        print 'finish'
        
    def WrWeibo(self, data, index):
        path = 'data/temp'+str(self.id)+'.tm'
        f = file(path, 'a')
        for i in range(len(data)):
            temp = ""
            temp += "\r\n\r\n"
            temp += Eng2Zh("___【微博】" +" <%s>___" % str(i+index+1))
            temp += "\r"
            if type(1) == type(data[i][0]):
                temp += "      "+ str(data[i][0])
            else:                    
                try:
                    temp += "      "+data[i][0].encode('gbk')
                except:
                    break
            f.write(temp)
        f.close()
        
    
    def WrFriend(self, data):
        for i in range(len(data)):
            #img = data[i][0]
            index = self.moreinfoLB.fship.rt.InsertStringItem(sys.maxint, str(data[i][0]))
            for j in range(1, len(data[i])):
                if j == 2:
                    gender=''
                    if data[i][j].encode('utf8') == 'f':
                        gender=Eng2Zh("男")
                    else:
                        gender = Eng2Zh("女")
                    self.moreinfoLB.fship.rt.SetStringItem(index, j, gender)
                elif j == 4:
                    self.moreinfoLB.fship.rt.SetStringItem(index, j, str(data[i][j]))
                else:
                    self.moreinfoLB.fship.rt.SetStringItem(index, j, data[i][j])
            
      
    def OnCount(self):
        tmPre = []
        if self.sur == "sina.com.cn":
            sinaapi = sina_sdk.myapi()
            tmPre = sinaapi.statistiek_of_statustime(self.id)
        elif self.sur == "renren.com":
            pass
        
        frame = self.moreinfoLB.tj
        for i in range(12):
            sta = frame.stas[i]
            sta.SetSize((40, tmPre[i]*400))
            sta.SetPosition((20+i*45+5, 450-tmPre[i]*400+10))
            stt = frame.stav[i]
            stt.SetPosition((25+i*45, 450-tmPre[i]*400-5))
            if tmPre[i]<>0:
                cnt = str(tmPre[i]*100)
                cnt = cnt[:cnt.find('.')+3]
                stt.SetLabel(cnt)
                    
    def Image(self,url):
        #print "url:", url
        if os.path.exists("image/python.png"):
            os.remove("image/python.png")
        try:
            fp = urllib2.urlopen(url)
        except:
            return
        op = open("image/python.png","wb")
        n = 0
        op.write(fp.read())
        fp.close()
        op.close()
    
    def __del__(self):
        sinasql = sqlite_op.sqlite_op()
        self.wbtdflag = True
        self.fdtdflag = True
        while 1:
            try:
                sinasql.delete_bytype('user_status', "user_id", int(self.id))
                sinasql.delete_bytype('friends', "host_id", int(self.id))
                print "delete...."
                break
            except:
                time.sleep(0.1)        
        print "exit -------------------"
    

if __name__ == "__main__":
    app = wx.PySimpleApp()
    #test = MoreInfo(None, "1947764854" , "sina.com.cn")
    test = MoreInfo(None, "223759013" , "renren.com")
    app.MainLoop()