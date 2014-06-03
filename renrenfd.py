#! /usr/bin/env python
#coding=utf-8

import urllib2,time,cookielib,urllib
import re

    

def renrenhaoyouimg(id):
    
    callback_url='www.renren.com'
    params={
            'email':"iseeu_deve@163.com",
            'password':'123456789iseeu',
            'origURL':'www.renren.com',
            'domain':'renren.com'
            }
    active_url="http://www.renren.com/PLogin.do"
    cJar=cookielib.LWPCookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cJar))
    opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
    urllib2.install_opener(opener)
    req=urllib2.Request(active_url,urllib.urlencode(params))
    recvdata=urllib2.urlopen(req).read()

    url = "http://www.renren.com/profile.do?id="+str(id)
    #print url
    req=urllib2.Request(url)
    
    thepage = urllib2.urlopen(req).read()

    #扣状态
    f = file("data/renrenzt"+str(id)+".txt","w")
    ztpage = thepage
    if ztpage.find("<div class=\"status-holder\">")!=-1:
        ztpage = thepage[thepage.find("<div class=\"status-holder\">"):]
        ztpage = ztpage[:ztpage.find("</div>")]
    else:
        ztpage = ztpage[ztpage.find("<h2"):ztpage.find("</h2>")]
    ztpage = ztpage.replace("\n","")
    ztpage = ztpage.replace("\t","")
    ztpage = clHtm(ztpage)
    ztpage = ztpage.replace("|所有状态","")
    ztpage = ztpage[ztpage.find("("):]
    ztpage = ztpage[ztpage.find(")")+1:]+ztpage[:ztpage.find(")")+1]
    f.write(ztpage)
    f.close()


    f = file("data/renren"+str(id)+".txt","w")
    #f.encoding = "utf8"
    #print thepage.find("的好友<")
    thepage = thepage[thepage.find("的好友<"):thepage.find(">关于<")]
    i = 0
    while thepage.find("src=\"")>-1:
        i += 1
        imgurl = thepage[thepage.find("src=\"")+5:thepage.find(".jpg\"")+4]
        #print imgurl
        req = ""
        try:
            req = urllib2.urlopen(imgurl)
        except:
            continue
        img = req.read()
        thepage = thepage[thepage.find(".jpg\"")+5:]
        nurl = thepage[:thepage.find("</")]
        nurl = nurl[nurl.rfind(">")+1:]
        nurl = nurl.replace("\n","")
        #print nurl
        thepage = thepage[thepage.find("</"):]
        fx = file(u"data/"+str(id)+"dhy"+str(i)+".jpg","wb")
        f.write(nurl+"\n")
        fx.write(img)
        fx.close()
    f.close()
    
    

    

def clHtm(str):
    if str.find("<")>str.find(">"):
        str = str[str.find(">")+1:]
    while str.find("<") != -1:
        a1 = str.find("<")
        a2 = str.find(">")
        #print "a1 ",a1,"  a2 ",a2
        if a2>a1:
            str = str[:a1]+str[a2+1:]
        elif a1>a2:
            str = str.replace(">","",1)
    return str


if __name__ == "__main__":
  
    renrenhaoyouimg(261513549)
    '''
    f = file('data/renren261513549.txt', 'r')
    name = f.readlines()
    f.close()
    print type(name[0]),name[0][:-1]#.decode("utf8").encode('gbk')'''
    