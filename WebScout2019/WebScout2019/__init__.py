"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
import WebScout2019.views

import Data
import logging
import time
import pickle
import json
import os
#date = (time.asctime(time.localtime()).replace(" ","_")).replace(":","-")
#logging.basicConfig(filename = "Log_{date}.log".format(date=date, level=logging.DEBUG))
#logging.info("Application Startup Complete")



if __name__ == "__main__":
    print("Welcome to the Highlanders Scouting Application")


    '''path = "Data/"
    
    if os.path.isfile(path + "season_data.pickle"):
        event_file = open(path + "season_data.pickle","rb")
        event = event = pickle.load(event_file)
        event_file.close()
    else:
        print("Loading Events from TBA")
        event = Data.Data()
        event.get_year_events(2019)
        event.save(path + "season_data")
    

    if os.path.isfile(path + "2019okok.pickle"):
        event_file = open(path + "2019okok.pickle","rb")
        orange = pickle.load(event_file)
        event_file.close()
    else:
        print("Loading Orange from TBA")
        import Data
        orange = Data.Event_Data("2019okok")



    #print(orange.teams)

    #print(event.events)

    #for row in event.events:
    #    print(row["city"],row["state_prov"],row["key"],row["week"])

    orange.generate_export_data()

    #event.save(path + "season_data")    
    orange.save(path + "2019okok")
    '''




