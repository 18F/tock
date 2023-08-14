#!/usr/bin/env python

# Follow the instructions at doc/compliance.md

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
    print(f"Done!")