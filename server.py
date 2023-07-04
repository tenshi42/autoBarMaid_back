import json
import logging
import atexit

from websocket_server import WebsocketServer
from threading import Thread

from BlendController import BlendController

ADDR = "0.0.0.0"
PORT = 8765


def new_client(client, server):
    print("hi !")
    print(client)


def thread_threat_message(client, server, message):
    t = Thread(target=threat_message, args=[client, server, message])
    t.start()


def threat_message(client, server, message):
    packet = json.loads(message)
    if packet['type'] == 'echo':
        print(f"Recv message : {packet['data']}")

        server.send_message(client, json.dumps(packet))
    elif packet['type'] == 'blend':
        print(f"Recv blend : {packet['data']}")

        def callback(remaining_time):
            server.send_message(client, json.dumps({'type': 'status', 'data': {'remaining_time': remaining_time}}))

        res = blend_controller.blend(packet['data'], callback)
        if not res:
            server.send_message(client, json.dumps({'type': 'error', 'data': {'msg': f'Already blending ! Retry in {blend_controller.remaining_time} sec'}}))


def main():
    server = WebsocketServer(host=ADDR, port=PORT, loglevel=logging.INFO)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(thread_threat_message)
    server.run_forever()


blend_controller = BlendController()
atexit.register(blend_controller.cleanup)

main()
