import numpy as np
import json
import os

# The Event_Data Class will grab and store data from TBA so that data is only downloaded once
# All Other classes should reference this class for the data they need.
# This class will offer basic Data simplification for output
class Event_Data(object):
    def __init__(self,event_code):
        self.event_code = event_code
        self.last_update = ""
        if not os.path.isfile("tournaments/data_"+event_code+"/TBA/events.csv"):
            self.load_data_from_TBA()
        else:
            self.load_data()
        self.team_list = self.get_team_list()
        print 'Loading Data for: {0:10} ==>  Complete'.format(event_code)

    #loads data from the saved data files
    def load_data(self):
        f = open("tournaments/data_"+self.event_code+"/TBA/events.csv",'r')
        self.events = json.loads(f.read()) 
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/stats.csv",'r')
        self.stats = json.loads(f.read())
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/teams.csv",'r')
        self.teams = json.loads(f.read())
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/rankings.csv",'r')
        self.rankings = json.loads(f.read())
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/matches.csv",'r')
        self.matches = json.loads(f.read())
        f.close()
        
    # Grab Data from the Blue Alliance
    def load_data_from_TBA(self):    
        import TBA
        self.event = TBA.request_event(self.event_code)
        self.stats = TBA.request_event_stats(self.event_code)
        self.teams = TBA.request_event_teams(self.event_code)
        self.rankings = TBA.request_event_rankings(self.event_code)
        self.matches = TBA.request_event_matches(self.event_code)
        self.save_data()

    # Returns a list of teams at event in numeric order 
    def get_team_list(self):
        team_list = []
        for team in self.teams:
            team_list.append(team["team_number"])
        team_list = sorted(team_list)
        return team_list

    # Returns an array of OPR's sorted by ascending team Number
    def get_opr_list(self):
        data = np.zeros(len(self.team_list))
        for opr in oprs:
            index = self.team_list.index(int(opr))
            data[index] = oprs[opr]
        return data

    def save_data(self):
        f = open("tournaments/data_"+self.event_code+"/TBA/events.csv",'a')
        f.write(json.dumps(self.event))
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/stats.csv",'a')
        f.write(json.dumps(self.stats))
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/teams.csv",'a')
        f.write(json.dumps(self.teams))
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/rankings.csv",'a')
        f.write(json.dumps(self.rankings))
        f.close()
        f = open("tournaments/data_"+self.event_code+"/TBA/matches.csv",'a')
        f.write(json.dumps(self.matches))
        f.close()


    # Finds the number of matches that have happened so far
    def get_num_matches(self):
        count = 0
        for match in self.matches:
            if match["comp_level"] == "qm":
                match_number = int(match["match_number"])
                if match_number > count:
                    count = match_number
        return count

    def get_num_matches_all(self):
        count = 0
        for match in self.matches:
            if match["score_breakdown"] is not None:
                count = count + 1
        return count












