#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python client library for the Facebook Platform.

This client library is designed to support the Graph API and the official
Facebook JavaScript SDK, which is the canonical way to implement
Facebook authentication. Read more about the Graph API at
http://developers.facebook.com/docs/api. You can download the Facebook
JavaScript SDK at http://github.com/facebook/connect-js/.

If your application is using Google AppEngine's webapp framework, your
usage of this module might look like this:

    user = facebook.get_user_from_cookie(self.request.cookies, key, secret)
    if user:
        graph = facebook.GraphAPI(user["access_token"])
        profile = graph.get_object("me")
        friends = graph.get_connections("me", "friends")

"""

import cgi
import hashlib
import time
import urllib
import urllib2, cookielib
import sqlite3

# Find a JSON parser

import json



class GraphAPI(object):
    """A client for the Facebook Graph API.

    See http://developers.facebook.com/docs/api for complete documentation
    for the API.

    The Graph API is made up of the objects in Facebook (e.g., people, pages,
    events, photos) and the connections between them (e.g., friends,
    photo tags, and event RSVPs). This client provides access to those
    primitive types in a generic way. For example, given an OAuth access
    token, this will fetch the profile of the active user and the list
    of the user's friends:

       graph = facebook.GraphAPI(access_token)
       user = graph.get_object("me")
       friends = graph.get_connections(user["id"], "friends")

    You can see a list of all of the objects and connections supported
    by the API at http://developers.facebook.com/docs/reference/api/.

    You can obtain an access token via OAuth or by using the Facebook
    JavaScript SDK. See http://developers.facebook.com/docs/authentication/
    for details.

    If you are using the JavaScript SDK, you can use the
    get_user_from_cookie() method below to get the OAuth access token
    for the active user from the cookie saved by the SDK.
    """
    def __init__(self, access_token=None):
        self.access_token = access_token

    def get_object(self, id, **args):
        """Fetchs the given object from the graph."""
        return self.request(id, args)

    def get_objects(self, ids, **args):
        """Fetchs all of the given object from the graph.

        We return a map from ID to object. If any of the IDs are invalid,
        we raise an exception.
        """
        args["ids"] = ",".join(ids)
        return self.request("", args)

    def get_connections(self, id, connection_name, **args):
        """Fetchs the connections for given object."""
        return self.request(id + "/" + connection_name, args)

    def put_object(self, parent_object, connection_name, **data):
        """Writes the given object to the graph, connected to the given parent.

        For example,

            graph.put_object("me", "feed", message="Hello, world")

        writes "Hello, world" to the active user's wall. Likewise, this
        will comment on a the first post of the active user's feed:

            feed = graph.get_connections("me", "feed")
            post = feed["data"][0]
            graph.put_object(post["id"], "comments", message="First!")

        See http://developers.facebook.com/docs/api#publishing for all of
        the supported writeable objects.

        Most write operations require extended permissions. For example,
        publishing wall posts requires the "publish_stream" permission. See
        http://developers.facebook.com/docs/authentication/ for details about
        extended permissions.
        """
        assert self.access_token, "Write operations require an access token"
        return self.request(parent_object + "/" + connection_name, post_args=data)

    def put_wall_post(self, message, attachment={}, profile_id="me"):
        """Writes a wall post to the given profile's wall.

        We default to writing to the authenticated user's wall if no
        profile_id is specified.

        attachment adds a structured attachment to the status message being
        posted to the Wall. It should be a dictionary of the form:

            {"name": "Link name"
             "link": "http://www.example.com/",
             "caption": "{*actor*} posted a new review",
             "description": "This is a longer description of the attachment",
             "picture": "http://www.example.com/thumbnail.jpg"}

        """
        return self.put_object(profile_id, "feed", message=message, **attachment)

    def put_comment(self, object_id, message):
        """Writes the given comment on the given post."""
        return self.put_object(object_id, "comments", message=message)

    def put_like(self, object_id):
        """Likes the given post."""
        return self.put_object(object_id, "likes")

    def delete_object(self, id):
        """Deletes the object with the given ID from the graph."""
        self.request(id, post_args={"method": "delete"})

    def request(self, path, args=None, post_args=None):
        """Fetches the given path in the Graph API.

        We translate args to a valid query string. If post_args is given,
        we send a POST request to the given path with the given arguments.
        """
        if not args: args = {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)
        file = urllib.urlopen("https://graph.facebook.com/" + path + "?" +
                              urllib.urlencode(args), post_data)
        try:
            response = json.loads(file.read())
        finally:
            file.close()
        if response.get("error"):
            raise GraphAPIError(response["error"]["type"],
                                response["error"]["message"])
        return response


class GraphAPIError(Exception):
    def __init__(self, type, message):
        Exception.__init__(self, message)
        self.type = type


def get_user_from_cookie(cookies, app_id, app_secret):
    """Parses the cookie set by the official Facebook JavaScript SDK.

    cookies should be a dictionary-like object mapping cookie names to
    cookie values.

    If the user is logged in via Facebook, we return a dictionary with the
    keys "uid" and "access_token". The former is the user's Facebook ID,
    and the latter can be used to make authenticated requests to the Graph API.
    If the user is not logged in, we return None.

    Download the official Facebook JavaScript SDK at
    http://github.com/facebook/connect-js/. Read more about Facebook
    authentication at http://developers.facebook.com/docs/authentication/.
    """
    cookie = cookies.get("fbs_" + app_id, "")
    if not cookie: return None
    args = dict((k, v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items())
    payload = "".join(k + "=" + args[k] for k in sorted(args.keys())
                      if k != "sig")
    sig = hashlib.md5(payload + app_secret).hexdigest()
    expires = int(args["expires"])
    if sig == args.get("sig") and (expires == 0 or time.time() < expires):
        return args
    else:
        return None
    
    
class FaceLogin(object):
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd
        self.cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)
        
        url = "http://www.facebook.com"
        req = urllib2.Request(url)
        ret = self.opener.open(req).read()
        
        ret = ret[ret.find('action="https://www.facebook.com/login.php?login_attempt=1"'):]
        ret = ret[:ret.find('</form>')]
        
        self.charset_test = ret[ret.find('name="charset_test"'):]
        self.charset_test = self.charset_test[self.charset_test.find('value="')+7:]
        self.charset_test = self.charset_test[:self.charset_test.find('"')]
        #print self.charset_test
        
        self.lsd = ret[ret.find('name="lsd"'):]
        self.lsd = self.lsd[self.lsd.find('value="')+7:]
        self.lsd = self.lsd[:self.lsd.find('"')]
        print self.lsd
        
        self.Login()
        
    def Login(self):
        url = 'https://www.facebook.com/login.php?login_attempt=1'
        params = {
                "charset_test":self.charset_test,
                "lsd":self.lsd,
                "locale":"zh_CN",
                "email":self.user,
                "pass":self.passwd,
                "persistent":"1",
                "default_persistent":"1",
                "charset_test":self.charset_test,
                "lsd":self.lsd
                }
        params = urllib.urlencode(params)
        #print params
        req = urllib2.Request(url, params)
        ret = self.opener.open(req).read()
        
#        f = file("face.html",'w')
#        f.write(ret)
#        f.close()
        
    def Get_Access_Token(self):
        url = "https://developers.facebook.com/apps"
        req = urllib2.Request(url)
        ret = self.opener.open(req).read()
        #Access Token\u003c\/div>\u003c\/td>\u003ctd class=\"contentPane\">\u003cdiv class=\"mvs\">\u003cspan>\u003cdiv class=\"mvl pas developerAppAccessToken uiBoxLightblue\">\u003cspan class=\"fss fwn\">161486763924570|2.AQDsdRWVho_0RFUU.3600.1310652000.0-100002613500596|mxMukX2wFGTV7d8nTF5E_qtwPUc\u003c\/span>
        access = ret[ret.find('Access Token'):]
        access = access[:access.find("/span>")]
        access = access[access.find('span')+4:]
        access = access[access.find('span')+4:]
        access = access[access.find('>')+1:]
        access = access[:access.find("\u003c")]
        #print access
        
        return access



class FacebookApi(object):
    def __init__(self, user="1015512573@qq.com", passwd="jiapeng881002"):
        self.user=user
        self.passwd=passwd
        test = FaceLogin(self.user,self.passwd)
        self.access_token = test.Get_Access_Token()
        
    def request(self,q,type):
        args = {}
        args["q"] = q
        args["type"] = type
        args["access_token"] = self.access_token
        file = urllib.urlopen("https://graph.facebook.com/" + "search" + "?" +
                             urllib.urlencode(args))
        try:
           response = json.loads(file.read())
        finally:
           file.close()
        if response.get("error"):
           raise GraphAPIError(response["error"]["type"],
                               response["error"]["message"])
        return response
   
   
    def get_users(self,name):
        users = self.request(q=name,type="user")
        #print users
        #print len(users["data"])
        users = users["data"]
        id_list = []
        for i in range(len(users)):
            id_list.append(users[i]["id"])
        #print id_list
        id_tuple = tuple(id_list)
        k = GraphAPI(self.access_token)
        information = k.get_objects(id_tuple)
        info = information.values() 
        #print info
        if len(info)==0:
            print "There is no data"
            return 
        con = sqlite3.connect('./facebook.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS facebook_users (u_id INTEGER PRIMARY KEY autoincrement,id integer ,\
                                                            name text,locale text,gender text,\
                                                            link text,updated_time text)')
        con.commit()
        for j in range(len(info)):
            info_j = info[j]
            #print type(info_j["id"])
            gender = ""
            if info_j["gender"] == "male":
                gender = "\xc4\xd0".decode("gbk")
            elif info_j["gender"] == "female":
                gender = "\xc5\xae".decode("gbk")
            try:
                cur.execute("INSERT INTO facebook_users (id,name,locale,gender,link,updated_time) \
                                                values ('%s','%s','%s','%s','%s','%s')" % \
                                                (info_j["id"],info_j["name"],info_j["locale"],gender,\
                                                info_j["link"],info_j["updated_time"]))
                con.commit()
            except:
                pass
        cur.close()
        con.close()
        return True
    
    def get_status(self,key):
        args = {}
        args["until"] = "yesterday"
        args["q"] = key
        file = urllib.urlopen("https://graph.facebook.com/" + "search" + "?" +
                             urllib.urlencode(args))
        try:
           response = json.loads(file.read())
        finally:
           file.close()
        if response.get("error"):
            raise GraphAPIError(response["error"]["type"],
                               response["error"]["message"])
            return 
        info = response["data"]
        con = sqlite3.connect('./facebook.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS facebook_status (u_id INTEGER PRIMARY KEY autoincrement,id text ,\
                                                            picture text,user_name text,user_id text,message text,type text,\
                                                            link text,updated_time text,caption text)')
        con.commit()
        for j in range(len(info)):
            info_j = info[j]
            #print type(info_j["id"])
            #try:
            cur.execute("INSERT INTO facebook_status (id,picture,user_name,user_id,message,type,link,updated_time,caption) \
                                            values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
                                            (info_j["id"],info_j.get("picture"," "),info_j["from"]["name"],\
                                            info_j["from"]["id"],info_j.get("message"," "),info_j.get("type"," "),\
                                            info_j.get("link"," "),info_j["updated_time"],info_j.get("caption"," ")))
            con.commit()
            #except:
                #pass
        cur.close()
        con.close()
        #print success
    
class Facebook_Sql():
    def __init__(self, dbname="facebook"):
        self.con = sqlite3.connect("./"+ dbname +".db")
        self.cur = self.con.cursor()
        
    def get_users(self, name, index=0, tbname = "facebook_users"):
        name = "%"+name+"%"
        #sql = "select id, name, gender, locale from %s where name like '%s'" % (tbname, name)
        #print sql
        sql = "select id, name, gender, locale from %s" % (tbname,)
        self.cur.execute(sql)
        self.con.commit()
        if index > 0:
            self.cur.fetchmany(index)
        ret = self.cur.fetchall()
        newret = []
        for i in range(len(ret)):
            new = []
            for j in range(len(ret[i])):
                if ret[i][j] == None:
                    new.append("")
                else:
                    new.append(ret[i][j])
            new.append("")
            new.append("facebook.com")
            newret.append(new)
                
        return newret
        
    def get_status(self, index=0, tbname = "facebook_status"):
        sql = "select user_id, user_name, id, message, caption from %s" % (tbname,)
        #print sql
        self.cur.execute(sql)
        self.con.commit()
        if index >0:
            self.cur.fetchmany(index)
        ret = self.cur.fetchall()
        newret = []
        for i in range(len(ret)):
            new = []
            for j in range(len(ret[i])):
                if ret[i][j] == None:
                    new.append("")
                    continue
                if j == 3:
                    new.append(ret[i][j] + "(" + ret[i][j+1] + ")")
                    break
                new.append(ret[i][j])
            new.append("")
            new.append("")
            new.append("")
            new.append("facebook.com")
            newret.append(new)
        return newret
    
    def clear_all(self, tbname = "facebook_users"):
        sql = "delete from %s" % tbname
        try:
            self.cur.execute(sql)
            self.con.commit() 
        except Exception,e:
            print "clear %s failed" % tbname
            
    def __del__(self):
        self.cur.close()
        self.con.close()
    
        
        
if __name__ == "__main__":  
    
    ke = raw_input(">")
    ke = ke.decode('gbk').encode('utf-8')
    print repr(ke)
    
    test = FacebookApi()
    #sql = Facebook_Sql()
    #print sql.get_users(ke)
    #list = test.get_status(ke)
    test.get_users(ke)
    #fl = FaceLogin("1015512573@qq.com","jiapeng881002")


        
        
#https://graph.facebook.com/search?until=yesterday&q=orange 
