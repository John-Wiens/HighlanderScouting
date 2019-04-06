import numpy as np
import os
import math




def predict_matches(event_data):
    matches = event_data.matches
    team_list = event_data.get_team_list()

    # Match Number, Red Score, Red Prob, Blue Score, Blue Prob
    predictions = np.zeros((len(event_data.matches),5))
    success = 0
    match_index = 0
    for match in matches:
        level = 0
        if match["comp_level"] =="qm":
            level = 0
        elif match["comp_level"] =="qf":
            level = 1000
        elif match["comp_level"] =="sf":
            level = 2000
        elif match["comp_level"] =="f":
            level = 3000
        
        predictions[match_index][0] = level + int(100 * float( match["set_number"])) + int(float(match["match_number"]))
        if match["score_breakdown"] is None:
            red_average = 0
            red_variance = 0
            for team in match["alliances"]["red"]["team_keys"]:
                    team_index = team_list.index(int(team[3:]))
                    red_average +=event_data.stats[team_index][6]
                    red_variance += event_data.stats_var[team_index][6]
                    team_index +=1
                
            blue_average = 0
            blue_variance = 0
            for team in match["alliances"]["blue"]["team_keys"]:
                    team_index = team_list.index(int(team[3:]))
                    blue_average +=event_data.stats[team_index][6]
                    blue_variance += event_data.stats_var[team_index][6]

            average = red_average - blue_average
            variance = red_variance + blue_variance
            prob_blue_wins = round((1.0 + math.erf(-average /(math.sqrt(variance)* math.sqrt(2.0)))) / 2.0,2)
            if prob_blue_wins > 0.99:
                prob_blue_wins = 0.99
            prob_red_wins = 1 - prob_blue_wins
            predictions[match_index][1] = red_average
            predictions[match_index][2] = prob_red_wins
            predictions[match_index][3] = blue_average
            predictions[match_index][4] = prob_blue_wins
        else:
            red_score = int(float(match["score_breakdown"]["red"]["totalPoints"]))
            blue_score = int(float(match["score_breakdown"]["blue"]["totalPoints"]))
            predictions[match_index][1] = red_score
            predictions[match_index][2] = 1 if red_score >= blue_score else 0
            predictions[match_index][3] = blue_score
            predictions[match_index][4] = 1 if red_score <= blue_score else 0
        match_index +=1
    return predictions



        # set_number
        # comp_level
        # match_number
        


# Creates a N x 1 matrix that lists out the variances for each team for a given statistic
def get_stat_variance(event_data, stat, means):
    matches = event_data.matches
    team_list = event_data.team_list
    num_matches = event_data.get_num_matches()

    quantity_factor = 1/(num_matches - 1)
    
    variances = np.zeros(len(team_list))

    for match in matches:
        if match["comp_level"] == "qm" and match["score_breakdown"] is not None:
            #Fill in the Data for the blue alliance
            actual_score = match["score_breakdown"]["red"][stat]
            predicted_score = 0
            for team in match["alliances"]["red"]["team_keys"]:
                team_index = team_list.index(int(team[3:]))
                predicted_score += means[team_index]

            for team in match["alliances"]["red"]["team_keys"]:
                team_index = team_list.index(int(team[3:]))
                variances[team_index] += ((actual_score - predicted_score)**2) * quantity_factor 

            #Fill in the Data for the Red alliance
            actual_score = match["score_breakdown"]["blue"][stat]
            predicted_score = 0
            for team in match["alliances"]["blue"]["team_keys"]:
                team_index = team_list.index(int(team[3:]))
                predicted_score += means[team_index]

            for team in match["alliances"]["blue"]["team_keys"]:
                team_index = team_list.index(int(team[3:]))
                variances[team_index] += ((actual_score - predicted_score)**2) * quantity_factor

    return variances

# generates a linear matrix and solution set for the given statistic
def create_matrix(event_data, stat, weight):
    matches = event_data.matches
    team_list = event_data.team_list
    num_matches = event_data.get_num_matches()
    
    # Create a matrix that is matches *2 long and #teams wide
    matrix = np.zeros((num_matches * 2,len(team_list)))
    solutions = np.zeros(num_matches *2)
    #try:
    # Iterate through all matches and build the matricies
    for match in matches:
        if match["comp_level"] == "qm" and match["score_breakdown"] is not None:
            index = (match["match_number"] * 2) -1
            
            #Fill in the Data for the blue alliance
            solutions[index] += match["score_breakdown"]["red"][stat] * weight
            for team in match["alliances"]["red"]["team_keys"]:
                team_index = team_list.index(int(team[3:]))
                matrix[index][team_index] = 1

            index -=1

            #Fill in the Data for the Red alliance
            solutions[index] += match["score_breakdown"]["blue"][stat] * weight
            for team in match["alliances"]["blue"]["team_keys"]:
                team_index = team_list.index(int(team[3:]))
                matrix[index][team_index] = 1

    #Zero Data for teams that cannot actually score a given factor
    if os.path.isfile("tournaments/data_" + event_data.code+"/no_"+stat + ".csv"):
        if os.path.getsize("tournaments/data_" + event_data.code+"/no_"+stat + ".csv") >0:
            zeros = np.loadtxt("tournaments/data_" + event_data.code+"/no_"+stat + ".csv",skiprows = 0)
            if zeros.size > 1:
                for element in zeros:
                    matrix[:,team_list.index(int(element))] = 0


    return matrix, solutions

# Solves the matrix as effectively as possible 
def solve_matrix(matrix, solution):
    return np.linalg.lstsq(matrix,solution,rcond=None)[0]

