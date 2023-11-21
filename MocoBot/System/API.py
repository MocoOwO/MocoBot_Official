import json
import sqlite3
import requests
import time
from .Init import configLoader


def getAppID() -> int:
    """获取AppId,来自config"""
    return configLoader()["appId"]


def getToken() -> str:
    """获取token，先从本地检查token是否有效，然后如果无效就更新token"""
    temp = sqlite3.connect("./db/temp.db")
    cursor = temp.execute("SELECT TOKEN,  EXPIRE, TIME  from TOKEN ORDER BY TIME DESC LIMIT 1")
    for i in cursor:
        data = i
    if data[1] + data[2] > time.time() + 60:
        return data[0]
    else:
        config = configLoader()
        appId = config['appId']
        appSecret = config['appSecret']
        r = requests.post("https://bots.qq.com/app/getAppAccessToken",
                          headers={'Content-Type': 'application/json'},
                          json={"appId": str(appId), "clientSecret": appSecret}
                          )
        data = json.loads(r.text)
        temp.execute(
            f"INSERT INTO TOKEN (TOKEN,EXPIRE,TIME) VALUES (\"{data['access_token']}\",{data['expires_in']},{time.time() // 1})")
        temp.commit()
        temp.close()
        return data['access_token']


def baseAPI(path: str, data: dict = {}) -> dict:
    """API基类,最好不要直接调用(("""
    BASEURL = "https://api.sgroup.qq.com"
    h = ({"X-Union-Appid": str(getAppID()), "Authorization": f"QQBot {getToken()}"})
    r = requests.post(BASEURL + path, data=data, headers=h)
    return json.loads(r.text)
