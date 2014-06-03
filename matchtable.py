#! /usr/bin/env python
#coding=utf-8

import wx
import wx.html as html
import sqlite_op
        
def File_Read (path):
    f = file(path, 'r')
    data = f.read()
    f.close()
    return data

        
def File_Write (path, data):
    f = file(path, 'w')
    f.write(data)
    f.close()
    return True

class Match_Table(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "iSeeu Analysis", size=(800,590),
                style=wx.DEFAULT_FRAME_STYLE^(wx.MAXIMIZE_BOX|wx.RESIZE_BORDER))
        self.Center()
        self.SetIcon(wx.Icon('image/icon.ico', wx.BITMAP_TYPE_ICO))
        
#        self.table = 
        self.htmlWnd = html.HtmlWindow(self, -1, size=(800,590))
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnLoad, self.timer)
        self.timer.Start(1)
        
    def OnLoad(self, evt):
        if self.timer.IsRunning():
            self.timer.Stop()
            
        matchsql = sqlite_op.MatchSql()
        matchsql.match_name()
        matchsql.match_status()
        
        name_num = len(matchsql.NAME_DATA)
        name_sex_num = len(matchsql.NAME_SEX_DATA)
        status_num = len(matchsql.STATUS_DATA)
        status_name_num = len(matchsql.STATUS_NAME_DATA)

        name_data = ""
        name_sex_data = ""
        status_data = ""
        status_name_data = ""
        if name_num <= 0:
            name_num = 1
            name_data += '<tr><td colspan="2">%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (u'无'.encode('gbk'),0,0,0,0)
            pass
        else:
            for name in matchsql.NAME_DATA:
                all = name['sina']+name['facebook']+name['twitter']
                name_data += '<tr><td colspan="2">%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (name['name'].encode('gbk'),name['sina'],name['facebook'],name['twitter'],all)
        if name_sex_num <= 0:
            name_sex_num = 1
            name_sex_data = '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (u'无'.encode('gbk'),u'无'.encode('gbk'),0,0,0,0)
            pass
        else:
            for name in matchsql.NAME_SEX_DATA:
                all = name['sina']+name['facebook']+name['twitter']
                name_sex_data = '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (name['name'].encode('gbk'),name['sex'].encode('gbk'),name['sina'],name['facebook'],name['twitter'],all)
        
        if status_num <= 0:
            status_num = 1
            status_data += '<tr><td colspan="2">%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (u'无'.encode('gbk'),0,0,0,0)
            pass
        else:
            for name in matchsql.STATUS_DATA:
                all = name['sina']+name['facebook']+name['twitter']
                status_data += '<tr><td colspan="2">%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (name['status'][:10].encode('gbk')+"...",name['sina'],name['facebook'],name['twitter'],all)
        if status_name_num <= 0:
            status_name_num = 1
            status_name_data = '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (u'无'.encode('gbk'),u'无'.encode('gbk'),0,0,0,0)
            pass
        else:
            for name in matchsql.STATUS_NAME_DATA:
                all = name['sina']+name['facebook']+name['twitter']
                status_name_data = '<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (name['name'].encode('gbk'),name['status'][:10].encode('gbk')+"...",name['sina'],name['facebook'],name['twitter'],all)
        
        page = File_Read("Match.html")
        page = page.replace('[NAME_NUM]', str(name_num+1))
        page = page.replace('[NAME_DATA]', name_data)
        page = page.replace('[NAME_SEX_NUM]', str(name_sex_num+1))
        page = page.replace('[NAME_SEX_DATA]', name_sex_data)
        
        page = page.replace('[STATUS_NUM]', str(status_num+1))
        page = page.replace('[STATUS_DATA]', status_data)
        page = page.replace('[STATUS_NAME_NUM]', str(status_name_num+1))
        page = page.replace('[STATUS_NAME_DATA]', status_name_data)
                
        self.htmlWnd.SetPage(page)
        
if __name__ == "__main__":
    app = wx.PySimpleApp()
    test = Match_Table(None)    
    test.Show()     
    app.MainLoop()