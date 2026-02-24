
import asyncio, json
import websockets

async def test():
    async with websockets.connect('ws://localhost:8000/ws/events') as ws:
        while True:
            raw = await ws.recv()
            d = json.loads(raw)
            if d['type'] == 'new_alarm':
                print('GOT ALARM:', d)
                break

asyncio.run(test())

