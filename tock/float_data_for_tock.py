import requests
import os
import json
from datetime import datetime, timedelta

message = '\nResults of operation:'
print(message)
print(len(message) * '=')

"""
Set up API request.
"""
url = 'https://api.floatschedule.com/api/v1/'
headers = {'Authorization': 'Bearer ' + os.environ.get('FLOAT_API_KEY')}

"""
Fetch task data  for prior and next six months.
"""
endpoint = 'tasks'
target_date = datetime.today() - timedelta(weeks=26)
year = target_date.year
month = target_date.month
day = target_date.day
weeks = '52'
request_date = str(year) + '-' + str(month) + '-' + str(day)
payload = {'start_day': request_date, 'weeks': weeks}
r = requests.get(url + endpoint, headers=headers, params=payload)
task_data = json.loads(r.content.decode().lower().strip())
print('\nFetched task items from Float.')

"""
Fetch people data for all users from Float.
"""
endpoint = 'people'
r = requests.get(url + endpoint, headers=headers)
people_data = json.loads(r.content.decode().lower().strip())
print('\nFetched people items from Float.')

"""
Clean people data for all users from Float to remove all but req'd fields.
"""
clean_data = list()
q = len(people_data['people']) - 1
while q >= 0:
    clean_data.append(
        {'im': people_data['people'][q]['im'],
            'people_id': people_data['people'][q]['people_id']
        }
        )
    q -= 1
print('\nCleaned Float people data.')

"""
Pull out relevant elements from task result.
"""
task_list = list()
for people in task_data['people']:
    for tasks in people['tasks']:
        task_list.append(dict(tasks))

for i in task_list:
    i.update({'tock_pk': None, 'im': None})
print('\nCleaned Float task data.')

"""
Fetch Tock Data
"""
r = requests.get('http://192.168.99.100:8000/api/users.json')
output = json.loads(r.content.decode().strip().lower())
print('\nTock data fetched.')

"""
Build crosswalk.
"""
v = len(output['results']) - 1
crosswalk = list()
while v >= 0:
    crosswalk.append(
        {'username': output['results'][v]['username'],
        'pk': output['results'][v]['id']
        }
        )
    v -= 1

a = len(crosswalk) - 1
b = len(clean_data) - 1
while a >= 0:
    while b >= 0:
        tock_record = str(crosswalk[a]['username'])
        float_record = str(clean_data[b]['im'])
        if tock_record[0:12] == float_record[0:12]:
            crosswalk[a].update({
                'people_id': clean_data[b]['people_id'],
                'im': clean_data[b]['im'],
                }
                )
        b -= 1
    a -= 1
    b = len(clean_data) - 1
print('\nFloat / Tock crosswalk built.')

clean_crosswalk = list()
for i in crosswalk:
    if len(i)>3:
        clean_crosswalk.append(i)

x = len(clean_crosswalk)
print('\nFound %s matches between Float "im" values and Tock "username" '
    'values.\nAvailable Tock User pk values will be assigned to Float task '
    'data.') % (x)

"""
Load values from crosswalk.
"""
b = len(clean_crosswalk) - 1
e = len(task_list) - 1
count = 0
while b >= 0:
    while e >= 0:
        if clean_crosswalk[b]['people_id'] == task_list[e]['people_id']:
            task_list[e].update(
                {'tock_pk': clean_crosswalk[b]['pk'], 'im': clean_crosswalk[b]['im']})
            count += 1
        e -=1

    b -= 1
    e = len(task_list) - 1
print('\nMatches from crosswalk loaded into Float task data.')

"""
Write elements to new dictionary that matches Django's loaddata fixture req's.
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

print('\nData updated to include Djano fixture requirements.')

"""
Save output as JSON file in present working directory.
"""
filename = 'task_data_' + datetime.today().strftime('%Y-%m-%d') + '.json'
with open(filename, 'w') as outfile:
   json.dump(fixture, outfile, indent=4)

print('\n' + str(y) + ' objects writen to ' + filename + '.\n')
