import json
import websocket

import requests


def testWebToken(appId: int, clientSecret: str) -> bool:
    """用来测试appSecret,但是下面那个全都会用到"""
    r = requests.post("https://bots.qq.com/app/getAppAccessToken",
                      headers={'Content-Type': 'application/json'},
                      json={"appId": str(appId), "clientSecret": clientSecret}
                      )
    data = json.loads(r.text)
    # print(data)
    if "code" in data:
        return False
    else:
        return True


def testWSToken(appId: int, clientSecret: str,) -> bool:
    """测试全场景的认证"""
    if testWebToken(appId, clientSecret):
        r = requests.post("https://bots.qq.com/app/getAppAccessToken",
                          headers={'Content-Type': 'application/json'},
                          json={"appId": str(appId), "clientSecret": clientSecret}
                          )
        data = json.loads(r.text)
        access_token = data['access_token']
        token = f"QQBot {access_token}"
        h = {
            "Authorization": token,
            "X-Union-Appid": f"{appId}"
        }
        r = requests.get("https://api.sgroup.qq.com/gateway", headers=h)

        try:
            url = json.loads(r.text)['url']
        except:
            return False
        ws = websocket.WebSocket()
        ws.connect(url)
        ws.recv()
        data = {
            "op": 2,
            "d": {
                "token": token,
                "intents": 1,
                "shard": [0, 1],
                "properties": {
                    "$os": "Windows",
                    "$browser": "MocoBot",
                    "$device": "MocoBot"
                }
            }
        }
        ws.send(json.dumps(data))
        msg = json.loads(ws.recv())
        if msg["op"] == 0:
            return True
        else:
            return False
    else:
        return False


def testAll(appId: int, clientSecret: str):
    """测试全场景，事实上WS已经测试过了"""
    return testWSToken(appId, clientSecret)
