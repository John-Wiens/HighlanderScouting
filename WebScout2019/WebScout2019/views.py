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
import TBA


#2019code 2019okok
#event_name = "2019casf" 
#event_name = "2019azpx"
#event_name = "2019nyny"
#event_name = "2019code"


def load_event(event_name):
    event_data = None
    path = "Data/"
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
    return event_data

@app.route('/')
@app.route('/home')
def home():
    try:
        """Renders the home page."""
        return render_template(
            'index.html',
            title='Home Page',
            year=datetime.now().year,
        )
    except:
        pass



@app.route('/2019')
@app.route('/2019/<event_code>/teams',methods = ['POST', 'GET'])
def teams(event_code):
    try:
        event_data = load_event(event_code)
        """Renders the contact page."""
        if request.method == 'POST':
            print(request.form)
            team = request.form['team']

            index = event_data.get_team_list().index(int(team))
            print(round(event_data.schedule_strength[index][2],2),round(event_data.predictions_final[index][1],2))
            return render_template(
            'teams.html',
            team_list=event_data.get_team_list(),
            selected_team = request.form['team'],
            opr = round(event_data.stats[index][1],2),
            cargo = round(event_data.stats[index][3],2),
            hatches = round(event_data.stats[index][2],2),
            climb = round(event_data.stats[index][4],2),
            pr = round(event_data.stats[index][6],2),
            hab = round(event_data.stats[index][5],2),
            sstrength = round(event_data.schedule_strength[index][2],2),
            pranking = round(event_data.predictions_final[index][1],2)
            )
        return render_template(
            'teams.html',
            team_list=event_data.get_team_list(),selected_team = 'robot')
    except:
        pass

@app.route('/2019')
@app.route('/2019/<event_code>/rankings')
def rankings(event_code):
    try:
        """Renders the about page."""
        event_data = load_event(event_code)
        return render_template(
            'rankings.html',
            stats=np.around(event_data.stats, decimals=2),
            title='Events',
            year=datetime.now().year,
            message='Your application description page.'
        )
    except:
        pass



@app.route('/2019')
@app.route('/2019/<event_code>/predictions')
def predictions(event_code):
    try:
         event_data = load_event(event_code)
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
            current_match = event_data.get_highest_qual_match_played(),
            title='Predictions',
            year=datetime.now().year,
        )
    except:
        pass

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    try:
        events = TBA.get_year_events(2019)
        print(events)
        return render_template(
            'events.html',
            title='Event',
            event_list = events,
            year=datetime.now().year,
        )
    except:
        pass


@app.route('/about')
def about():
    try:
        return render_template(
            'about.html',
            title='About',
            year=datetime.now().year,
        )
    except:
        pass
