#! /usr/bin/env python
#coding=utf-8

import wx
import sqlite3, time, sys
import sqlite_op,sina_sdk, sql_renren

import iseeuMoreinfo

def Eng2Zh(text):
    return text.decode("utf8").encode("gbk")

class iSeeu_Match_Frame(wx.Frame):
    def __init__(self, key, parent=None, title=Eng2Zh("iSeeu-Match")):
        wx.Frame.__init__(self, parent, -1, title=title, size=(800,590),style=wx.DEFAULT_FRAME_STYLE^(wx.MAXIMIZE_BOX|wx.RESIZE_BORDER))
        self.Center()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.SetIcon(wx.Icon('image/icon.ico', wx.BITMAP_TYPE_ICO))
        
        self.genderlist = wx.ComboBox(self, size=(100,-1))
        self.provincelist = wx.ComboBox(self, size=(100,-1))
        self.citylist = wx.ComboBox(self, size=(100,-1))
        self.source = wx.ComboBox(self, size=(100,-1))
        
        #------------------------------------------------------------------
        hbox = wx.BoxSizer()
        hbox.Add((10,15), 0, wx.ALL, 5)
        
        hbox2 = wx.BoxSizer()
        hbox2.Add((20,10), 0, wx.ALL, 5)
        hbox2.Add(self.genderlist, 0, wx.LEFT, 5)
        hbox2.Add((30,10), 0, wx.ALL, 5)
        hbox2.Add(self.provincelist, 0, wx.LEFT, 5)
        hbox2.Add((30,10), 0, wx.ALL, 5)
        hbox2.Add(self.citylist, 0, wx.LEFT, 5)     
        hbox2.Add((30,10), 0, wx.ALL, 5)
        hbox2.Add(self.source, 0, wx.LEFT, 5)     
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((800,200),0,wx.ALL,0)
        vbox.Add(hbox, 0, wx.ALL^wx.BOTTOM, 5)
        vbox.Add(hbox2, 0, wx.ALL^wx.BOTTOM, 5)
        
        self.namelist = wx.ListCtrl(self, style=wx.LC_REPORT| wx.LC_EDIT_LABELS| wx.LC_SORT_ASCENDING)
        self.namelist.InsertColumn(0,Eng2Zh("姓名"),wx.LIST_FORMAT_CENTER,width=100)
        self.namelist.InsertColumn(1,Eng2Zh("ID"),wx.LIST_FORMAT_CENTER,width=100)
        self.namelist.InsertColumn(2,Eng2Zh("性别"), wx.LIST_FORMAT_CENTER,width=100)
        self.namelist.InsertColumn(3,Eng2Zh("省"),wx.LIST_FORMAT_CENTER,width=100)
        self.namelist.InsertColumn(4,Eng2Zh("城市"),wx.LIST_FORMAT_CENTER,width=100)
        self.namelist.InsertColumn(5,Eng2Zh("来源"),wx.LIST_FORMAT_CENTER,width=100)
        
        vbox.Add(self.namelist, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(vbox)      
        
        #成员变量
        self.key = key 
        self.mysql=sqlite_op.sqlite_op()
        self.rensql = sql_renren.renren_sql()
        
        self.genderlist.Bind(wx.EVT_COMBOBOX,self.OnSexCha)
        self.provincelist.Bind(wx.EVT_COMBOBOX,self.OnSexCha)
        self.citylist.Bind(wx.EVT_COMBOBOX,self.OnSexCha)
        self.namelist.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnMoreInfo)
        self.source.Bind(wx.EVT_COMBOBOX, self.OnSexCha)
        
        self.timer = wx.Timer(self, 1)
        self.timer.Start(1)
        self.Bind(wx.EVT_TIMER, self.OnInitPage, self.timer)
        
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        bk = wx.Image(r"image/mainbk.jpg", wx.BITMAP_TYPE_ANY, -1).ConvertToBitmap()
        dc.DrawBitmap(bk, 0, 0, True)
        #dc = wx.ClientDC(self)
        dc.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD,False, u'\u5fae\u8f6f\u96c5\u9ed1'))
        dc.DrawText(Eng2Zh("选择选项进行筛选"), 6,210) 
        dc.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))       
        dc.DrawText(Eng2Zh("性别"), 6,240)
        dc.DrawText(Eng2Zh("省区"), 150,240)
        dc.DrawText(Eng2Zh("城市"), 295,240)
        dc.DrawText(Eng2Zh("来源"), 440,240)
        evt.Skip()   
    
    def OnInitPage(self, evt):
        if self.timer.IsRunning():
            self.timer.Stop()
        self.DelItems()
        data = None
        cnt = 5
        temp = None
        while not data:     
            try:
                self.mysql.delete_repeat_user("sina_users")
                data=self.mysql.searchByName(self.key)
                temp = data
                if data == None or data == []:
                    cnt -= 1
                    if cnt==0:
                        wx.MessageBox(Eng2Zh('数据库请求频繁，运行缓慢，请再尝试'))
                        self.Destroy()
                else:
                    cnt = -1
                    self.WriteData(data)
                    data=self.rensql.get_part_value(self.key, 0)
                    self.WriteData(data)
                    for value in data:
                        temp.append(value)
                        
                    break
            except Exception,e:
                time.sleep(0.1)
                print "match get sql error:",e
        ##初始化combo
        self.WriteComboAll(temp)
        
    def WriteData(self,data):
        for values in data:
            index=self.namelist.InsertStringItem(sys.maxint,values[0])
            for i in range(1,6):    
                try:
                    self.namelist.SetStringItem(index,i,values[i])
                except:
                    self.namelist.SetStringItem(index,i,str(values[i]))
    
    def WriteComboAll(self,data):
        gender={}
        province={}
        city={}
        source = {}
        for values in data:
            gender.setdefault(values[2],"")
            province.setdefault(values[3],"")
            city.setdefault(values[4],"")
            if values[5] == "sina.com.cn":
                source.setdefault(Eng2Zh("新浪"),"")
            elif values[5] == "renren.com":
                source.setdefault(Eng2Zh("人人"),"")
        genderl=[Eng2Zh("<空>")]
        provincel=[Eng2Zh("<空>")]
        cityl=[Eng2Zh("<空>")]
        sourcel = [Eng2Zh("<空>")]
        for key in gender.keys():
            if key <> " ":
                genderl.append(key)
        for key in province.keys():
            if key <> " ":
                provincel.append(key)
        for key in city.keys():
            if key <> " ":
                cityl.append(key)
        for key in source.keys():
            if key <> " ":
                sourcel.append(key)
        
        self.WriteCombo(1,genderl)
        self.WriteCombo(2,provincel)
        self.WriteCombo(3,cityl)
        self.WriteCombo(4,sourcel)
        
    def WriteCombo(self,index,data):
        
        if index==1:
            #gender
            for value in data:
                self.genderlist.Append(value)
        elif index==2:
            #province
            for value in data:
                self.provincelist.Append(value)
        elif index==3:
            #city
            for value in data:
                self.citylist.Append(value)
        elif index==4:
            for value in data:
                self.source.Append(value)
            
    def OnSexCha(self,event):
        #wx.MessageBox("gender change","note")
        #插入数据库处理代码，限制条件可以加上self.provincelist.GetValue(),self.citylist.GetValue()的值
        #data="select * from * where gender=" + chaval
        ygender=self.genderlist.GetValue()
        ypro=self.provincelist.GetValue()
        ycity=self.citylist.GetValue()
        ysource = self.source.GetValue()
        
        data = []
        if ysource == "新浪".decode("utf8"):
            data=self.mysql.searchByKey(self.key,ygender,ypro,ycity)
        elif ysource == "人人".decode("utf8"):
            data=self.rensql.searchByKey(self.key,ygender,ypro,ycity)
        elif ysource=="" or ysource==u"<空>":
            data=self.mysql.searchByKey(self.key,ygender,ypro,ycity)
            temp=self.rensql.searchByKey(self.key,ygender,ypro,ycity)
            for value in temp:
                data.append(value)
        self.DelItems()
        #写入新的数据
        self.WriteData(data)
        
        self.genderlist.Clear()   
        self.provincelist.Clear()        
        self.citylist.Clear()    
        self.source.Clear()
                 
        self.WriteComboAll(data)
        
        self.genderlist.SetStringSelection(ygender)
        self.provincelist.SetStringSelection(ypro)
        self.citylist.SetStringSelection(ycity)
        self.source.SetStringSelection(ysource.encode('gbk'))
    
    def DelItems(self):
        self.namelist.DeleteAllItems()
        
    def OnMoreInfo(self,event):
        #调用详细信息的窗口
        id=self.namelist.GetItem(event.GetIndex(),1).GetText()
        source = self.namelist.GetItem(event.GetIndex(),5).GetText()
        self.one_more_info=iseeuMoreinfo.MoreInfo(self,id,source) 
    
        
if __name__=="__main__":
    app = wx.PySimpleApp()
    frame = iSeeu_Match_Frame("df")
    frame.Show()
    app.MainLoop()