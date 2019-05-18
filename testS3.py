import boto3
import pickle

# Iterates through all the objects, doing the pagination for you. Each obj
# is an ObjectSummary, so it doesn't contain the body. You'll need to call
# get to get the whole body.
key_file = open('accessKeys.csv','r')
data = key_file.read()
lines = data.split('\n')
parts = lines[1].split(',')
access_key_id= parts[0]
secret_key = parts[1]

print(access_key_id,secret_key)

session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_key,
)

s3 = session.resource('s3')


def load_s3_event(event_name):
    print("Loading Event: " + str(event_name))
    aws_object = s3.Object('highlanders-scouting-application-us-west',str(event_name) + '.pickle')
    body = aws_object.get()['Body'].read()
    print(type(body))
    event = pickle.loads(body)
    print(event)
    return event
load_s3_event('2019none')



