import requests

base_url = "http://pratiklondhe4.pythonanywhere.com"


def get_severity(desc):
    req = base_url+"/predict"
    data = {
        "bug_description": desc,
        "model_choice": "nb"}
    r = requests.post(url=req, json=data)
    print(r)
    # Remove quotes from the response text
    return r.text.strip('"').rstrip('"')[0:-2]
