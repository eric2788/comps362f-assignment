import json


# a function that catch the json decode error so that to
# not causing internal server error while invalid json format
def json_load(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        print(f'Errror while decoding json: {e}')
        return None