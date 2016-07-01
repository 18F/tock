import requests
import os
import json

api_key = os.environ.get('FLOAT_API_KEY')
headers = {'Authorization': 'Bearer ' + api_key}
endpoint = 'tasks'
year = "2016"
month = "04"
day = "01"
weeks = "52"
timecard_date = str(year + "-" + month + "-" + day)
payload = {'start_day': timecard_date, 'weeks': weeks}
url = 'https://api.floatschedule.com/api/v1/' + endpoint
r = requests.get(url, headers=headers, params=payload)
output = r.content

print "\nData successfully pulled from Float API. \n"

fmt = 'json'
def writeToFile(x, str_data={}, fmt=fmt):
    with open("output." + fmt,"w") as fp:
        fp.write(x)

writeToFile(output)

print "Data written to temporary file.\n"

with open('output.json') as data_file:
    data = json.load(data_file)

print "Data retrieved from temporary file.\n"

task_list = list()
for people in data['people']:
    for tasks in people['tasks']:
        task_list.append(tasks)

fixture = list()
for item in task_list:
    fixture.append(dict())

y = len(task_list)
x = y - 1
while x >= 0:
    fixture[x]["pk"] = x
    fixture[x]["model"] = "float.floattasks"
    fixture[x]["fields"] = task_list[x]
    x = x - 1

with open('json_task_data.json', 'w') as outfile:
   json.dump(fixture, outfile, indent=4)

print str(y) + " objects writen to ../tock/float/fixtures/json_task_data.json.\n"

os.rename("json_task_data.json", "/Users/patrickbateman/tock/tock/float/fixtures/json_task_data.json")

os.remove('output.json')

print "Temporary file removed.\n"
