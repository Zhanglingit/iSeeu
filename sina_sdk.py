#! /usr/bin/env python
#coding=utf-8

from weibopy.auth import OAuthHandler
from weibopy.api import API
import re,json,sqlite3,time,os
import urllib,urllib2,cookielib
import binascii

gconsumer_key="1776055845"
gconsumer_secret="a035f29ed0e1a661ddaa95363ff3823d"
gtoken="6e6b63ebfa97fd6e4f2c6ecf61c7ad5b"
gtokenSecret="9169de5d49724fba206c65f48c52d14f"

class myapi():
    def __init__(self,username="lee_develop@sina.com",psw="123456789"):
        #self.logfile=log_stream.log_stream("sina_sdk")
        global gconsumer_key
        global gconsumer_secret
        global gtoken
        global gtokenSecret
        
        #创建一个opener
        self.__cJar=cookielib.CookieJar()
        self.__opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cJar))
        self.__opener.addheaders=[('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
        urllib2.install_opener(self.__opener)
        
        #创建一个auth对象
        self.__auth=OAuthHandler(gconsumer_key,gconsumer_secret)
        
        self.__auth.setToken(gtoken,gtokenSecret)
        
        #创建api对象
        self.__api=API(self.__auth)        
    def __del__(self):
        pass
    
    def __get_pin(self,username,psw):
        req=urllib2.Request(self.__url)
        recvdata=urllib2.urlopen(req).read()
        
        params={
            "action":"submit",
            "regCallback":"http://api.t.sina.com.cn/oauth/authorize?oauth_token=%s&oauth_callback=none&from=" % self.__oauth_token,
            "oauth_token":self.__oauth_token,
            "oauth_callback":"none",
            "from":"",
            "userId":username,
            "passwd":psw,
            }
        req=urllib2.Request("http://api.t.sina.com.cn/oauth/authorize",urllib.urlencode(params))
        recvdata=urllib2.urlopen(req).read()
        #获得PIN
        pin=re.search("<b>.*：[0-9]*<",recvdata).group(0)
        pin=pin[pin.find("\x9a")+1:-1]
        return pin

    def getAtt(self, key):
        try:
            return self.obj.__getattribute__(key)
        except Exception, e:
            print e
            return ''
            
    def getAttValue(self, obj, key):
        try:
            return obj.__getattribute__(key)
        except Exception, e:
            print e
            return ''

    def search_user(self, q, count="40", page="1"):
        try:
            self.mySearch = self.__api.search_users(q, count, page,sort="1",snick="1",sdomain="1",sintro="0",\
                                               province="",city="",comorsch="",base_app="")
        except:
            return ["iseeu_error_exit"]
        return self.mySearch
    
    def search_friends(self,id,count=200,cursor=-1):
        self.mySearch=self.__api.friends(id,count,cursor)
        return self.mySearch
        return False
    
    def imputfriends(self,user_id):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS friends (u_id INTEGER PRIMARY KEY autoincrement,host_id integer,id integer,name text,\
                                                location text,statuses_count integer,friends_count integer,\
                                                gender text,profile_image_url text,followers_count integer,\
                                                favourites_count integer,\
                                                status_text text,status_source text)')
        con.commit()
        cursor_num=-1
        count=0
        while cursor_num!=0:
            recvfriends=self.search_friends(id=str(user_id),cursor=cursor_num)
            data1=json.loads(recvfriends)
            friends=data1["users"]
            cursor_num=data1["next_cursor"]
            if len(friends)==0:
                print "This person has no friends!"
            else:
                #print len(friends)
                for j in range(len(friends)):
                    friendsww=friends[j]
                    if friendsww.get("status","none")!="none":
                        friendsstatus=friendsww["status"]
                        cur.execute("INSERT INTO friends( host_id,id,name,location,statuses_count,friends_count,gender,\
                                                profile_image_url,followers_count,favourites_count,\
                                                status_text,status_source) \
                                    values ('%d','%d','%s','%s','%d','%d','%s','%s','%d','%d','%s','%s')" % \
                                    (user_id,friendsww["id"],friendsww["name"],friendsww["location"],friendsww["statuses_count"],\
                                    friendsww["friends_count"],friendsww["gender"],friendsww["profile_image_url"],\
                                    friendsww["followers_count"],\
                                    friendsww["favourites_count"],\
                                    friendsstatus["text"].replace("\'","''"),\
                                    friendsstatus["source"]))
                        con.commit()
                    else:
                        cur.execute("INSERT INTO friends( host_id,id,name,location,statuses_count,friends_count,gender,\
                                                profile_image_url,followers_count,favourites_count) \
                                    values ('%d','%d','%s','%s','%d','%d','%s','%s','%d','%d')" % \
                                    (user_id,friendsww["id"],friendsww["name"],friendsww["location"],friendsww["statuses_count"],\
                                    friendsww["friends_count"],friendsww["gender"],friendsww["profile_image_url"],\
                                    friendsww["followers_count"],friendsww["favourites_count"]))
                        con.commit()
                    count=count+1
                    #print str(j) + os.linesep
        cur.close()
        con.close()            
    
            
    def imputdata (self,name,pageNum):
        #if bIsChiDead[0]==True:return
        
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS sina_users (u_id INTEGER PRIMARY KEY autoincrement,id integer  ,name text,\
                                            location text,description text,gender text,domain text,province text,\
                                            city text,statuses_count integer,friends_count integer,\
                                            profile_image_url text,created_at text,\
                                            status text,status_source text,status_time text)')
        con.commit()
        name=str(name)
        
        #if bIsChiDead[0]==True:return
        #print "sina:"+str(bIsChiDead[0])
        
        information=self.search_user(q=name,page=str(pageNum))
        if information[0] == "iseeu_error_exit":
            return "iseeu_error_exit"
        information=json.loads(information)            
        if len(information)==0:
            return "iseeu_nodata_again"
        for i in range(len(information)):
            info=information[i]
            prov_city=self.prov_and_city(province_num=info["province"],city_num=info["city"])
            gender=info["gender"]
            if gender == "m":
                zgender="男"
            elif gender == "f":
                zgender="女"
            zgender=zgender.decode("utf-8")
            prov=prov_city[0].decode("utf-8")
            city=prov_city[1].decode("utf-8")
            
            #if bIsChiDead[0]==True:return
            id = info["id"]
            sql = "select * from sina_users where id = %d" % id
            cur.execute(sql)
            con.commit()
            ret = cur.fetchall()
            if len(ret) > 0:
                "has the data already"
                continue
            
            if info.get("status","none")!="none":
                infostatus=info["status"]
                try:
                    cur.execute("INSERT INTO sina_users( id,name,location,description,gender,domain,province,city,\
                                            statuses_count,friends_count,profile_image_url,created_at,\
                                            status,status_source,status_time) \
                            values ('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                                        (info["id"],info["name"],info["location"],info["description"],\
                                        zgender,info["domain"],prov,city,\
                                        info["statuses_count"],info["friends_count"],info["profile_image_url"],\
                                        info["created_at"],infostatus["text"],infostatus["source"],infostatus["created_at"]))
                    con.commit()
                except sqlite3.OperationalError:
                    pass
                    #print "insert error"
            else:
                try:
                    cur.execute("INSERT INTO sina_users( id,name,location,description,gender,domain,province,city,\
                                                statuses_count,friends_count,profile_image_url,created_at) \
                                values ('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                                            (info["id"],info["name"],info["location"],info["description"],\
                                            zgender,info["domain"],prov,city,\
                                            info["statuses_count"],info["friends_count"],info["profile_image_url"],\
                                            info["created_at"]))
                    con.commit()
                except sqlite3.OperationalError:
                    #print "insert error"
                    pass
        cur.close()
        con.close()
        
    def search_status(self,q,page=1,rpp=200):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS status (u_id INTEGER PRIMARY KEY autoincrement,id integer ,status text,\
                                                    user_name text,user_id integer,user_location text,\
                                                    user_gender text,created_at text,source text)')
        con.commit()
        #while page<=100:
        self.mySearch = self.__api.search_status(q,page,rpp)
        status = json.loads(self.mySearch)
        if len(status)==0:
            return "iseeu_nodata_again"
        else:
            for i in range(len(status)):
                sta=status[i]
                user=sta["user"]
                try:
                    cur.execute("INSERT INTO status( id,status,user_name,user_id,user_location,user_gender,created_at,source) \
                                values ('%d','%s','%s','%d','%s','%s','%s','%s')" % \
                                                (sta["id"],sta["text"],user["name"],\
                                                user["id"],user["location"],user["gender"],sta["created_at"],sta["source"]))
                    con.commit()
                except sqlite3.OperationalError:
                    pass
            #print page
            #page=page+1  
        cur.execute("Delete from status where u_id not in (select min(u_id) from status group by id)" )
        con.commit()
        cur.close()
        con.close()
        print "status ok"
        
    def user_status(self,user_id,count=40,page=1,feature=0):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS user_status (u_id INTEGER PRIMARY KEY autoincrement,status_id integer ,status text,\
                                                    user_name text,user_id integer,created_at text,source text)')
        con.commit()
        self.mySearch=self.__api.user_timeline(user_id,count,page,feature)
        user_status=json.loads(self.mySearch)
        if len(user_status)==0:
            return "NULL"
        else:
            for i in range(len(user_status)):
                #print i
                sta=user_status[i]
                user=sta["user"]
                try:
                    cur.execute("INSERT INTO user_status(status_id,status,user_name,user_id,created_at,source) \
                                                values ('%d','%s','%s','%d','%s','%s')" % \
                                                (sta["id"],sta["text"],user["name"],\
                                                user["id"],sta["created_at"],sta["source"]))
                    con.commit()
                except sqlite3.OperationalError:
                    pass
        cur.close()
        con.close()
        return "success"
    
    def search_user_byid(self,user_id):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS sina_users (u_id INTEGER PRIMARY KEY autoincrement,id integer  ,name text,\
                                                location text,description text,gender text,domain text,province text,\
                                                city text,statuses_count integer,friends_count integer,\
                                                profile_image_url text,created_at text,\
                                                status text,status_source text,status_time text)')
        con.commit()
        self.mySearch = self.__api.get_user(user_id)
        info = json.loads(self.mySearch)
        try:
            dd=info['error_code']
            return
        except:
            pass
        prov_city=self.prov_and_city(province_num=info["province"],city_num=info["city"])
        prov=prov_city[0].decode("utf-8")
        city=prov_city[1].decode("utf-8")
        if info.get("status","none")!="none":
            infostatus=info["status"]
            try:
                cur.execute("INSERT INTO sina_users( id,name,location,description,gender,domain,province,city,\
                                            statuses_count,friends_count,profile_image_url,created_at,\
                                            status,status_source,status_time) \
                            values ('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                                        (info["id"],info["name"],info["location"],info["description"],\
                                        info["gender"],info["domain"],prov,city,\
                                        info["statuses_count"],info["friends_count"],info["profile_image_url"],\
                                        info["created_at"],infostatus["text"],infostatus["source"],infostatus["created_at"]))
                con.commit()
                #print "insert success"
            except sqlite3.OperationalError:
                #print "insert error"
                pass
        else:
            try:
                cur.execute("INSERT INTO sina_users( id,name,location,description,gender,domain,province,city,\
                                                statuses_count,friends_count,profile_image_url,created_at) \
                                values ('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                                            (info["id"],info["name"],info["location"],info["description"],\
                                            info["gender"],info["domain"],prov,city,\
                                            info["statuses_count"],info["friends_count"],info["profile_image_url"],\
                                            info["created_at"]))
                con.commit()
                #print "insert success"
            except sqlite3.OperationalError:
                #print "insert error"
                pass
        cur.close()
        con.close()
    
    def count_of_pageN(self, username, pageNum=10):
        pageNum=str(pageNum)
        recvdata=self.search_user(q=username,page=pageNum)
        recvdata=json.loads(recvdata)
        count=len(recvdata)
        return count
    
    def prov_and_city(self,province_num,city_num):
        province_dic={"11":"北京","12":"天津","13":"河北","14":"山西","15":"内蒙古","21":"辽宁","22":"吉林","23":"黑龙江",\
                      "31":"上海","32":"江苏","33":"浙江","34":"安徽","35":"福建","36":"江西","37":"山东","41":"河南",\
                      "42":"湖北","43":"湖南","44":"广东","45":"广西","46":"海南","50":"重庆","51":"四川","52":"贵州",\
                      "53":"云南","54":"西藏","61":"陕西","62":"甘肃","63":"青海","64":"宁夏","65":"新疆","71":"台湾",\
                      "81":"香港","82":"澳门","400":"海外","100":"其他"}
        city_dic = {"11":{"1":"东城区","2":"西城区","3":"崇文区","4":"宣武区","5":"朝阳区","6":"丰台区","7":"石景山区",\
                          "8":"海淀区","9":"门头沟区","11":"房山区","12":"通州区","13":"顺义区","14":"昌平区","15":"大兴区",\
                          "16":"怀柔区","17":"平谷区","28":"密云县","29":"延庆县"},
                    "12":{"1":"和平区","2":"河东区","3":"河西区","4":"南开区","5":"河北区","6":"红桥区","7":"塘沽区",\
                          "8":"汉沽区","9":"大港区","10":"东丽区","11":"西青区","12":"津南区","13":"北辰区","14":"武清区",\
                          "15":"宝坻区","21":"宁河县","23":"静海县","25":"蓟县"},
                    "13":{"1":"石家庄","2":"唐山","3":"秦皇岛","4":"邯郸","5":"邢台","6":"保定","7":"张家口",\
                          "8":"承德","9":"沧州","10":"廊坊","11":"衡水"},
                    "14":{"1":"太原","2":"大同","3":"阳泉","4":"长治","5":"晋城","6":"朔州","7":"晋中",\
                          "8":"运城","9":"忻州","10":"临汾","23":"吕梁"},
                    "15":{"1":"呼和浩特","2":"包头","3":"乌海","4":"赤峰","5":"通辽","6":"鄂尔多斯","7":"呼伦贝尔",\
                          "22":"兴安盟","25":"锡林郭勒盟","26":"乌兰察布盟","28":"巴彦淖尔盟","29":"阿拉善盟"},
                    "21":{"1":"沈阳","2":"大连","3":"鞍山","4":"抚顺","5":"本溪","6":"丹东","7":"锦州",\
                          "8":"营口","9":"阜新","10":"辽阳","11":"盘锦","12":"铁岭","13":"朝阳","14":"葫芦岛"},
                    "22":{"1":"长春","2":"吉林","3":"四平","4":"辽源","5":"通化","6":"白山","7":"松原",\
                          "8":"白城","24":"延边朝鲜族自治州"},
                    "23":{"1":"哈尔滨","2":"齐齐哈尔","3":"鸡西","4":"鹤岗","5":"双鸭山","6":"大庆","7":"伊春",\
                          "8":"佳木斯","9":"七台河","10":"牡丹江","11":"黑河","12":"绥化","27":"大兴安岭"},
                    "31":{"1":"黄浦区","3":"卢湾区","4":"徐汇区","5":"长宁区","6":"静安区","7":"普陀区","8":"闸北区",\
                          "9":"虹口区","10":"杨浦区","12":"闵行区","13":"宝山区","14":"嘉定区","15":"浦东新区",\
                          "16":"金山区","17":"松江区","18":"青浦区","19":"南汇区","20":"奉贤区","30":"崇明县"},
                    "32":{"1":"南京","2":"无锡","3":"徐州","4":"常州","5":"苏州","6":"南通","7":"连云港",\
                          "8":"淮安","9":"盐城","10":"扬州","11":"镇江","12":"泰州","13":"宿迁"},
                    "33":{"1":"杭州","2":"宁波","3":"温州","4":"嘉兴","5":"湖州","6":"绍兴","7":"金华",\
                          "8":"衢州","9":"舟山","10":"台州","11":"丽水"},
                    "34":{"1":"合肥","2":"芜湖","3":"蚌埠","4":"淮南","5":"马鞍山","6":"淮北","7":"铜陵",\
                          "8":"安庆","10":"黄山","11":"滁州","12":"阜阳","13":"宿州","14":"巢湖","15":"六安",\
                          "16":"毫州","17":"池州","18":"宣城"},
                    "35":{"1":"福州","2":"厦门","3":"莆田","4":"三明","5":"泉州","6":"漳州","7":"南平",\
                          "8":"龙岩","9":"宁德"},
                    "36":{"1":"南昌","2":"景德镇","3":"萍乡","4":"九江","5":"新余","6":"鹰潭","7":"赣州",\
                          "8":"吉安","9":"宜春","10":"抚州","11":"上饶"},
                    "37":{"1":"济南","2":"青岛","3":"淄博","4":"枣庄","5":"东营","6":"烟台","7":"潍坊",\
                          "8":"济宁","9":"泰安","10":"威海","11":"日照","12":"莱芜","13":"临沂","14":"德州",\
                          "15":"聊城","16":"滨州","17":"菏泽"},
                    "41":{"1":"郑州","2":"开封","3":"洛阳","4":"平顶山","5":"安阳","6":"鹤壁","7":"新乡",\
                          "8":"焦作","9":"濮阳","10":"许昌","11":"漯河","12":"三门峡","13":"南阳","14":"商丘",\
                          "15":"信阳","16":"周口","17":"驻马店"},
                    "42":{"1":"武汉","2":"黄石","3":"十堰","5":"宜昌","6":"襄樊","7":"鄂州","8":"荆门",\
                          "9":"孝感","10":"荆州","11":"黄冈","12":"咸宁","13":"随州","28":"恩施土家族苗族自治州"},
                    "43":{"1":"长沙","2":"株洲","3":"湘潭","4":"衡阳","5":"邵阳","6":"岳阳","7":"常德","8":"张家界",\
                          "9":"益阳","10":"郴州","11":"永州","12":"怀化","13":"娄底","31":"湘西土家族苗族自治州"},
                    "44":{"1":"广州","2":"韶关","3":"深圳","4":"珠海","5":"汕头","6":"佛山","7":"江门",\
                          "8":"湛江","9":"茂名","12":"肇庆","13":"惠州","14":"梅州","15":"汕尾",\
                          "16":"河源","17":"阳江","18":"清远","19":"东莞","20":"中山","51":"潮州",\
                          "52":"揭阳","53":"云浮"},
                    "45":{"1":"南宁","2":"柳州","3":"桂林","4":"梧州","5":"北海","6":"防城港","7":"钦州","8":"贵港",\
                          "9":"玉林","10":"白色","11":"贺州","12":"河池","21":"南宁","22":"柳州"},
                    "46":{"1":"海口","2":"三亚","90":"其他"},
                    "50":{"1":"万州区","2":"涪陵区","3":"渝中区","4":"大渡口区","5":"江北区","6":"沙坪坝区",\
                          "7":"九龙坡区","8":"南岸区","9":"北碚区","10":"万盛区","11":"双桥区","12":"渝北区",\
                          "13":"巴南区","14":"黔江区","15":"长寿区","22":"綦江县","23":"潼南县","24":"铜梁县",\
                          "25":"大足县","26":"荣昌县","27":"璧山县","28":"梁平县","29":"城口县","30":"丰都县",\
                          "31":"垫江县","32":"武隆县","33":"忠县","34":"开县","35":"云阳县","36":"奉节县",\
                          "37":"巫山县","38":"巫溪县","40":"石柱土家族自治县","41":"秀山土家族自治县",\
                          "42":"怀柔区酉阳土家族苗族自治县","43":"彭水苗族土家族自治县","81":"江津市",\
                          "82":"合川市","83":"永川市","84":"南川市"},
                    "51":{"1":"成都","3":"自贡","4":"攀枝花","5":"泸州","6":"德阳","7":"绵阳","8":"广元",\
                          "9":"遂宁","10":"内江","11":"乐山","13":"南充","14":"眉山","15":"宜宾","16":"广安",\
                          "17":"达州","18":"雅安","19":"巴中","20":"资阳","32":"阿坝","33":"甘孜","34":"凉山"},
                    "52":{"1":"贵阳","2":"六盘水","3":"遵义","4":"安顺","22":"铜仁","23":"黔西南",\
                          "24":"毕节","26":"黔东南","27":"黔南"},
                    "53":{"1":"昆明","3":"曲靖","4":"玉溪","5":"保山","6":"昭通","23":"楚雄","25":"红河","26":"文山",\
                          "27":"思茅","28":"西双版纳","29":"大理","31":"德宏","32":"丽江","33":"怒江","34":"迪庆",\
                          "35":"临沧"},
                    "54":{"1":"拉萨","21":"昌都","22":"山南","23":"日喀则","24":"那曲","25":"阿里","26":"林芝"},
                    "61":{"1":"西安","2":"铜川","3":"宝鸡","4":"咸阳","5":"渭南","6":"延安","7":"汉中",\
                          "8":"榆林","9":"安康","10":"商洛"},
                    "62":{"1":"兰州","2":"嘉峪关","3":"金昌","4":"白银","5":"天水","6":"武威","7":"张掖",\
                          "8":"平凉","9":"酒泉","10":"庆阳","24":"定西","26":"陇南","29":"临夏","30":"甘南"},
                    "63":{"1":"西宁","21":"海东","22":"海北","23":"黄南","25":"海南","26":"果洛","27":"玉树","28":"海西"},
                    "64":{"1":"银川","2":"石嘴山","3":"吴忠","4":"固原"},
                    "65":{"1":"乌鲁木齐","2":"克拉玛依","21":"吐鲁番","22":"哈密","23":"昌吉","27":"博尔塔拉","28":"巴音郭楞",\
                          "29":"阿克苏","30":"克孜勒苏","31":"喀什","32":"和田","40":"伊犁","42":"塔城","43":"阿勒泰"},
                    "71":{"1":"台北","2":"高雄","90":"其他"},
                    "81":{"1":"香港"},
                    "82":{"1":"澳门"},
                    "400":{"1":"美国","2":"英国","3":"法国","4":"俄罗斯","5":"加拿大","6":"巴西","7":"澳大利亚",\
                          "8":"印尼","9":"泰国","10":"马来西亚","11":"新加坡","12":"菲律宾","13":"越南","14":"印度",\
                          "15":"日本","16":"其他"},
                    "100":{}}
        province = province_dic.get(province_num," ")
        if province <> " ":
            city = city_dic.get(province_num," ").get(city_num," ")
        else:
            city=" "
        list = [province,city]
        return list
    
    def statistiek_of_statustime(self,user_id,table_name='user_status'):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        sql = "select created_at from %s where user_id=%d" % (table_name,int(user_id))
        cur.execute(sql)
        time=cur.fetchall()
        cur.close()
        con.close()
        count=len(time)
        hour_0_2,hour_2_4,hour_4_6,hour_6_8,hour_8_10,hour_10_12=(0,0,0,0,0,0)
        hour_12_14,hour_14_16,hour_16_18,hour_18_20,hour_20_22,hour_22_24=(0,0,0,0,0,0)
        for i in range(len(time)):
           hour=int(time[i][0].split(" ")[3].split(":")[0])
           #print hour
           if (hour>=0 and hour<2):
               hour_0_2+=1
           elif (hour>=2 and hour<4):
               hour_2_4+=1
           elif (hour>=4 and hour<6):
               hour_4_6+=1
           elif (hour>=6 and hour<8):
               hour_6_8+=1
           elif (hour>=8 and hour<10):
               hour_8_10+=1
           elif (hour>=10 and hour<12):
               hour_10_12+=1
           elif (hour>=12 and hour<14):
               hour_12_14+=1
           elif (hour>=14 and hour<16):
               hour_14_16+=1
           elif (hour>=16 and hour<18):
               hour_16_18+=1
           elif (hour>=18 and hour<20):
               hour_18_20+=1
           elif (hour>=20 and hour<22):
               hour_20_22+=1
           elif (hour>=22 and hour<24):
               hour_22_24+=1
        count = float(count)
        try:
            hour_0_2=(hour_0_2/count)
            hour_2_4=(hour_2_4/count)
            hour_4_6=(hour_4_6/count)
            hour_6_8=(hour_6_8/count)
            hour_8_10=(hour_8_10/count)
            hour_10_12=(hour_10_12/count)
            hour_12_14=(hour_12_14/count)
            hour_14_16=(hour_14_16/count)
            hour_16_18=(hour_16_18/count)
            hour_18_20=(hour_18_20/count)
            hour_20_22=(hour_20_22/count)
            hour_22_24=(hour_22_24/count)
        except:
            hour_0_2=hour_2_4=hour_4_6=hour_6_8=hour_8_10=hour_10_12=hour_12_14=hour_14_16=hour_16_18=hour_18_20=hour_20_22=hour_22_24=0           
        return [hour_0_2,hour_2_4,hour_4_6,hour_6_8,hour_8_10,hour_10_12,hour_12_14,
                hour_14_16,hour_16_18,hour_18_20,hour_20_22,hour_22_24]


    def comments(self, id=0, count=20, page = 1):
        '''
        statuses/comments 根据微博消息ID返回某条微博消息的评论列表 
        http://api.t.sina.com.cn/statuses/comments.(json|xml)   GET 

        source  true  string  申请应用时分配的AppKey，调用接口时候代表应用的唯一身份。（采用OAuth授权方式不需要此参数）  
        id  true  int64  指定要获取的评论列表所属的微博消息ID  
        count  false  int，默认值20，最大值200。  单页返回的记录条数。  
        page  false  int，默认值1。  返回结果的页码。

        字段说明 - comment 
        id: 评论ID 
        text: 评论内容 
        source: 评论来源 
        favorited: 是否收藏 
        truncated: 是否被截断 
        created_at: 评论时间 
        user: 评论人信息,结构参考user 
        status: 评论的微博,结构参考status 
        reply_comment 评论来源，数据结构跟comment一致 
        字段说明 - user 
        id: 用户UID 
        screen_name: 微博昵称 
        name: 友好显示名称，同微博昵称 
        province: 省份编码（参考省份编码表） 
        city: 城市编码（参考城市编码表） 
        location：地址 
        description: 个人描述 
        url: 用户博客地址 
        profile_image_url: 自定义图像 
        domain: 用户个性化URL 
        gender: 性别,m--男，f--女,n--未知 
        followers_count: 粉丝数 
        friends_count: 关注数 
        statuses_count: 微博数 
        favourites_count: 收藏数 
        created_at: 创建时间 
        following: 是否已关注(此特性暂不支持) 
        verified: 加V标示，是否微博认证用户 
        字段说明 - status 
        created_at: 创建时间 
        id: 微博ID 
        text: 微博信息内容 
        source: 微博来源 
        favorited: 是否已收藏 
        truncated: 是否被截断 
        in_reply_to_status_id: 回复ID 
        in_reply_to_user_id: 回复人UID 
        in_reply_to_screen_name: 回复人昵称 
        thumbnail_pic: 缩略图 
        bmiddle_pic: 中型图片 
        original_pic：原始图片 
        user: 作者信息 
        retweeted_status: 转发的博文，内容为status，如果不是转发，则没有此字段 
        '''
        comment_list = self.__api.comments(id, count=count, page=page)

        if comment_list <> '[]':
            #File_Write('ret_data/comment'+str(page)+'.txt', comment_list)
            comment_lists= json.loads(comment_list)
            if len(comment_lists) <= 0:
                return "comments nodata"
            else:
                print "comments num:",len(comment_lists)
                sina_sql = Sina_Sqlite()
                sina_sql.create_table()
                new_comment_lists = []
                for i in range(len(comment_lists)):
                    comment = comment_lists[i]
                    comment_dict = dict()
                    comment_dict["comment"] = comment.get('text', "")
                    user = comment.get("user", "")
                    comment_dict["user_id"] = user.get("id", 0)
                    comment_dict["user_name"] = user.get("name", "")
                    new_comment_lists.append(comment_dict)

                sina_sql.insert(new_comment_lists)
                sina_sql.del_repeat()
        else:
            return "comments nodata"
        
    def status_comment_count(self, id=0):
        '''
        statuses/counts 
        批量获取n条微博消息的评论数和转发数。一次请求最多可以获取20条微博消息的评论数和转发数 

        http://api.t.sina.com.cn/statuses/counts.(json|xml)   GET 是否需要登录 true  true关于请求数限制，参见接口访问权限说明 
        
        source  true  string  申请应用时分配的AppKey，调用接口时候代表应用的唯一身份。（采用OAuth授权方式不需要此参数）  
        ids  true  int64  要获取评论数和转发数的微博消息ID列表，用逗号隔开

        [{"id":2794158817,"comments":2,"rt":0}]
        comments: 评论条数
        rt: 转发条数
        '''
        comment_counts = self.__api.counts(id)
        #print comment_counts
        if comment_counts == '[]':
            return "status_comment_count no data"
        
        comment_counts = json.loads(comment_counts)
        try:
            return [comment_counts[0]["comments"], comment_counts[0]["rt"]]
        except Exception, e:
            print "get comment error:",e
            print comment_counts
            return "status_comment_count no data"
        

    def search_status_and_comment_count(self,q,page=1,rpp=200):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS status (u_id INTEGER PRIMARY KEY autoincrement,id integer ,status text,\
                                                    user_name text,user_id integer,user_location text,\
                                                    user_gender text,created_at text,source text,\
                                                    comment integer, rt integer)')
        con.commit()
        #while page<=100:
        self.mySearch = self.__api.search_status(q,page,rpp)
        status = json.loads(self.mySearch)
        if len(status)==0:
            return "iseeu_nodata_again"
        else:
            for i in range(len(status)):
                sta=status[i]
                idget = sta["id"]
                comment = self.status_comment_count(idget)
                if comment == "status_comment_count no data":
                    comment = [0,0]
                user=sta["user"]
                try:
                    cur.execute("INSERT INTO status( id,status,user_name,user_id,user_location,user_gender,created_at,source,comment,rt) \
                                values ('%d','%s','%s','%d','%s','%s','%s','%s',%d,%d)" % \
                                                (sta["id"],sta["text"],user["name"],\
                                                user["id"],user["location"],user["gender"],sta["created_at"],sta["source"],comment[0],comment[1]))
                    con.commit()
                except sqlite3.OperationalError:
                    pass
            #print page
            #page=page+1  
        cur.execute("Delete from status where u_id not in (select min(u_id) from status group by id)" )
        con.commit()
        cur.close()
        con.close()
        print "status ok"
        
    def trends_status (self, key, page=1, rpp = 200):
        con = sqlite3.connect('./sina.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS status (u_id INTEGER PRIMARY KEY autoincrement,id integer ,status text,\
                                                    user_name text,user_id integer,user_location text,\
                                                    user_gender text,created_at text,source text,\
                                                    comment integer, rt integer)')
        con.commit()
        trends_status_con = self.__api.trends_status(key, page, prepage=rpp)
        #print trends_status_con
        File_Write("data/status" + str(page) + '.txt', trends_status_con)
        #print "count:",len(json.loads(trends_status_con))
        status = json.loads(trends_status_con)
        if len(status)==0:
            return "iseeu_nodata_again"
        else:
            for i in range(len(status)):
                sta=status[i]
                idget = sta["id"]
                comment = self.status_comment_count(idget)
                if comment == "status_comment_count no data":
                    comment = [0,0]
                user=sta["user"]
                #check has the status or not
                sql = "select * from status where id = %d" % idget
                cur.execute(sql)
                con.commit()
                ret =cur.fetchall()
                if len(ret) > 0:
                    continue        
                try:
                    cur.execute("INSERT INTO status( id,status,user_name,user_id,user_location,user_gender,created_at,source,comment,rt) \
                                values ('%d','%s','%s','%d','%s','%s','%s','%s',%d,%d)" % \
                                                (sta["id"],sta["text"],user["name"],\
                                                user["id"],user["location"],user["gender"],sta["created_at"],sta["source"],comment[0],comment[1]))
                    con.commit()
                except Exception,e:
                    print "insert status error:",e
            #print page
            #page=page+1  
        '''cur.execute("Delete from status where u_id not in (select min(u_id) from status group by id)" )
        con.commit()'''
        cur.close()
        con.close()
        print "status ok"
        
def File_Write (path, data):
    f = file(path, 'w')
    f.write(data)
    f.close()
    return True

class Sina_Sqlite():
    def __init__ (self, dbname=''):
        self.con = sqlite3.connect('./sina.db')
        self.cur = self.con.cursor()

    def __del__ (self):
        self.cur.close()
        self.con.close()

    def create_table (self, type_para = None, tbname='sina_comments'):
        if not type_para:          #sina_commments table
            self.cur.execute("CREATE TABLE IF NOT EXISTS %s (\
                             cm_id INTEGER PRIMARY KEY autoincrement,\
                             user_name text, user_id text, status_id text, comment text)" % tbname)

        self.con.commit()
       
    def insert(self, in_data, tbname = 'sina_comments'):
        #in_data [{}]
        if type([]) == type(in_data):
            for i in range(len(in_data)):
                keys = in_data[i]
                key = ''
                value = ''
                for k, v in keys.items():
                    key += k + "," 
                    if type(u'a') == type(v):
                        value += "'" + v + "',"
                    else:
                        value += str(v) + ","
                sql = "insert into %s (" % tbname + key[:-1] + ") values(" + value[:-1] + ")"
                #print sql.encode('gbk')
                try:
                    self.cur.execute(sql)
                    self.con.commit()
                except Exception,e:
                    print "insert sina comment error:",e          
                
        
    def order (self, type = "comment", tbname = 'status'):
        sql = "select user_id,user_name,id,status,user_location,comment,rt from %s order by %s desc" % (tbname, type)
        try:
            self.cur.execute(sql)
            self.con.commit()
            result = self.cur.fetchall()
            newret = []
            for i in range(len(result)):
                new = []
                for j in range(len(result[i])):
                    new.append(result[i][j])
                new.append("sina.com.cn")
                newret.append(new)
            return newret

        except Exception,e:
            print "order sina comment error:",e         
            return False
        
    def del_repeat (self, tbname = 'sina_comments'):
        sql = "delete from %s where cm_id not in (select min(cm_id) from %s group by user_id)" % (tbname, tbname)
        try:
            self.cur.execute(sql)
            self.con.commit()
        except Exception,e:
            print "del_repeat sina comment error:",e         
        
    
if __name__ == "__main__":
    
    test=myapi()
    #test.search_user_byid('1684205261')
    #test.imputfriends(2031323277)
    #test.imputdata(name="李飞",pageNum=10)
    #k=test.prov_and_city("11","2")
    #print k
    
    #test.search_status('潘玮柏')

    #for i in range(10):
    #   print test.comments(13878744430, 20 ,i)

    #test.status_comment_count(2794158817)

    #test.search_status_and_comment_count('工作与生活是要区分开的')

    #test.comments(13878744430)
    for i in range(1):
        test.trends_status('工作与生活是要区分开的', i)    