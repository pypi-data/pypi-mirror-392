import requests

def checknet(host="https://www.google.com"):
    try:
        response = requests.get(host, timeout=10)
        if response.status_code == 200:
            return "You have internet.", True
        else:
            return "You don't have internet.", False
    except:
        return "You don't have internet.", False
