
import json

def save_json(data, file_name):

    with open(file_name,"w") as f:

        json.dump(data, f, indent=4)