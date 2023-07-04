import json
import logging
import atexit

from websocket_server import WebsocketServer
from threading import Thread

from BlendController import BlendController

ADDR = "0.0.0.0"
PORT = 8765

blend_controller = BlendController()


def blend_status_callback(waiting_time, server, client):
    server.send_message(client, json.dumps({'type': 'status', 'data': {'waiting_time': waiting_time}}))


"""async def threat_msg(websocket):
    for message in websocket:
        print(f"Recv : {message}")
        asyncio.create_task(parse_msg(message, websocket))
        print(2)"""


"""async def main():
    print(f"Listening on {ADDR}:{PORT}")
    async with serve(threat_msg, ADDR, PORT):
        await asyncio.Future()  # run forever"""


def new_client(client, server):
    print("hi !")
    print(client)


def thread_threat_message(client, server, message):
    t = Thread(target=threat_message, args=[client, server, message])
    t.start()


def threat_message(client, server, message):
    print(message)
    packet = json.loads(message)
    if packet['type'] == 'echo':
        print(f"Recv message : {packet['data']}")

        server.send_message(client, json.dumps(packet))
    elif packet['type'] == 'blend':
        print(f"Recv blend : {packet['data']}")

        def callback(waiting_time):
            blend_status_callback(waiting_time, server, client)

        res = blend_controller.blend(packet['data'], callback)
        if not res:
            server.send_message(client, json.dumps({'type': 'error', 'data': {'msg': f'Already blending ! Retry in {blend_controller.waiting_time} sec'}}))


def main2():
    server = WebsocketServer(host=ADDR, port=PORT, loglevel=logging.INFO)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(thread_threat_message)
    server.run_forever()


atexit.register(blend_controller.cleanup)

main2()

# asyncio.run(main())