# Generates a stat list for any given match statistic
def generate_ols_stat_list(event_data,stat,weight):
    matrix, solution = create_matrix(event_data,stat,weight)
    solution = solve_matrix(matrix,solution)

    # Sanitize Data
    for row in range(len(solution)):
        if abs(solution[row]) > 1000:
            solution[row] = 0
        if solution[row] < 0:
            solution[row] = 0
    return solution


#index[x][y] of an array becomes index [y][x] and the matrix is resized accordingly
def flip_array(array):
    matrix = np.zeros((len(array[0]), len(array)))
    for i in range(0,len(array)):
        for j in range(0,len(array[0])):
            matrix[j][i] = array[i][j]

    return matrix

#Gets the List of Score standard Deviations
def get_sd_list(event_data):
    team_list = event_data.team_list
    matches = event_data.matches
    num_matches = event_data.get_num_matches()
    rankings = event_data.rankings

    scores = np.empty(len(team_list),dtype = object)
    for i in range (len(scores)):
        scores[i] = []
    count = 0
    for match in matches:
        if match["comp_level"] == "qm":
            for team in match["alliances"]["red"]["teams"]:
                team_index = team_list.index(int(team[3:]))
                scores[team_index].append(match["score_breakdown"]["red"]["totalPoints"])
            for team in match["alliances"]["blue"]["teams"]:
                team_index = team_list.index(int(team[3:]))
                scores[team_index].append( match["score_breakdown"]["blue"]["totalPoints"])


    sd = np.zeros(len(team_list))
    for i in range(0,len(team_list)):
        sd[i] = np.std(scores[i],dtype=np.float64) / np.average(scores[i])

    return sd
def sort_data(data,index):
    data = (data[np.argsort(data[:, index])])[::-1]
    return data

#Calculates the strength of a teams schedule based upon how well their alliance partners did
def generate_schedule_power(event_data,data):
    team_list = event_data.team_list
    schedule = np.zeros((len(team_list),3))
    sorted_teams = data[:,0]
    for match in event_data.matches:
        if match["comp_level"] == "qm" and match["score_breakdown"] is not None:
            for team in match["alliances"]["red"]["teams"]:
                team_index = team_list.index(int(team[3:]))    
                for pair_team in match["alliances"]["red"]["teams"]:
                    if pair_team is not team:
                        schedule[team_index,0] += data[np.where(sorted_teams == int(pair_team[3:]))][0][6]
                for pair_team in match["alliances"]["blue"]["teams"]:
                        schedule[team_index,1] += (data[np.where(sorted_teams == int(pair_team[3:]))][0][6])
            
            for team in match["alliances"]["blue"]["teams"]:
                team_index = team_list.index(int(team[3:]))
                for pair_team in match["alliances"]["blue"]["teams"]:
                    if pair_team is not team:
                        schedule[team_index,0] += (data[np.where(sorted_teams == int(pair_team[3:]))][0][6])
                for pair_team in match["alliances"]["red"]["teams"]:
                        schedule[team_index,1] += (data[np.where(sorted_teams == int(pair_team[3:]))][0][6])

    average_team = np.average(schedule[:,0])
    average_opponent = np.average(schedule[:,1])

    for row in range(len(schedule)):
        schedule[row][0] /= average_team
        schedule[row][1] /= average_opponent
        if not schedule[row][1] == 0:
            schedule[row][2] = schedule[row][0] / schedule[row][1]
        else:
            schedule[row][2] = 1
        #print (team_list[row] , schedule[row][0], schedule[row][1], schedule[row][2])
    return schedule

def generate_win_loss_power(event_data,data):
    team_list = event_data.team_list
    schedule = np.zeros(len(team_list))
    sorted_teams = data[:,0]
    for match in event_data.matches:
        if match["comp_level"] == "qm" and match["score_breakdown"] is not None:
            red_power = 0
            blue_power = 0
            for pair_team in match["alliances"]["red"]["teams"]:
                    red_power += data[np.where(sorted_teams == int(pair_team[3:]))][0][6]
            for pair_team in match["alliances"]["blue"]["teams"]:
                    blue_power += data[np.where(sorted_teams == int(pair_team[3:]))][0][6]

            delta_power = red_power - blue_power

            for pair_team in match["alliances"]["red"]["teams"]:
                    schedule[team_list.index(int(pair_team[3:]))] += delta_power / abs(delta_power)
            for pair_team in match["alliances"]["blue"]["teams"]:
                    schedule[team_list.index(int(pair_team[3:]))] -= delta_power / abs(delta_power)
            

def adjust_data_for_schedule(event_data,data):
    scheudle = generate_schedule_power(event_data,data)
    for row in range(len(data)):
            if schedule_power[row][2] > 1:
                data[row][6] *=  1 - (schedule_power[row][2]-1)
            else:
                data[row][6] *= (2-schedule_power[row][2])

def get_rank_data(event_data):
    team_list = event_data.team_list
    ranks = np.zeros(len(team_list))
    low_rank = 1
    high_rank = 24
    alliances = event_data.events["alliances"]
    for i in range(len(ranks)):
        ranks[i] = len(ranks) +1
    
    #load the top 24 based on the order they were picked
    for alliance in alliances:
        ranks[team_list.index(int(alliance["picks"][0][3:]))] = low_rank
        low_rank +=1
        ranks[team_list.index(int(alliance["picks"][1][3:]))] = low_rank
        low_rank +=1
        ranks[team_list.index(int(alliance["picks"][2][3:]))] = high_rank
        high_rank -= 1

    rankings = event_data.rankings
    index = 25
    length = len(ranks) +1
    for i in range(1,len(rankings)):
        if ranks[i-1] == length:
            ranks[i-1] = index
            index +=1
    return ranks














