import requests
import os
select_url = raw_input("Which Tock API endpoint would you like to access? Type the number that corresponds with your choice:\n 1 = ...projects.json \n 2 = ...timecards_bulk.csv \n 3 = ...users.json \n \n >>>")
if select_url == "1":
    url = "https://tock.18f.gov/api/projects.json"
    print "Gathering data..."
elif select_url == "2":
    url = "https://tock.18f.gov/api/timecards_bulk.csv"
    print "Gathering data..."
elif select_url == "3":
    url = "https://tock.18f.gov/api/users.json"
    print "Gathering data..."
else:
    print "Please re-run and make a valid selection!"
    exit(1)
cookies = dict(_oauthproxy=os.environ.get('OAUTHPROXY'))
r = requests.get(url, cookies=cookies)
data = r.content
if select_url == "1":
    target = open("output.json",'w')
    target.truncate()
    target.write(data)
    print "\nData written to output.json!"
elif select_url == "2":
    target = open("output.csv",'w')
    target.truncate()
    target.write(data)
    print "\nData written to output.csv!"
elif select_url == "1":
    target = open("output.json",'w')
    target.truncate()
    target.write(data)
    print "\nData written to output.json!"
