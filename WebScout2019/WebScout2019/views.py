"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request
from WebScout2019 import app
import os
import pickle
import urllib.request
import re
import Events
import numpy as np
import Processing as proc


path = "Data/"

#2019code 2019okok
#event_name = "2019casf" 
event_name = "2019azpx"

if os.path.isfile(path + event_name + ".pickle"):
    print("Found Local Data File for: {}".format(event_name))
    event_file = open(path + event_name+".pickle","rb")
    event_data = pickle.load(event_file)
    event_data.update()
    event_file.close()
else:
    print("Querying Data for: {}".format(event_name))
    print("Loading event_data from TBA")
    event_data = Events.Event_2019(event_name)

event_data.save(path + event_name)
teams = event_data.get_team_list()


print("\n\nEvent Data Schedule Strengths")
event_data.get_schedule_strength()




@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/teams',methods = ['POST', 'GET'])
def teams():
    """Renders the contact page."""
    if request.method == 'POST':
        print(request.form)
        team = request.form['team']



        index = event_data.get_team_list().index(int(team))
        return render_template(
        'teams.html',
        team_list=event_data.get_team_list(),
        selected_team = request.form['team'],
        opr = round(event_data.stats[index][1],2),
        cargo = round(event_data.stats[index][3],2),
        hatches = round(event_data.stats[index][2],2),
        climb = round(event_data.stats[index][4],2),
        pr = round(event_data.stats[index][6],2),
        hab = round(event_data.stats[index][5],2))


        

    return render_template(
        'teams.html',
        team_list=event_data.get_team_list(),selected_team = 'robot')

@app.route('/Rankings')
def rankings():
    """Renders the about page."""
    return render_template(
        'rankings.html',
        stats=np.around(event_data.stats, decimals=2),
        title='Events',
        year=datetime.now().year,
        message='Your application description page.'
    )



@app.route('/Predictions')
def predictions():
     return render_template(
        'predictions.html',
        #predictions=np.around(event_data.predictions, decimals=2),
        predictions = np.around(proc.flip_array(np.array([
                                event_data.predictions[:,0],
                                event_data.predictions[:,1],
                                event_data.predictions[:,2],
                                event_data.predictions_rp[:,0],
                                event_data.predictions_rp[:,1],
                                event_data.predictions[:,3],
                                event_data.predictions[:,4],
                                event_data.predictions_rp[:,2],
                                event_data.predictions_rp[:,3]])),decimals=2),
        final_predictions = np.around(event_data.predictions_final,decimals=2),
        title='Predictions',
        year=datetime.now().year,
    )




@app.route('/about')
def about():
     return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
    )
