#! /usr/bin/env python
#coding=gbk

import wx
class iseeuMenu():
    def __init__(self,parent):
        self.menubar=wx.MenuBar()
        self.file=wx.Menu()
        self.testnet = self.file.Append(-1, "�������")
        self.exit=self.file.Append(-1,"�˳�")
        self.menubar.Append(self.file,"�ļ�")
        #'''
        self.seti=wx.Menu()
        self.settimeout=self.seti.Append(-1,"�����������ʱ��")
        self.setpagetimeout=self.seti.Append(-1,"����ҳ�������ʱ��")
        self.seti.AppendSeparator()
        self.setpagecnt=self.seti.Append(-1,"��Ҫ���ص�ҳ��")
        self.setthreadcnt=self.seti.Append(-1,"�����߳���")

        self.seti.AppendSeparator()
        temp = wx.Menu()
        self.facebook = temp.AppendCheckItem(-1, "Facebook")
        self.twitter = temp.AppendCheckItem(-1, "Twitter")
        self.seti.AppendMenu(-1, "��������Դ", temp)
        
        
        self.menubar.Append(self.seti,"����")
		#'''
        self.tools = wx.Menu()
        self.order_by_comment = self.tools.Append(-1, "΢��������������")
        self.order_by_rt = self.tools.Append(-1, "΢����ת��������")
        self.tools.AppendSeparator()
        #self.analysis = self.tools.Append(-1, "΢�����ݼ��з���")
        self.gwmatch = self.tools.Append(-1, "����������ƥ��")
        
        self.menubar.Append(self.tools, "����")
        
        self.help=wx.Menu()
        self.about=self.help.Append(-1,"����")
        self.menubar.Append(self.help,"����")
		
        parent.SetMenuBar(self.menubar)

'''
<object class="wxMenubar" name="menubar">
			<object class="wxMenu" name="file">
				<object class="wxMenuItem" name="exit">
					<label>�˳�</label>
				</object>
			</object>
		</object>

'''