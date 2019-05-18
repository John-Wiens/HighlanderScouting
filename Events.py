
import pickle
import numpy as np
import TBA
import Processing
import datetime
import os
import S3Manager

# Events will be completely classified by their TBA event codes which include both a year and an event number
# Events will primarily contain a Data Array with stats for every team, and will provide Labeled Headers for the Data
class Event_2019():
    def __init__(self, event_code):
        self.code = event_code
        self.last_update_time = ""
        
        self.event = None
        self.stats  = None # Array of Team Stats [Team, OPR, Panels, Cargo, Climb, Hab Start, PR]
        self.stats_var = None # Array of Team Stat Variances [Team, OPR, Panels, Cargo, Climb, Hab Start, PR]
        self.previous_stats = None
        self.previous_stats_var = None

        self.teams = None
        self.rankings = None
        self.matches = None

        self.predictions = None
        self.predictions_rp = None
        self.predictions_final = None
        self.schedule_strength = None

        self.update()
        self.team_list = self.get_team_list()
        
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

    def serialize(self):
        return pickle.dumps(self)

    def save(self,f_name):
        pickle_out = open("{f}.pickle".format(f=f_name),"wb")
        pickle.dump(self, pickle_out)
        pickle_out.close()

    def update(self):
        if TBA.check_tba_connection():
            if(TBA.check_tba_new_data("/event/" + self.code,self.last_update_time)) or True:
                print("Updating: {}".format(self.code))
                self.event, _ = TBA.update_entry("/event/" + self.code, self.event, self.last_update_time)
                self.teams, _ = TBA.update_entry("/event/" + self.code + "/teams",self.teams,self.last_update_time)
                self.rankings, _ = TBA.update_entry("/event/" + self.code + "/rankings",self.rankings,self.last_update_time)
                self.matches, self.last_update_time = TBA.update_entry("/event/" + self.code + "/matches",self.matches,self.last_update_time)
                self.update_team_stats()
                #print(self.matches[0])
                self.predictions = Processing.predict_matches(self)
                self.predictions_rp = self.predict_match_rp()
                self.predictions_final = self.predict_final_rankings()
                self.schedule_strength = self.get_schedule_strength()
                S3Manager.write_s3_bucket(self)
            else:
                print("{} is already Up to Date".format(self.code))
        else:
            print("Unable to Connect to TBA")
        

    def predict_final_rankings(self):
        #Team Num, Expected RP, Expected Cargo, Expected Hatch, Expected Climb
        rp_predictions = np.zeros(len(self.team_list))
        cargo_predictions = np.zeros(len(self.team_list))
        hatch_predictions = np.zeros(len(self.team_list))
        climb_predictions = np.zeros(len(self.team_list))
        matches = self.matches
        team_list = self.get_team_list()
        match_index = 0
        teams_played = 0
        for match in matches:
            if match["comp_level"] == 'qm':
                for team in match["alliances"]["red"]["team_keys"]:
                    team_index = team_list.index(int(team[3:]))
                    if match["score_breakdown"] is not None:
                        teams_played +=1
                        cargo_predictions[team_index] += match["score_breakdown"]["red"]["cargoPoints"]
                        hatch_predictions[team_index] += match["score_breakdown"]["red"]["hatchPanelPoints"]
                        climb_predictions[team_index] += match["score_breakdown"]["red"]["habClimbPoints"]
                        rp_predictions[team_index] += match["score_breakdown"]["red"]["habDockingRankingPoint"] 
                        rp_predictions[team_index] += match["score_breakdown"]["red"]["completeRocketRankingPoint"]
                        rp_predictions[team_index] += 2 if int(match["score_breakdown"]["red"]["totalPoints"]) > int(match["score_breakdown"]["blue"]["totalPoints"]) else 0
                        rp_predictions[team_index] += 2 if int(match["score_breakdown"]["red"]["totalPoints"]) == int(match["score_breakdown"]["blue"]["totalPoints"]) else 0
                    else:
                        rp_predictions[team_index] += self.predictions_rp[match_index][0] + self.predictions_rp[match_index][1]
                        rp_predictions[team_index] += 2 if self.predictions[match_index][1] >= self.predictions[match_index][3] else 0

                for team in match["alliances"]["blue"]["team_keys"]:
                    team_index = team_list.index(int(team[3:]))
                    if match["score_breakdown"] is not None:
                        teams_played +=1
                        cargo_predictions[team_index] += match["score_breakdown"]["blue"]["cargoPoints"]
                        hatch_predictions[team_index] += match["score_breakdown"]["blue"]["hatchPanelPoints"]
                        climb_predictions[team_index] += match["score_breakdown"]["blue"]["habClimbPoints"]
                        rp_predictions[team_index] += match["score_breakdown"]["blue"]["habDockingRankingPoint"] 
                        rp_predictions[team_index] += match["score_breakdown"]["blue"]["completeRocketRankingPoint"]
                        rp_predictions[team_index] += 2 if int(match["score_breakdown"]["red"]["totalPoints"]) < int(match["score_breakdown"]["blue"]["totalPoints"]) else 0
                        rp_predictions[team_index] += 2 if int(match["score_breakdown"]["red"]["totalPoints"]) == int(match["score_breakdown"]["blue"]["totalPoints"]) else 0
                    else:
                        rp_predictions[team_index] += self.predictions_rp[match_index][2] + self.predictions_rp[match_index][3]
                        rp_predictions[team_index] += 2 if self.predictions[match_index][1] <= self.predictions[match_index][3] else 0
                match_index +=1
        
        matches_remaining = match_index - self.get_highest_qual_match_played()
        average_cargo = np.average(self.stats[:,3])
        average_hatches = np.average(self.stats[:,2])
        average_climb = np.average(self.stats[:,4])

        cargo_predictions += (self.stats[:,3] + average_cargo) * matches_remaining
        hatch_predictions += (self.stats[:,2] + average_hatches) * matches_remaining
        climb_predictions += (self.stats[:,4] + average_climb) * matches_remaining

        final_predictions = np.array([team_list, rp_predictions, cargo_predictions, hatch_predictions, climb_predictions])
        return Processing.flip_array(final_predictions)

    def get_highest_qual_match_played(self):
        highest = 0
        for match in self.matches:
            if match["score_breakdown"] is not None:
                num = int(float(match["match_number"]))
                if num > highest:
                    highest = num
        return highest

    #generates match statistics for a given tournament
    def update_team_stats(self):
        team_list = self.get_team_list()
        if self.get_highest_qual_match_played() > 10:
            # Load Lists of statistics (calculated using linear regression)
            opr = Processing.generate_ols_stat_list(self,"totalPoints",1)
            opr_var = Processing.get_stat_variance(self,"totalPoints",opr)

            panels = Processing.generate_ols_stat_list(self,"hatchPanelPoints",1)
            panel_var = Processing.get_stat_variance(self,"hatchPanelPoints",panels)

            cargo = Processing.generate_ols_stat_list(self,"cargoPoints",1)
            cargo_var = Processing.get_stat_variance(self,"cargoPoints",cargo) 

            # Load Data On Statistics that are known on a per robot basis
            climb, climb_var = self.get_team_climb_stats()
        

            hab, hab_var = self.get_team_hab_stats()

            # Populate the power rating graph from the other available statistics
            pr = np.zeros(len(team_list))
            export_data = np.array([team_list, opr, panels, cargo,climb,hab, pr])
            export_data_var = np.array([team_list, opr_var, panel_var, cargo_var, climb_var, hab_var, pr])
            for row in range(0,len(export_data[0])):
                value = 0
                value_var = 0
                for column in range(2,len(export_data)-1):
                    value += export_data[column][row]
                    value_var += export_data_var[column][row]
                export_data[-1][row] = value
                export_data_var[-1][row] = value_var
            self.stats = Processing.flip_array(export_data)
            self.stats_var = Processing.flip_array(export_data_var)
        else:
            if self.previous_stats is None:
                print("Calculating Previous Event Stats: ", self.code)
                stats = np.zeros((len(self.team_list),7))
                stats_var = np.zeros((len(self.team_list),7))
                i = 0
                for team in self.team_list:
                    stat, var = self.get_team_opr_history(team, 2019)
                    stats[i] += stat
                    stats_var[i] += var
                    i+=1
                self.previous_stats = stats
                self.previous_stats_var = stats_var

                self.stats = stats
                self.stats_var = stats_var
            #print(self.stats)
        #generates export data for a single tournament up to the round supplied
    def export_csv(self):

        self.update()

        #Check if export_data already exists
        if os.path.isfile("data/{code}.csv".format(code=self.code)):
            os.remove("data/{code}.csv".format(code=self.code))
        

        # Format and export the numpy export_data array
        export_file = open("data/export_data.csv","w+")
        export_file.write("Team,OPR,Panels,Cargo,Climb,Hab Start, PR\n")
        np.around(export_data)
        np.savetxt(export_file, export_data,delimiter=",",fmt='%i,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f')
        export_file.close()
        return export_data

    def predict_match_rp(self):
        matches = self.matches
        team_list = self.get_team_list()
        team_rocket_powers = Processing.generate_ols_stat_list(self,"completeRocketRankingPoint",1)
        # Red Climb, Red Rocket, Blue Climb, Blue Rocket
        rp = np.zeros((len(self.matches),4))
        match_index = 0
        for match in matches:
            if match["comp_level"] == 'qm': 
                if match["score_breakdown"] is None:
                    red_climb_power = 0
                    red_rocket_power = 0
                    for team in match["alliances"]["red"]["team_keys"]:
                        team_index = team_list.index(int(team[3:]))
                        red_climb_power += self.stats[team_index][4]
                        red_rocket_power += team_rocket_powers[team_index]
                    if red_climb_power >=15:
                        rp[match_index][0] = 1
                    if red_rocket_power >= 1:
                        rp[match_index][1] = 1

                
                    blue_climb_power = 0
                    blue_rocket_power = 0
                    for team in match["alliances"]["blue"]["team_keys"]:
                            team_index = team_list.index(int(team[3:]))
                            blue_climb_power += self.stats[team_index][4]
                            blue_rocket_power += team_rocket_powers[team_index]
                    if blue_climb_power >=15:
                        rp[match_index][2] = 1
                    if blue_rocket_power >= 1:
                        rp[match_index][3] = 1
                else:
                    rp[match_index][0] = 1 if match["score_breakdown"]["red"]["habDockingRankingPoint"] else 0
                    rp[match_index][1] = 1 if match["score_breakdown"]["red"]["completeRocketRankingPoint"] else 0
                    rp[match_index][2] = 1 if match["score_breakdown"]["blue"]["habDockingRankingPoint"] else 0
                    rp[match_index][3] = 1 if match["score_breakdown"]["blue"]["completeRocketRankingPoint"] else 0
            match_index +=1

        return rp

    def get_team_hab_stats(self):
        np_hab = np.array(self.get_team_specific_data_arrays( "habLineRobot"))
        hab_stats = np.zeros(len(self.team_list))
        np_level = np.array(self.get_team_specific_data_arrays("preMatchLevelRobot"))
        hab_var = np.zeros(len(self.team_list))
        index = 0
        for c in np_hab:
            row = np.array(c)
            level = np.array(np_level[index])
            sandstorm = (row == "CrossedHabLineInSandstorm")

            level[level == "None"] = 0
            level[level == "HabLevel1"] = 3
            level[level == "HabLevel2"] = 6
            level[level == "Unknown"] = 0

            level = level.astype(int)
            level = np.multiply(sandstorm,level)
            if len(row) > 0:
                sandstorm_score = np.sum(level)/len(row)
                var = level.var()
                if var == np.nan:
                    var = 0
            else:
                sandstorm_score = 0
                var = 0

            hab_stats[index] = sandstorm_score
            hab_var[index] = var
            index +=1
        
        return hab_stats, hab_var

    def get_team_climb_stats(self):
        np_climb = np.array(self.get_team_specific_data_arrays( "endgameRobot"))
        climb_stats = np.zeros(len(self.team_list))
        climb_var = np.zeros(len(self.team_list))

        index = 0
        for c in np_climb:
            row = np.array(c)
            row[row == "None"] = 0
            row[row == "HabLevel1"] = 3
            row[row == "HabLevel2"] = 6
            row[row == "HabLevel3"] = 12
            row[row == "Unknown"] = 0
            row = row.astype(int)
            if len(row) > 0:
                hab_score = np.sum(row)/len(row)
                var = row.var()
                if var == np.nan:
                    var = 0
            else:
                hab_score = 0
                var = 0

            climb_stats[index] = hab_score
            climb_var[index] = var
            index +=1

          
        return climb_stats, climb_var
        
    def get_schedule_strength(self):
        schedule = np.zeros((len(self.team_list),3))
        for match in self.matches:
            if match["comp_level"] == "qm":
                for team in match["alliances"]["red"]["team_keys"]:
                    team_index = self.team_list.index(int(team[3:]))    
                    for pair_team in match["alliances"]["red"]["team_keys"]:
                        if pair_team is not team:
                            pair_index = self.team_list.index(int(pair_team[3:]))   
                            schedule[team_index,0] += self.stats[pair_index][6]
                    for pair_team in match["alliances"]["blue"]["team_keys"]:
                            pair_index = self.team_list.index(int(pair_team[3:]))   
                            schedule[team_index,1] += self.stats[pair_index][6]
            
                for team in match["alliances"]["blue"]["team_keys"]:
                    team_index = self.team_list.index(int(team[3:]))
                    for pair_team in match["alliances"]["blue"]["team_keys"]:
                        if pair_team is not team:
                            pair_index = self.team_list.index(int(pair_team[3:]))   
                            schedule[team_index,0] += self.stats[pair_index][6]
                    for pair_team in match["alliances"]["red"]["team_keys"]:
                            pair_index = self.team_list.index(int(pair_team[3:]))   
                            schedule[team_index,1] += self.stats[pair_index][6]

        average_team = np.average(schedule[:,0])
        average_opponent = np.average(schedule[:,1])

        for row in range(len(schedule)):
            schedule[row][0] /= average_team
            schedule[row][1] /= average_opponent
            if not schedule[row][1] == 0:
                schedule[row][2] = schedule[row][0] / schedule[row][1]
            else:
                schedule[row][2] = 1
            #print (self.team_list[row] , schedule[row][0], schedule[row][1], schedule[row][2])
        return schedule



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

    
    def get_team_opr_history(self,team, year):
        event_codes = []
        events, _ =TBA.update_entry("/team/frc{team_num}/events/{year}/simple".format(team_num = team,year = year),event_codes, "")
        pr = np.array([team,0,0,0,0,0,0])
        pr_var = np.array([team,0,0,0,0,0,0])
        most_recent_event = datetime.datetime(year,1,1,0)
        this_event_date = datetime.datetime.strptime(self.event["start_date"], "%Y-%m-%d")
        event_name = ""
        today = datetime.datetime.today()
        for event in events:
            if event["event_type"] != "4":
                today = datetime.datetime.today()
                compare_date = datetime.datetime.strptime(event["end_date"], "%Y-%m-%d")
                if this_event_date > compare_date and compare_date > most_recent_event and today >compare_date:
                    most_recent_event = compare_date 
                    event_name =str(year) + event["event_code"]
        if event_name != "":
            event_data = S3Manager.load_s3_event(event_name)
            index = event_data.get_team_list().index(int(team))
            increase_by = .3571 * float((this_event_date - most_recent_event).days)
            pr = event_data.stats[index]
            event_data.stats[6] += increase_by
            pr_var = event_data.stats[index]
        return pr, pr_var



        
    
    

