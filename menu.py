#! /usr/bin/env python
#coding=gbk

import wx
class iseeuMenu():
    def __init__(self,parent):
        self.menubar=wx.MenuBar()
        self.file=wx.Menu()
        self.testnet = self.file.Append(-1, "网络测试")
        self.exit=self.file.Append(-1,"退出")
        self.menubar.Append(self.file,"文件")
        #'''
        self.seti=wx.Menu()
        self.settimeout=self.seti.Append(-1,"设置最大搜索时间")
        self.setpagetimeout=self.seti.Append(-1,"设置页间最大间隔时间")
        self.seti.AppendSeparator()
        self.setpagecnt=self.seti.Append(-1,"需要返回的页数")
        self.setthreadcnt=self.seti.Append(-1,"设置线程数")

        self.seti.AppendSeparator()
        temp = wx.Menu()
        self.facebook = temp.AppendCheckItem(-1, "Facebook")
        self.twitter = temp.AppendCheckItem(-1, "Twitter")
        self.seti.AppendMenu(-1, "增加数据源", temp)
        
        
        self.menubar.Append(self.seti,"配置")
		#'''
        self.tools = wx.Menu()
        self.order_by_comment = self.tools.Append(-1, "微博按评论数排序")
        self.order_by_rt = self.tools.Append(-1, "微博按转发数排序")
        self.tools.AppendSeparator()
        #self.analysis = self.tools.Append(-1, "微博数据集中分析")
        self.gwmatch = self.tools.Append(-1, "境内外数据匹配")
        
        self.menubar.Append(self.tools, "工具")
        
        self.help=wx.Menu()
        self.about=self.help.Append(-1,"关于")
        self.menubar.Append(self.help,"帮助")
		
        parent.SetMenuBar(self.menubar)

'''
<object class="wxMenubar" name="menubar">
			<object class="wxMenu" name="file">
				<object class="wxMenuItem" name="exit">
					<label>退出</label>
				</object>
			</object>
		</object>

'''