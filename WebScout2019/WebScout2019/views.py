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
import Data


path = "Data/"
event_name = "2019okok" #2019code
if os.path.isfile(path + event_name + ".pickle"):
    event_file = open(path + event_name+".pickle","rb")
    event_data = pickle.load(event_file)
    event_file.close()
else:
    print("Loading event_data from TBA")
    event_data = Data.Event_Data(event_name)

event_data.generate_export_data()
teams = event_data.get_team_list()



@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        option_list=['a','b','c']
    )

@app.route('/teams',methods = ['POST', 'GET'])
def teams():
    """Renders the contact page."""
    if request.method == 'POST':
        print(request.form)
        team = request.form['team']
        
        index = event_data.get_team_list().index(int(team))
        #picture_path = "WebScout2019/static/pictures/teampictures"
        #if not(os.path.isfile("{path}/{team}.jpg".format(path=picture_path,team=team))):
        #    response = urllib.request.urlopen("https://www.thebluealliance.com/team/{team}".format(team=team))
        #    output = response.read()
        #    print(output)
        #    urllib.request.urlretrieve("https://i.imgur.com/IiNmPeHh.jpg", "{path}/{team}.jpg".format(path=picture_path,team=team))
        return render_template(
        'teams.html',
        team_list=event_data.get_team_list(),
        selected_team = request.form['team'],
        opr = round(event_data.team_data[index].OPR,2),
        cargo = round(event_data.team_data[index].cargo,2),
        hatches = round(event_data.team_data[index].hatches,2),
        climb = round(event_data.team_data[index].climb,2),
        pr = round(event_data.team_data[index].pr,2),
        hab = round(event_data.team_data[index].hab,2))


        

    return render_template(
        'teams.html',
        team_list=event_data.get_team_list(),selected_team = 'robot')

@app.route('/events')
def events():
    """Renders the about page."""
    return render_template(
        'events.html',
        title='Events',
        year=datetime.now().year,
        message='Your application description page.'
    )

