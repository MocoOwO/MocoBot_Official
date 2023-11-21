import json
import time

import requests
import sqlite3
import os


def init():
    """初始化Bot的方法"""

    config = configLoader()
    appId = config['appId']
    token = config['token']
    appSecret = config['appSecret']
    databaseLoader()
    getToken(appId, appSecret)


def configLoader() -> dict:
    """配置读取函数"""

    try:
        f = open("config.json")
    except FileNotFoundError:

        print("没找到配置文件!")
        f = open("config.json", mode="w")
        f.write(json.dumps({"appId": 0, "token": "", "appSecret": ""}))
        f.close()
        input("已经生成配置文件，按回车退出程序")
        exit(1)

    try:
        data = json.load(f)
        appId = data['appId']
        token = data['token']
        appSecret = data['appSecret']
    except:
        s = input("配置文件出现错误,是否重新生成？(y/N):")
        if s == "y" or s == "Y":
            f = open("config.json", mode="w")
            f.write(json.dumps({"appId": 0, "token": "", "appSecret": ""}))
            f.close()
        exit(1)
    return data


def databaseLoader() -> None:
    """初始化数据库(系统数据库)"""
    folder = os.path.exists("db")
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("db")  # makedirs 创建文件时如果路径不存在会创建这个路径
    # todo: 完善总表
    db = sqlite3.connect("./db/main.db")
    temp = sqlite3.connect("./db/temp.db")
    db.close()
    temp.close()


def getToken(appId: int, clientSecret: str) -> None:
    r = requests.post("https://bots.qq.com/app/getAppAccessToken",
                      headers={'Content-Type': 'application/json'},
                      json={"appId": str(appId), "clientSecret": clientSecret}
                      )
    data = json.loads(r.text)
    # print(data)
    if "code" in data:
        print(f"获取AccessToken错误:{data['message']}")
        input("请检查配置中的appId和appSecret是否正确，按回车退出程序")
        exit(1)
    else:
        temp = sqlite3.connect("./db/temp.db")
        temp.execute("""
            CREATE TABLE IF NOT EXISTS TOKEN (
                TOKEN TEXT,
                EXPIRE INT,
                TIME INT
            );""")
        temp.execute(
            f"INSERT INTO TOKEN (TOKEN,EXPIRE,TIME) VALUES (\"{data['access_token']}\",{data['expires_in']},{time.time() // 1})")
        temp.commit()
        temp.close()
