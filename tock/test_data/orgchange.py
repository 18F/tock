import pdb
import json

def main():
    with open("data-update-deduped.json") as f:
        raw = f.read()
    entries = json.loads(raw)
    for entry in entries:
        if entry["model"] == "employees.userdata":
            if entry["fields"]["organization"] == None:
                entry["fields"]["organization"] = 1
    output = json.dumps(entries)
    with open("data-update-deduped-changeorg.json","w+") as f:
        f.write(output)


if __name__ == "__main__":
#    pdb.set_trace()
    main()
     
  
