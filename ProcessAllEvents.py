
import TBA
import datetime
import S3Manager
import Events
import json


def process_events():
    r = TBA.make_tba_request("/events/{year}".format(year = 2019),"")
    today = datetime.datetime.today()
    for row in r.json():
        try:
            event_name = "2019"+row["first_event_code"].lower()
            if S3Manager.check_key_exists(event_name+".pickle"):
                event_end_date = datetime.datetime.strptime(row["end_date"], "%Y-%m-%d")
                if event_end_date > today:
                    print("Updating S3")
                    event = S3Manager.load_s3_event(event_name)
                    event.update()
                    S3Manager.write_s3_bucket(event)
            else:
            	print("File Doesn't exist on S3")
            	event = Events.Event_2019(event_name)
            	event.update()
            	S3Manager.write_s3_bucket(event)
        except:
            pass


def lambda_handler(event, context):
    # TODO implement
    process_events()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

if __name__ == "__main__":
    process_events()
    event = S3Manager.load_s3_event('2019new')
    event.update()
    S3Manager.write_s3_bucket(event)