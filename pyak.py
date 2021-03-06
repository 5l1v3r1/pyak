import json
import requests
import time
import urllib

def parse_time(timestr):
    format = "%Y-%m-%d %H:%M:%S"
    return time.mktime(time.strptime(timestr, format))

class Location:
    def __init__(self, latitude, longitude, delta=None):
        self.latitude = latitude
        self.longitude = longitude
        if delta is None:
            delta = "0.030000"
        self.delta = delta

class Comment:
    def __init__(self, raw, message_id, client):
        self.client = client
        self.message_id = message_id
        self.comment_id = raw["commentID"]
        self.comment = raw["comment"]
        self.time = parse_time(raw["time"])
        self.likes = int(raw["numberOfLikes"])
        self.poster_id = raw["posterID"]
        self.liked = int(raw["liked"])

    def upvote(self):
        if self.liked == 0:
            self.likes += 1
            self.liked += 1
            return self.client.upvote_comment(self.comment_id)

    def downvote(self):
        if self.liked == 0:
            self.likes -= 1
            self.liked += 1
            return self.client.downvote_comment(self.comment_id)

    def report(self):
        return self.client.report_comment(self.comment_id, self.message_id)

    def delete(self):
        if self.poster_id == self.client.id:
            return self.client.delete_comment(self.comment_id, self.message_id)

    def reply(self, comment):
        return self.client.post_comment(self.message_id, comment)

    def print_comment(self):
        my_action = ""
        if self.liked > 0:
            my_action = "^"
        elif self.liked < 0:
            my_action = "v"
        print "%s(%s) %s" % (my_action, self.likes, self.comment)

class Yak:
    def __init__(self, raw, client):
        self.client = client
        self.poster_id = raw["posterID"]
        self.hide_pin = bool(int(raw["hidePin"]))
        self.handle = raw["handle"]
        self.message_id = raw["messageID"]
        self.delivery_id = raw["deliveryID"]
        self.longitude = raw["longitude"]
        self.comments = int(raw["comments"])
        self.time = parse_time(raw["time"])
        self.latitude = raw["latitude"]
        self.likes = int(raw["numberOfLikes"])
        self.message = raw["message"]
        self.type = raw["type"]
        self.liked = int(raw["liked"])
        self.reyaked = raw["reyaked"]

    def upvote(self):
        if self.liked == 0:
            self.liked += 1
            self.likes += 1
            return self.client.upvote_yak(self.message_id)

    def downvote(self):
        if self.liked == 0:
            self.liked -= 1
            self.likes -= 1
            return self.client.downvote_yak(self.message_id)

    def report(self):
        return self.client.report_yak(self.message_id)

    def delete(self):
        if self.poster_id == self.client.id:
            return self.client.delete_yak(self.message_id)

    def add_comment(self, comment):
        return self.client.post_comment(self.message_id, comment)

    def get_comments(self):
        return self.client.get_comments(self.message_id)

    def print_yak(self):
        if self.handle is not None:
            print "%s:" % self.handle
        print self.message
        print "%s likes, %s comments. posted %s at %s %s" % (self.likes, self.comments, self.time, self.latitude, self.longitude)

