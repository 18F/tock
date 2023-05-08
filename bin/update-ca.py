#!/usr/bin/env python
#
# Add the cloud.gov CA certificate for egress traffic control.
# See docs/egress.md for details.
import requests
import certifi

url = "https://uaa.fr.cloud.gov"
try:
    resp = requests.get(url)
    print("update-ca: nothing to do")
except requests.exceptions.SSLError as err:
    print(err, "update-ca: cloud.gov ca certificate needs to be added to certifi")
    try:
        customca = open("/etc/cf-system-certificates/trusted-ca-1.crt", "rb").read()
        cafile = certifi.where()
        with open(cafile, "ab") as outfile:
            outfile.write(b"\n")
            outfile.write(customca)
    except FileNotFoundError as e:
        print(f"update-ca: error updating: {e}")
    requests.get(url)  # throw an exception if we still cannot access UAA
    print(f"update-ca: success")
