import requests
import os
select_url = raw_input("Which Tock API endpoint would you like to access? Type the number that corresponds with your choice:\n 1 = ...projects.json \n 2 = ...timecards_bulk.csv \n 3 = ...users.json \n \n >>>")
print "Gathering data..."
if select_url == "1":
    url = "https://tock.18f.gov/api/projects.json"
    fmt = "json"
elif select_url == "2":
    url = "https://tock.18f.gov/api/timecards_bulk.csv"
    fmt = "csv"
elif select_url == "3":
    url = "https://tock.18f.gov/api/users.json"
    fmt = "json"
else:
    print "Please re-run and make a valid selection!"
    exit(1)
cookies = dict(_oauthproxy=os.environ.get('OAUTHPROXY'))
r = requests.get(url, cookies=cookies)
data = r.content
str_data = str(data)

def writeToFile(str_data={}, fmt=fmt):
    with open("output." + fmt,"w") as fp:
        fp.write(data)
    print ("\nData written to output." + fmt + "!")

writeToFile()
