import json

def json_to_string(value):
    return json.dumps(
        value, 
        indent=4, 
        sort_keys=True, 
        default=str
    ).encode("utf-8")
