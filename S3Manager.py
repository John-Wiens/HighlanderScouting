
import boto3
import Events
import pickle

key_file = open('accessKeys.csv','r')
data = key_file.read()
lines = data.split('\n')
parts = lines[1].split(',')
access_key_id= parts[0]
secret_key = parts[1]
session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_key,
)
s3 = session.resource('s3')

def create_s3_event(event_name):
    print("S3 Creating New Event: ", event_name)
    event = Events.Event_2019(event_name)
    event.update()
    write_s3_bucket(event)
    return event

def load_s3_event(event_name):
    if check_key_exists(event_name + ".pickle"):
        aws_object = s3.Object('highlanders-scouting-application-us-west',str(event_name) + '.pickle')
        body = aws_object.get()['Body'].read()
        event = pickle.loads(body)
        return event
    else:
        event = create_s3_event(event_name)
        return event

def write_s3_bucket(event):
    aws_object = s3.Object('highlanders-scouting-application-us-west',str(event.code) + '.pickle')
    aws_object.put(Body=event.serialize())


def check_key_exists(key):
    try:
        s3.Object('highlanders-scouting-application-us-west', key).load()
    except:
        return False
    return True
    