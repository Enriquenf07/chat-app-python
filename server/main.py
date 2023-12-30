import asyncio
import json
import websockets
from datetime import datetime
from pydantic import BaseModel

connected = set()


class Message(BaseModel):
    time: str
    user: str
    message: str


class MessageReponse(BaseModel):
    message: str


async def async_input(websocket):
    while True:
        inp = await asyncio.to_thread(input)
        await websocket.send(inp)


async def async_output(websocket):
    while True:
        msg_received = await websocket.recv()
        msg = MessageReponse(**json.loads(msg_received))
        msg_json = {'time': datetime.now().strftime('%X'), 'user': websocket.request_headers["name"], 'message': msg.message}
        msg_final = Message(**msg_json)
        websockets.broadcast(connected, msg_final.model_dump_json())


async def handler(websocket):
    print(websocket.request_headers["name"])
    connected.add(websocket)
    try:
        msg = Message(**{'time': datetime.now().strftime('%X'),
                         'user': 'Server',
                         'message': f"{websocket.request_headers["name"]} joined the chat"})
        websockets.broadcast(connected, msg.model_dump_json())
        await asyncio.gather(
            async_input(websocket),
            async_output(websocket))
    except websockets.ConnectionClosedOK:
        connected.remove(websocket)
        msg = Message(**{'time': datetime.now().strftime('%X'),
                         'user': 'Server',
                         'message': f"{websocket.request_headers["name"]} left the chat"})
        websockets.broadcast(connected, msg.model_dump_json())


async def main():
    async with websockets.serve(handler, "127.0.0.1", 5678):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())