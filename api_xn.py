#coding=utf-8

import urllib2,urllib,hashlib,httplib,httplib2,json
import time,cookielib,re,os
import ConfigParser
API_KEY=''
SECRET_KEY=''
#SESSION_KEY='2.5bb4a4b088ba1708f0ab762e1965b907.3600.1301637600-278925717'
OAUTN_TOKEN=''



def searchonRenren(name,page):
#    if bgetid[0] == True:
#        return
#    bgetid[0] = True
#    print "bgetid",bgetid[0]
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    ret = opener.open(" http://www.renren.com")

    pagenum = page*10
    cfg = ConfigParser.RawConfigParser()
    cfg.read("idimg.temp")
    while 1:
        data = urllib.urlencode({'q':name,'ajax':1,'offset':pagenum})
        request = urllib2.Request('http://browse.renren.com/searchEx.do?ref=syshome',data)
        response = opener.open(request)
        thepage = response.read()
        time.sleep(0.5)
        #print thepage
        #thepage = thepage[:thepage.find("<!--搜索无结果注册开始-->")]
        list = thepage.split("姓名")
        #print "len:",len(list)
        #print "pagenum",pagenum
        f = file("data/renrenid"+str(pagenum/10)+".txt","w")
        for i in range(1,len(list)):
            id = list[i][list[i].find("href=")+6:list[i].find("\" target")]
            id = id[id.find("id=")+3:id.find("&from")]
            #print "**",pagenum,"**",i,"**",id,"**"
            url = list[i-1]
            url = url[url.rfind('<a'):url.rfind('</a>')]
            url = url[url.find('<img src="')+10:]
            url = url[:url.find('"')]
            cfg.set("idimg", id, url)
            cfg.write(open('idimg.temp','w'))
            f.write(id)
            f.write("\n")
            #result=users_getInfo(api_key,session_key,uids=id)
            #print result
        f.close()
        
        #pagenum +=10
        #if len(list)<11:
        break

def init_info (api_key,secret_key):
    global API_KEY
    global SECRET_KEY
    #global OAUTN_TOKEN
    API_KEY=api_key
    SECRET_KEY=secret_key
    #OAUTN_TOKEN=oauth_token

def logout ():

    req=urllib2.Request('http://www.renren.com/Logout.do')
    urllib2.urlopen(req)
    
def get_session_key (username,password,callback_url='http://apps.renren.com/iseeu_sk'):
    params={
        'email':username,
        'password':password,
        'origURL':callback_url,
        'domain':'renren.com'
        }
    active_url="http://www.renren.com/PLogin.do"
    cJar=cookielib.CookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cJar))
    opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
    urllib2.install_opener(opener)
    req=urllib2.Request(active_url,urllib.urlencode(params))
    recvdata=urllib2.urlopen(req).read()
    pattern=re.compile(r'xn_sig_session_key=.*&amp;xn_sig_added')
    if not pattern:
        return [None]
    xn_sig_session_key=pattern.search(recvdata).group()
    session_key=xn_sig_session_key[19:-17]
    g_session_key=session_key#[session_key]
    return g_session_key


def get_sig (params):   
    params=sorted(params.items(),key=lambda d:d[0])
    #print params
    query=''
    for param in params:
        query=query+param[0]+'='+param[1]
    query+=SECRET_KEY
    #print query
    sig=hashlib.md5(query).hexdigest().lower()
    #print sig
    return sig

def request_api (params):
    req=urllib2.Request('http://api.xiaonei.com/restserver.do',urllib.urlencode(params))
    return urllib2.urlopen(req).read()

#--管理类接口--#
def admin_getAllocation(api_key,call_id='',v='1.0',method='admin.getAllocation',format='json'):
    '得到一个应用当天可以发送的通知和邀请的配额。'
    params={
        'api_key':api_key,
        'call_id':call_id,
        'method':method,
        'v':v,
        'format':format}
    sig=get_sig(params)
    params.setdefault('sig',sig)
    return request_api(params)

#--好友关系类接口--#
def friends_areFriends (api_key,session_key,uids1='',uids2='',call_id='',v='1.0',format='json',method='friends.areFriends'):
    '判断两组用户是否互为好友关系，比较的两组用户数必须相等'
    params={
        'api_key':api_key,
        'session_key':session_key,
        'uids1':uids1,
        'uids2':uids2,
        'call_id':call_id,
        'v':v,
        'format':format,
        'method':method
        }
    sig=get_sig(params)
    params.setdefault('sig',sig)
    return request_api(params)

def friends_get  (api_key,session_key,call_id='',v='1.0',format='json',method='friends.get',page='1',count='500'):
    '得到当前登录用户的好友列表，得到的只是含有好友uid的列表'
    params={
        'api_key':api_key,
        'session_key':session_key,
        'call_id':call_id,
        'v':v,
        'format':format,
        'method':method,
        'page':page,
        'count':count}
    sig=get_sig(params)
    params.setdefault('sig',sig)
    return request_api(params)  
    
def friends_getFriends (api_key,session_key,method='friends.getFriends',call_id='',v='1.0',format='json',page='0',count='500'):    
    '得到当前登录用户的好友列表'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'page':page,
        'count':count
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

