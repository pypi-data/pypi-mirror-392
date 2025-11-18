import requests

def getir(url, username, password, otvet, login):
    data = {"username": "example", "password": "example"}
    data["password"] = password
    data["username"] = username
    session = requests.Session()
    resp = session.get(url, data=data)
    if otvet in resp.text:
        print(login)
        return resp.text