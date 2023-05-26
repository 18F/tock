# Compliance

As part of our compliance duties, we are required to periodically deactivate user accounts for Tock for individuals who have left TTS. (These users will not be able to log in Tock anyway, since GSA SecureAuth would prevent them doing so, but it is still good practice to disable these Tock accounts.)

These list of users are given to us in CSV format. Here is a sample script to call the Tock API and compare against the given list (note: some minor adjustments may be necessary):

```python
#!/usr/bin/env python

import csv
import sys
import requests

# token.txt should have API key in it and nothing else
token_data = open("token.txt", "r").readlines()
token = "".join(token_data).strip()

url = "https://tock.18f.gov/api"
headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
resp = requests.get(f"{url}/users.json", headers=headers)

emails = {person["email"] for person in resp.json()}

filename = sys.argv[1]
with open(filename, "r") as fd:
    cr = csv.reader(fd)
    header = next(cr)
    index = 2 if header[0] == "SF50 Effective Date" else 3
    for line in cr:
        email = line[index].strip()
        # some emails are gsa.govxxx where x is variable
        first = email.split("@")[0]
        email = first + "@gsa.gov"
        if email in emails:
            print(f"{email} needs to be de-activated")
```

To use:

- Add your API key in `token.txt`
- Download separations report as CSVs
  - Note: there are two: one for GSA employees, one for contractors
- Run script
  - Example: `./manage.py Jan_2023_Separations_Report.csv`

Each user that is printed out will need to have their account set as `active=False` in the Tock admin. (Please do not delete their account; marking them as inactive is sufficient.)
