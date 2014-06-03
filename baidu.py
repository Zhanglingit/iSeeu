#! /usr/bin/env python
#coding=utf-8
#平台数据

import urllib2
import re
import time, os

baidubiaoji = "\xb0\xd9\xb6\xc8\xbf\xec\xd5\xd5"#百度快照
headers = {"Host":"www.baidu.com",
            #"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0",
            "User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 Chrome/6.0.472.33Safari/534.3 SE 2.X MetaSr 1.0",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection":"Keep-Alive"
            }

def xinhua(item):
    ntime = time.time()
    #在百度上搜索新华网上的数据
    url = "http://www.baidu.com/s?wd="+item+"+inurl:xinhuanet.com/ziliao"
    req = urllib2.Request(url)
    try:
        req = urllib2.urlopen(req)
        thepagebd = req.read()
    except:
        print "xhover1:",time.time()-ntime
        return False
    #处理百度返回页获取连接
    if thepagebd.find(baidubiaoji) == -1 :
        print "xhover2:",time.time()-ntime
        return False
    thepagebd = thepagebd[:thepagebd.find(baidubiaoji)]
    ema = thepagebd.find("<em>")
    hrea = thepagebd[:ema].rfind("href=")
    urlre = re.compile("\"http.*?\"")
    if (urlre.search(thepagebd[hrea:ema])!="None") and (ema!=-1):
        url = urlre.search(thepagebd[hrea:ema]).group()
        url = url[1:-1]
        print "xhurl:",url
    else:
        print "xhover3:",time.time()-ntime
        return False
    req = urllib2.Request(url)
    try:
        req = urllib2.urlopen(req)
        thepage = req.read()
    except:
        print url,"failed"
        print "xhover4:",time.time()-ntime
        return False
    if thepage.find("\xa1\xbf")==-1:
        print "xhover5:",time.time()-ntime
        return False
    res = file("data/xh"+item+".txt","w")
    
    if thepage.find("class=txt18")!=-1:
        nstr = thepage[thepage.find("class=txt18"):]
        nstr = nstr[nstr.find(">")+1:nstr.find("<")]
    if thepage.find("class='txt18'")!=-1:
        nstr = thepage[thepage.find("class='txt18'"):]
        nstr = nstr[nstr.find(">")+1:nstr.find("<")]

    res.write(nstr+"\n")
    
    thepage = thepage[thepage.find("\xa1\xbf")+2:]#】
    thepage = thepage[thepage.find("\xa1\xbf")+2:thepage.find("\xa1\xbe\xcd\xc6\xbc\xf6")]#】 【推荐
    thepage = thepage.replace("&nbsp;","")
    #读图
    imgnum = 1
    start = 0
    while thepage.find("IMG",start)>-1:
        theimg = thepage
        start = theimg.find("IMG")+3
        theimg = theimg[start:]
        theimg = theimg[theimg.find("src=")+5:]
        theimg = theimg[:theimg.find("\"")]
        if theimg.find("http:")==-1:
            imgurl = url[:url.rfind("/")+1]+theimg
            #print "imgurl=",imgurl
        else:
            imgurl = theimg
        
        #print "imgurl=",imgurl
        req = urllib2.urlopen(imgurl)
        theimg = req.read()
        img = file("data/xh"+item+str(imgnum)+imgurl[-4:],"wb")
        img.write(theimg)
        img.close()
        imgnum += 1 
        thepage = thepage.replace("IMG","",1)

    thepage = clHtm(thepage)

    #去除空行
    bre = re.compile("[\r\n ]{3}")
    x = bre.search(thepage).group()
    thepage = thepage.replace(x,"")
    x = bre.search(thepage).group()
    thepage = thepage.replace(x,"")

    res.write(item)
    res.write(thepage)
    res.close()
    print "xhover6:",time.time()-ntime
    return True

