
import requests
import json


api_url = 'http://www.thebluealliance.com/api/v3/'
#c = http.client.HTTPSConnection(api_url)

auth_key = '0Ws8VJsYtWRYmN6CQwahhtiM0vP4pl83J23Lpf4AqsdwmoLmRU7DkXYGDPTGUBWk'


class TBA():
    def __init__(self):
        self.LM_key_list = ""
        pass

    def make_tba_request(self, key_string, last_modified):
        header = {'X-TBA-Auth-Key':auth_key,'If-Modified-Since':last_modified}
        r = requests.get(api_url + key_string, headers=header)
        return r

    def request_event_key_list(self,year,last_modified=""):
        self.make_tba_request("events/{year}/keys".format(year=year),last_modified)
        return  r

    def request_event(self,code):
        c.putrequest("GET", "/api/v2/event/" + str(code))
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        return jsonData

    def request_event_stats(self,code): # OPR, DPR etc...
        c.putrequest("GET", "/api/v3/event/" + code + "/stats")
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        return jsonData

    def request_event_rankings(self,code): # Rankings, win-loss record etc...
        c.putrequest("GET", "/api/v2/event/" + code + "/rankings")
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        return jsonData

    def request_event_teams(self,code):
        c.putrequest("GET", "/api/v2/event/" + code + "/teams")
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        return jsonData

    def request_event_matches(self,code):
        c.putrequest("GET", "/api/v2/event/" + code + "/matches")
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        return jsonData

    def request_team_info(self,team): 
        c.putrequest("GET", "/api/v2/team/frc" + str(team))
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        jsonData = json.loads(data)
        return jsonData

    def request_team_event_info(self,team):
        c.putrequest("GET", "/api/v2/team/frc" + str(team) + "/2017/events")
        c.putheader(header,app)
        c.endheaders()
        response = c.getresponse()
        data = response.read()
        #print data
        if len(data)> 0:
            jsonData = json.loads(data)
            return jsonData
        else:
            return None