class Yakker:
    base_url = "http://www.yikyakapp.com/YikYakFiles/"
    user_agent = "android-async-http/1.4.4 (http://loopj.com/android-async-http)"
    
    def __init__(self, user_id=None):
        if user_id is None:
            user_id = self.register_id()
        
        self.id = user_id
        self.location = Location("0", "0")
        self.handle = None

        #self.update_stats()
        
    def get(self, page, params):
        url = self.base_url + page
        if len(params) > 0:
            url += "?" + urllib.urlencode(params)
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip",
        }
        
        return requests.get(url, headers=headers)

    def get_yak_list(self, page, params):
        return self.parse_yaks(self.get(page, params).text)
        
    def parse_yaks(self, text):
        try:
            raw_yaks = json.loads(text)["messages"]
        except:
            raw_yaks = []
        yaks = []
        for raw_yak in raw_yaks:
            yaks.append(Yak(raw_yak, self))
        return yaks

    def parse_comments(self, text, message_id):
        try:
            raw_comments = json.loads(text)["comments"]
        except:
            raw_comments = []
        comments = []
        for raw_comment in raw_comments:
            comments.append(Comment(raw_comment, message_id, self))
        return comments

    def contact(self, message):
        params = {
            "userID": self.id,
            "message": message
        }
        return self.get("contactUs.php", params)

    def upvote_yak(self, message_id):
        params = {
            "userID": self.id,
            "messageID": message_id
        }
        return self.get("likeMessage.php", params)

    def downvote_yak(self, message_id):
        params = {
            "userID": self.id,
            "messageID": message_id
        }
        return self.get("downvoteMessage.php", params)

    def upvote_comment(self, comment_id):
        params = {
            "userID": self.id,
            "commentID": comment_id
        }
        return self.get("likeComment.php", params)

    def downvote_comment(self, comment_id):
        params = {
            "userID": self.id,
            "commentID": comment_id
        }
        return self.get("downvoteComment.php", params)

    def report_yak(self, message_id):
        params = params = {
            "userID": self.id,
            "messageID": message_id
        }
        return self.get("reportMessage.php", params)

    def delete_yak(self, message_id):
        params = params = {
            "userID": self.id,
            "messageID": message_id
        }
        return self.get("deleteMessage2.php", params)

    def report_comment(self, comment_id, message_id):
        params = {
            "userID": self.id,
            "commentID": comment_id,
            "messageID": message_id,
        }
        return self.get("reportMessage.php", params)

    def delete_comment(self, comment_id, message_id):
        params = {
            "userID": self.id,
            "commentID": comment_id,
            "messageID": message_id,
        }
        return self.get("deleteComment.php", params)

    def update_handle(self, handle):
        success = False 
        if handle != self.handle:
            self.handle = handle
            params = {
                "userID": self.id,
                "handle": self.handle
            }
            success = bool(self.get("updateHandle.php", params) == "0")

        return success

    def get_handle_info(self):
        params = {
            "userID": self.id,
        }
        return self.get("getHandleInfo.php", params).text

    def update_stats(self):
        params = {
            "userID": self.id,
        }
        stats = self.get("getMyStats.php", params).text.split()
        #TODO: fix this for real...
        try:
            self.num_messages = int(stats[0])
            self.neg3 = int(stats[1])
            self.upvotes_given = int(stats[2])
            self.downvotes_given = int(stats[3])
            self.yak_score = int(stats[4])
        except IndexError:
            pass
        
    def get_greatest(self):
        return self.get_yak_list("getGreatest.php", {})
        
    def get_my_tops(self):
        params = {
            "userID": self.id,
        }
        return self.get_yak_list("getMyTops.php", params)
        
    def get_recent_replied(self):
        params = {
            "userID": self.id,
        }
        return self.get_yak_list("getMyRecentReplied.php", params)
        
    def update_location(self, location):
        self.loc = location
        params = {
            "userID": self.id,
            "lat": location.latitude,
            "long": location.longitude,
        }

        return self.get("updateLocation.php", params)
        
    def get_my_recent_yaks(self):
        params = {
            "userID": self.id,
        }
        return self.get_yak_list("getMyRecentYaks.php", params)
        
    def get_area_tops(self, loc=None):
        if loc is None:
            loc = self.location
        params = {
            "lat": loc.latitude,
            "long": loc.longitude,
        }
        return self.get_yak_list("getAreaTops.php", params)
    
    def get_yaks(self):
        params = {
            "userID": self.id,
        }
        return self.get_yak_list("getMessages.php", params)
    
    def post_yak(self, message, loc=None, showloc=False, handle=False):
        if loc is None:
            loc = self.location
        params = {
            "userID": self.id,
            "lat": loc.latitude,
            "long": loc.longitude,
            "message": message,
        }
        if not showloc:
            params["hidePin"] = "1"
        if handle and (self.handle is not None):
            params["hndl"] = self.handle
        return self.get("sendMessage.php", params)

    def get_comments(self, message_id):
        params = {
            "userID": self.id,
            "messageID": message_id
        }
            
        return self.parse_comments(self.get("getComments.php", params).text, message_id)
        
    def post_comment(self, message_id, comment):
        params = {
            "userID": self.id,
            "messageID": message_id,
            "comment": comment,
        }
        return self.get("postComment.php", params)
    
    def peek(self, location):
        params = {
            "userID": self.id,
            "lat": location.latitude,
            "long": location.longitude,
            "delta": location.delta,
        }
        return self.get_yak_list("getPeekMessages.php", params)
    
    def register_id(self):
        result = self.get("registerUserDroid.php", {})
        return result.text
