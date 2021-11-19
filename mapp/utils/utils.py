import json
import requests
import urllib3


def get_request(url, return_type="json", timeout=10):
    headers = {}
    if return_type:
        headers["Accept"] = "application/" + return_type.lower()

    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        if resp.status_code == requests.codes.ok:
            return json.loads(resp.text)
        else:
            return None
    except urllib3.exceptions.ConnectTimeoutError as e:
        return False
    except Exception as e:
        print(e)
        return None


def get_key(key):
    try:
        return int(key)
    except ValueError:
        return key


def get_elapsed_seconds(start, end):
    elapsed = round(end - start, 2)
    return elapsed
