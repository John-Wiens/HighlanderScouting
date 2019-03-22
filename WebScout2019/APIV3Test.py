api_url = 'www.thebluealliance.com/api/v3'
c = http.client.HTTPSConnection(api_url)

header = "X-TBA-App-Id"
app = "4499:scouting:1"

def request_event_key_list(year,*params, **keywords):
    print("Test")
    c.request("GET", "/events/{year}/keys".format(year = year),header)
    response = c.getresponse()
    print(response.info())
    '''
    data = response.read()
    jsonData = json.loads(data)
    keys = []
    for event in jsonData:
    	print(event)
    	keys.append(event["key"])
    '''
    return False

if __name__ == '__main__':
    request_event_key_list(2019)
    pass