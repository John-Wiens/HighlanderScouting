


import requests
import json
import logging
import pickle
import os
import numpy as np

import Processing
api_url = "https://www.thebluealliance.com/api/v3"
auth_key = "0Ws8VJsYtWRYmN6CQwahhtiM0vP4pl83J23Lpf4AqsdwmoLmRU7DkXYGDPTGUBWk"


class Data():
    def __init__(self):
        pass

    def save(self,f_name):
        pickle_out = open("{f}.pickle".format(f=f_name),"wb")
        pickle.dump(self, pickle_out)
        pickle_out.close()

class Team():
    def __init__(self,team_number):
        self.number = team_number
        self.OPR = 0
        self.cargo = 0
        self.hatches = 0
        self.climb = 0
        self.pr = 0
        self.hab = 0
    


class Event_Data(Data):
    def __init__(self, event_code):
        Data.__init__(self)
        logging.info("Creating Event Class: " + event_code)
        self.code = event_code

        self.event = None
        self.stats  = None
        self.teams = None
        self.rankings = None
        self.matches = None


        self.last_event_update = ""
        self.last_stats_update = ""
        self.last_teams_update = ""
        self.last_rankings_update = ""
        self.last_matches_update = ""
        self.export_data = None
        self.update_event_data()

        self.team_list = []
        
        self.team_data = []

    def get_team_list(self):
        team_list = []
        for row in self.teams:
            team_list.append(row['team_number'])
        team_list = sorted(team_list)
        self.team_list = team_list
        return team_list

    def get_num_matches(self):
        count = 0
        for match in self.matches:
            if match["comp_level"] == "qm":
                match_number = int(match["match_number"])
                if match_number > count:
                    count = match_number
        return count


    def update_event_data(self):
        self.event, self.last_event_update= self.update_entry(api_url + "/event/" + self.code,self.event,self.last_event_update)
        #self.update_entry(api_url + "/event/" + self.code + "/stats", self.stats, self.last_stats_update)
        self.teams, self.last_teams_update= self.update_entry(api_url + "/event/" + self.code + "/teams",self.teams,self.last_teams_update)
        self.rankings, self.last_rankings_update = self.update_entry(api_url + "/event/" + self.code + "/rankings",self.rankings,self.last_rankings_update)
        self.matches, self.last_matches_update = self.update_entry(api_url + "/event/" + self.code + "/matches",self.matches,self.last_matches_update)
      
    #generates match statistics for a given tournament
    def generate_match_power_data(self):

        team_list = self.get_team_list()
        #Load Lists of statistics (calculated using linear regression)
        opr = Processing.generate_ols_stat_list(self,"totalPoints",1)
        
        panels = Processing.generate_ols_stat_list(self,"hatchPanelPoints",1)
        cargo = Processing.generate_ols_stat_list(self,"cargoPoints",1) 

        #self.get_team_specific_data_arrays( "endgameRobot")
        climb, climb_detailed_array = self.get_team_climb_stats()
        hab, hab_detailed_array = self.get_team_hab_stats()
        # Populate the power rating graph from the other available statistics
        pr = np.zeros(len(team_list))
        export_data = np.array([team_list, opr, panels, cargo,climb,hab, pr])
        self.team_data = []
        for row in range(0,len(export_data[0])):
            
            value = 0
            for column in range(2,len(export_data)-1):
                value += export_data[column][row]
            export_data[-1][row] = value
            new_team = Team(export_data[0][row])
            new_team.OPR = export_data[1][row]
            new_team.hatches = export_data[2][row]
            new_team.cargo = export_data[3][row]
            new_team.climb = export_data[4][row]
            new_team.hab = export_data[5][row]
            new_team.pr = export_data[6][row]
            self.team_data.append(new_team)
        export_data = Processing.flip_array(export_data)
        #export_data = (export_data[np.argsort(export_data[:, 6])])[::-1]
        #print export_data
        self.stats = export_data
        return export_data



    # This will generate aditional data about teams that may be useful
    def generate_match_data(self):
        fpr = Processing.generate_stat_list(self,["foulCount"]["techFoulCount"],-5)

    #generates export data for a single tournament up to the round supplied
    def generate_export_data(self):
        #Check if export_data already exists
        if os.path.isfile("data/export_data.csv"):
            os.remove("data/export_data.csv")
        export_data = self.generate_match_power_data()

        # Format and export the numpy export_data array
        export_file = open("data/export_data.csv","w+")
        export_file.write("Team,OPR,Panels,Cargo,Climb,Hab Start, PR\n")
        np.around(export_data)
        np.savetxt(export_file, export_data,delimiter=",",fmt='%i,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f')
        export_file.close()
        return export_data

    def get_team_hab_stats(self):
        np_hab = np.array(self.get_team_specific_data_arrays( "habLineRobot"))
        hab_stats = np.zeros(len(self.team_list))

        np_level = np.array(self.get_team_specific_data_arrays("preMatchLevelRobot"))

        index = 0
        for c in np_hab:
            row = np.array(c)
            level = np.array(np_level[index])
            
            sandstorm = row == "CrossedHabLineInSandstorm"

            points = (level=="HabLevel1") *3 + (level=="HabLevel2") *6
            np.multiply(sandstorm,points)
            if len(row) > 0:
                sandstorm_score = np.sum(np.multiply(sandstorm,points))/len(row)
            else:
                sandstorm_score = 0
            hab_stats[index] = sandstorm_score
            #print(self.team_list[index],hab_score,hab3)
            index +=1

        return hab_stats, np_hab

    def get_team_climb_stats(self):
        np_climb = np.array(self.get_team_specific_data_arrays( "endgameRobot"))
        climb_stats = np.zeros(len(self.team_list))

        index = 0
        for c in np_climb:
            row = np.array(c)
            hab1 = row == "HabLevel1"
            hab2 = row == "HabLevel2" 
            hab3 = row == "HabLevel3"
            if len(row) > 0:
                hab_score = np.sum((3*hab1 + 6*hab2 + 12*hab3)/len(row))
            else:
                hab_score = 0
            climb_stats[index] = hab_score
            #print(self.team_list[index],hab_score,hab3)
            index +=1

        return climb_stats, np_climb
        




    def get_team_specific_data_arrays(self, stat):
        matches = self.matches
        team_list = self.team_list
        num_matches = self.get_num_matches()

        robot_stats = []
        for team in team_list:
            robot_stats.append([])

        for match in matches:
            if match["comp_level"] == "qm" and match["score_breakdown"] is not None:
                robot_number = 1
                for team in match["alliances"]["red"]["team_keys"]:
                    team_index = team_list.index(int(team[3:]))
                    
                    robot_stats[team_index].append( match["score_breakdown"]["red"][stat+str(robot_number)])
                    robot_number +=1

                robot_number = 1
                for team in match["alliances"]["blue"]["team_keys"]:
                    team_index = team_list.index(int(team[3:]))
                    robot_stats[team_index].append( match["score_breakdown"]["blue"][stat+str(robot_number)]) 
                    robot_number +=1



        return robot_stats