def baike(item):
    ntime = time.time()
    #在百度上搜索百科上的数据
    url = "http://www.baidu.com/s?wd=intitle:"+item+"+inurl:baike.baidu.com"
    #print "bkurl:",url
    try:
        req = urllib2.urlopen(url)
    except:
        #print url,"failed"
        print "baikeover1:",time.time()-ntime
        return False
    thepagebd = req.read()
    #处理百度返回页获取连接
    if thepagebd.find(baidubiaoji) <= -1 :
        return False    
    thepagebd = thepagebd[:thepagebd.find(baidubiaoji)]
    ema = thepagebd.find("<em>")
    hrea = thepagebd[:ema].rfind("href=")
    urlre = re.compile("\"http.*?\"")
    if (urlre.search(thepagebd[hrea:ema])!="None") and (ema!=-1):
        url = urlre.search(thepagebd[hrea:ema]).group()[1:-1]
    else:
        print "baikeover2:",time.time()-ntime
        return False
    #print "bkurl:",url
    try:
        req = urllib2.urlopen(url)
        thepage = req.read()
    except:
        #print url,"failed"
        print "baikeover3:",time.time()-ntime
        return False
    
    
    thepage = thepage[thepage.find('content-bd main-body')+len('content-bd main-body'):thepage.find('<div class="content-ft">')]
    thepage = thepage[thepage.find('>')+1:]
    #thepage = thepage.replace('src="http://imgsrc.baidu.com/baike/abpic/item/', 'src="')
    
    #print "get img"
    #读图
    summary = thepage[thepage.find('<div class="pic"'):]
    summary = summary[:summary.find('<div class="card-info nslog-area"')]
    imgurl = summary[summary.find('<img'):]
    imgurl = imgurl[imgurl.find('src="')+5:]
    imgurl = imgurl[:imgurl.find('"')]
    #print "img:",imgurl
    
    #print thepage
    if imgurl<>"" and imgurl[-4] == ".":
        try:
            ext = imgurl[-4:]
            req = urllib2.urlopen(imgurl)
            theimg = req.read()
            name = imgurl[imgurl.rfind('/')+1:]
            PICTURE = '<img src="' + name + '" />'
            path = "data/baikems"+(item)+ext
            #print path,"---------------------"
            if not os.path.exists(path):
                img = file(path,"wb")
                img.write(theimg)
                img.close()
        except:
            pass
    if thepage.find("<p>目录</p>".decode("utf-8").encode("gbk"))!=-1:
            thepage = thepage[thepage.find("<p>目录</p>".decode("utf-8").encode("gbk"))+len("<p>目录</p>".decode("utf-8").encode("gbk")):]
    
    #去掉SUP
    while thepage.find("<sup>")!=-1:
        thepage = thepage[:thepage.find("<sup>")]+thepage[thepage.find("</sup>")+6:]
    while thepage.find("<style")!=-1:
            thepage = thepage[:thepage.find("<style")]+thepage[thepage.find("</style>")+8:]
    while thepage.find("<script")!=-1:
            thepage = thepage[:thepage.find("<script")]+thepage[thepage.find("</script>")+9:]
    
    
    thepage = clHtm(thepage)
    
    #去除空行
    bre = re.compile("[\r\n]{3,}")
    while bre.search(thepage)!=None:
        thepage = thepage.replace(bre.search(thepage).group(),"\n")
    
    #处理&
    re7 = re.compile("&.{2,8}?;")
    while re7.search(thepage)!=None:
        thepage = thepage.replace(re7.search(thepage).group(),"")
    
    re8 = re.compile("baikeViewInfo.*?};")
    while re8.search(thepage)!=None:
        thepage = thepage.replace(re8.search(thepage).group(),"")
    
    re9 = re.compile("bk\..*?;")
    
    while re9.search(thepage)!=None:
            thepage = thepage.replace(re9.search(thepage).group(),"")
    
    
    thepage = re.sub(r'\n+', " ", thepage)
    #处理
    res = file("data/baikems"+(item)+".txt","w")
    res.write(thepage)
    res.close()
    #print "ok"
    print "baikeover4:",time.time()-ntime
    return True
    
def baidu(item):
    ntime = time.time()
    #在百度上搜索百度上的数据
    url = "http://www.baidu.com/s?wd="+item+"%20title%3A%20%28%20%28%BC%F2%C0%FA%20%7C%20%BC%F2%BD%E9%29%29"#title((简介|简历))
    #print "bdurl:",url
    req = urllib2.urlopen(url)
    thepagebd = req.read()
    #处理百度返回页获取连接
    list = thepagebd.split(baidubiaoji)
    #print len(list)
    pn = 0
    
    f = file("data/"+item+"jianli.txt","w")
    while len(list)>1:
        for i in range(len(list)-1):
            ema = list[i].find("<em>")
            hrea = list[i][:ema].rfind("href=")
            urlre = re.compile("\"http.*?\"")
            if urlre.search(list[i][hrea:ema])!="None":
                dataurl = urlre.search(list[i][hrea:ema]).group()[1:-1]
                #print dataurl
            abt = list[i][hrea:list[i].find("</h3>")]
            abt = clHtm(abt)
            #print "bat:",abt
            f.write(u"【题目】： ".encode("gbk")+abt)
            f.write(u"【链接】： ".encode("gbk")+dataurl)
            f.write("\n")
            abdata = list[i][list[i].find("</h3>")+5:]
            abdata = clHtm(abdata)
            #print "abdata:",abdata
            f.write(u"【摘要】： ".encode("gbk")+abdata)
            f.write(u"\n\n\n")
        if len(list)<11:
            break
        #print "**pn",pn,"**len",len(list)
        pn += 10
        searchurl = url+"&pn="+str(pn)
        #print searchurl
        req = None
        try:
            req = urllib2.urlopen(searchurl)
        except:
            print "baiduover1:",time.time()-ntime
            return False
        
        #time.sleep(0.2)
        thepagebd = req.read()
        list = thepagebd.split(baidubiaoji)
    f.close()   
    
    print "baiduover:2",time.time()-ntime,"suliang:",pn+len(list)-1
    return True

            
    
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

    
if __name__=="__main__":
    x = raw_input("name>")
    xinhua(x)
    #baike(x)
    #baidu(x)
    print "ok"
    #clHtm('<a href="http://baike.baidu.com/update/id=5427145" target="_blank">更多</a></span>贡献光荣榜</h2>')