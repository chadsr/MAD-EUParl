from flask import json
from collections import defaultdict

def load_json(path):
    try:
        f = open(path, 'r')
        print ('Loading file:', path)
        try:
            json_data = json.load(f)
        except ValueError, error:
            print error
            print
            return None
        f.close()
        print
        return json_data
    except IOError, error:
        print error
        print
        return None

# TODO: There is probably a better way to get from json to a defaultdict, but this works..
def json_to_defaultdict(json_str):
    def_dict = defaultdict(list)

    for key in json_str:
        for element in json_str[key]:
            def_dict[str(key)].append(element)

    return def_dict
