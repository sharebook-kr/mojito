import asyncio
from re import sub 
import websockets
import json

with open("./koreainvestment.key") as f:
    lines = f.readlines()

api_key = lines[0].strip()
api_secret = lines[1].strip()


async def ws_client():
    uri = "ws://ops.koreainvestment.com:21000"

    async with websockets.connect(uri, ping_interval=None) as websocket:
        #data = await websocket.recv()
        #print(data)

        header = {
           "appKey": api_key,
           "appSecret": api_secret, 
           "custtype": "P",
           "tr_type": "1",
           "content": "utf-8"
        }
        body = {
            "tr_id": "H0STCNT0",
            "tr_key": "005930" 
        }
        fmt = {
            "header": header, 
            "body": {
                "input": body
            } 
        }

        subscribe_data = json.dumps(fmt)
        await websocket.send(subscribe_data)

        while True:
            data = await websocket.recv()
            print(data)


async def main():
    await ws_client()

asyncio.run(main()) 
 