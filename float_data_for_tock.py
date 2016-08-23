import requests
import os
import json
from datetime import datetime, timedelta

print('Working...')

"""
Fetch data for prior and next six months from Float.
"""
api_key = os.environ.get('FLOAT_API_KEY')
headers = {'Authorization': 'Bearer ' + api_key}
endpoint = 'tasks'
target_date = datetime.today() - timedelta(weeks=26)
year = target_date.year
month = target_date.month
day = target_date.day
weeks = '52'
request_date = str(year) + '-' + str(month) + '-' + str(day)
payload = {'start_day': request_date, 'weeks': weeks}
url = 'https://api.floatschedule.com/api/v1/' + endpoint
r = requests.get(url, headers=headers, params=payload)
task_data = json.loads(r.content)

"""
Pull out relevant elements from request result.
"""
task_list = list()
for people in task_data['people']:
    for tasks in people['tasks']:
        task_list.append(tasks)

"""
Write elements to new dictionary.
"""
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

"""
Save output as JSON file in present working directory.
"""
filename = 'task_data_' + datetime.today().strftime('%Y-%m-%d') + '.json'
with open(filename, 'w') as outfile:
   json.dump(fixture, outfile, indent=4)

print(str(y) + ' objects writen to ' + filename + '.\n')
