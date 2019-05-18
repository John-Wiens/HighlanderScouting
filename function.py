
import TBA
import datetime
import S3Manager
import Events
import json
import numpy as np
import os
import math
import pickle
import requests
import Processing
import time
from Events import Event_2019

def process_events():
    start_time = time.time()
    r = TBA.make_tba_request("/events/{year}".format(year = 2019),"")
    today = datetime.datetime.today()
    for row in r.json():
        try:
            event_name = row["key"]
            if S3Manager.check_key_exists(event_name+".pickle"):
                event_end_date = datetime.datetime.strptime(row["end_date"], "%Y-%m-%d")
                event_start_date = datetime.datetime.strptime(row["start_date"], "%Y-%m-%d")
                if event_end_date >= today or True:
                    print("Event Period Update: ", event_name)
                    event = S3Manager.load_s3_event(event_name)
                    event.update()
                else:
                    print("Event has already Finished: ",event)
            else:
                print("Creating Missing Event: ", event_name)
                S3Manager.create_s3_event(event_name)
        except:
            print("Failed Event Update: " + str(event_name))
            pass
    print("Update Complete in: ", time.time() - start_time)

def lambda_handler(event, context):
    # TODO implement
    process_events()
    return {
        'statusCode': 200,
        'body': json.dumps("Event Processing Complete")
    }
