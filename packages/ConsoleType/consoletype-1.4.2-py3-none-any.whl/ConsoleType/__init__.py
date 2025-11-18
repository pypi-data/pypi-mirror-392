import os
import time
import .getit
import requests

def prints(text, times, size, title):
    sizes = 0
    ot = "-"
    tt = "-" * size
    while not sizes == size:
        os.system("cls")
        print(f"{ot}{text}{tt}")
        time.sleep(times)
        tt = tt[:-1]
        ot = ot + "-"
        sizes += 1

    print(title)
    #print("Create in prints")

def outputs(text, times):
    print(f"gf")

def title(title):
    print(title)

def idlogin(homeurl, error, name, otvet):
    print(f"IDLogin {name}")
    data = {"username": "example", "password": "example"}
    data["username"] = input("Имя Пользователя: ")
    data["password"] = input("Пароль: ")
    session = requests.Session()
    resp = session.get(homeurl, data=data)
    if otvet in resp.text:
        print("Вход выполнен IDLogin")
        IDLogin = resp.text[4:]
        return IDLogin
    else:
        print(error)

def login():
    print("IDLogin")

def cval(one, two, onez, twoz):
    one = eval(f"{one}{onez}{two}")
    one = eval(f"{one}{twoz}{two}")
    return one

def spatext(text):
    texts = " ".join(original_string)
    text = texts
    return texts

def set(size,simvol):
    simvol = simvol * size
    return simvol

def get(url, username,password, otvet, login):
    text = getit.getir(url, username, password, otvet, login)
    return text