import json
import logging
import atexit

from websocket_server import WebsocketServer
from threading import Thread

from BlendController import BlendController, BlendAction

ADDR = "0.0.0.0"
PORT = 8765


def new_client(client, server):
    print("hi !")
    print(client)


def thread_threat_message(client, server, message):
    t = Thread(target=threat_message, args=[client, server, message])
    t.start()


def if_not_busy(server, client, action, data, callback):
    if blend_controller.current_action != BlendAction.Idle:
        server.send_message(client, json.dumps({'type': 'error', 'data': {'msg': f'Busy ! Retry in {blend_controller.remaining_time} sec'}}))
    else:
        return action(data, callback)


def threat_message(client, server, message):
    packet = json.loads(message)
    message_type = packet['type']
    print(f"Recv {message_type} : {packet['data']}")

    def callback(data):
        server.send_message(client, json.dumps({'type': 'status', 'data': data}))

    if message_type == 'echo':
        server.send_message(client, json.dumps(packet))
    elif message_type == 'blend':
        if_not_busy(server, client, blend_controller.blend, packet['data'], callback)
    elif message_type == "refill":
        if_not_busy(server, client, blend_controller.refill, packet['data'], callback)


def main():
    server = WebsocketServer(host=ADDR, port=PORT, loglevel=logging.INFO)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(thread_threat_message)
    server.run_forever()


blend_controller = BlendController()
atexit.register(blend_controller.cleanup)

main()