def friends_getAppUsers(api_key,session_key,call_id='',v='1.0',format='json',method='friends.getAppUsers'):
    '返回已经添加了一个应用的好友的用户Id列表，此接口只返回全部好友中的数据，如果你需要完整的全部数据请调用'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)
  
def friends_getAppFriends (api_key,session_key,fields='name,tinyurl,headurl',call_id='',v='1.0',format='json',method='friends.getAppFriends'):
    '返回App好友的ID列表。App好友是指某个用户安装了同一应用的好友'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'fields':fields
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)
 
#--邀请类接口 --# 
def invitations_createLink (api_key,session_key,domain='0',call_id='',v='1.0',format='json',method='invitations.createLink'):
    '生成用户站外邀请用户注册的链接地址,应用可以引导用户通过QQ或者msn等渠道邀请好友加入应用'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'domain':domain
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)
 
def invitations_getInfo (api_key,invitee_id='',begin_time='',end_time='',call_id='',v='1.0',format='json',method='invitations.getInfo'):
    '根据应用新用户的id获取用户的是否通过邀请安装，同时得到此次邀请的详细信息（包括邀请者、邀请时间、被邀请者等）。接口可以按照用户id或者时间段来查询，本接口不需要传入session_key参数。此接口下一个版本将会支持获取站内邀请的关系，暂时只支持站外邀请 '
    #Note: 
    #1.如果想获得某个用户被谁邀请进来的，请传入invitee_id
    #2.如果想获得一段时间内所有用户的邀请信息，请传入begin_time和end_time，此时请不要传入invitee_id
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'format':format,
        'invitee_id':invitee_id,
        'begin_time':begin_time,
        'end_time':end_time,
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)  
    
#--通知类接口 --#
def notifications_send (api_key,session_key,to_ids='',notification='',call_id='',v='1.0',format='json',method='notifications.send'):
    '给当前登录者的好友或也安装了同样应用的用户发通知。分发继续考虑应用的评分、通知的屏蔽和通知的举报这些因素，没有发送总量的限制，每一个应用通知的分发分为appToUser和UserToUser两种方式，这次更新暂时不开放appToUser。 UserToUser：每个app的每一个安装用户(sender)每一天有一定配额（可以通过admin.getAllocation接口取到这个配额）。接收者（receiver）必须是用户的好友或者是安装应用的用户。没有通过审核的app，通知只发送给发送者，默认配额数量为20条。'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'to_ids':to_ids,
        'notification':notification
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

def notifications_sendEmail(api_key,session_key,uid='2342342',template_id='1',recipients='2838234',template_data="{'who':'234234','static_uid':'23423423'}",call_id='',v='1.0',format='json',method='notifications.sendEmail'):
    '给你的用户发送Email。此接口需要扩展权限---Email '
    params={
        'api_key':api_key,
        'method':method,
        'uid':uid,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'template_id':template_id,
        'recipients':recipients,
        'template_data':template_data
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

#--公共主页类接口--#
def pages_isFan (api_key,session_key,page_id='1',uid='',call_id='',v='1.0',format='json',method='pages.isFan'):
    '判断用户是否为Page的粉丝。这个接口里session_key不是必须的参数'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'uid':uid,
        'page_id':page_id
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

#--用户信息类接口--#   
def users_getInfo (api_key,session_key,uids='',method='users.getInfo',call_id='',v='1.0',format='json',
                   fields='uid,name,sex,star,zidou,vip,birthday,email_hash,tinyurl,headurl,mainurl,hometown_location,work_info,university_info'):
    '得到用户信息。'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format,
        'uids':uids,
        'fields':fields
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

def users_getLoggedInUser (api_key,session_key,call_id='',v='1.0',format='json',method='users.getLoggedInUser'):
    '根据session_key得到用户的ID，返回的ID值应该在session_key有效期内被存储，从而避免重复地调用该方法'
    params={
        'api_key':api_key,
        'method':method,
        'call_id':call_id,
        'v':v,
        'session_key':session_key,
        'format':format
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

def users_hasAppPermission (api_key,session_key,uid='8055',v='1.0',ext_perm='email',format='json',method='users.hasAppPermission'):
    '检查用户是否授予应用扩展权限'
    params={
        'api_key':api_key,
        'method':method,
        'v':v,
        'uid':uid,
        'ext_perm':ext_perm,
        'session_key':session_key,
        'format':format
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)

def users_isAppUser (api_key,session_key,uid='8055',call_id='',v='1.0',ext_perm='email',format='json',method='users.isAppUser'):
    '判断用户是否已经对应用授权。这个接口里session_key不是必须的参数。'
    params={
        'api_key':api_key,
        'method':method,
        'v':v,
        'uid':uid,
        'call_id':call_id,
        'ext_perm':ext_perm,
        'session_key':session_key,
        'format':format
        }
    sig=get_sig(params)    
    params.setdefault('sig',sig)
    return request_api(params)
            
if __name__ == "__main__":

    x = "黄茜"
    #x = x.decode("utf8").encode("utf-8")
    print repr(x)
    #print x
    searchonRenren(x)
    print "ok"