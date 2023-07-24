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


def send_message(server, msg_type, data):
    server.send_message_to_all(json.dumps({
        'type': msg_type,
        'data': data
    }))


def thread_threat_message(client, server, message):
    t = Thread(target=threat_message, args=[client, server, message])
    t.start()


def if_not_busy(server, action, data, callback):
    if blend_controller.current_action != BlendAction.Idle:
        send_message(server, 'error', {'msg': f'Busy ! Retry in {blend_controller.remaining_time} sec'})
    else:
        return action(data, callback)


def threat_message(client, server, message):
    packet = json.loads(message)
    message_type = packet['type']
    # print(f"Recv {message_type} : {packet['data']}")

    def callback(data):
        send_message(server, 'status', data)

    if message_type == 'echo':
        send_message(server, 'echo', packet)
    elif message_type == 'blend':
        if_not_busy(server, blend_controller.blend, packet['data'], callback)
    elif message_type == "get_blend_status":
        blend_controller.get_blend_status(callback)
    elif message_type == "refill":
        if_not_busy(server, blend_controller.refill, packet['data'], callback)
    elif message_type == "get_pumps_states":
        send_message(server, 'pumps_states', blend_controller.get_pump_states())
    elif message_type == "set_pump_state":
        pump_index = packet['data']['pump_index']
        state = packet['data']['state']
        blend_controller.change_pump_state(pump_index, state)
        send_message(server, 'pumps_states', blend_controller.get_pump_states())
    elif message_type == "set_pump_refill_time":
        pump_index = packet['data']['pump_index']
        refill_time = packet['data']['refill_time']
        blend_controller.set_pump_refill_time(pump_index, refill_time)
        send_message(server, 'pumps_states', blend_controller.get_pump_states())
    elif message_type == "set_sec_per_liter":
        sec_per_liter = packet['data']['sec_per_liter']
        blend_controller.set_sec_per_liter(sec_per_liter)
        send_message(server, 'sec_per_liter', blend_controller.get_sec_per_liter())
    elif message_type == "get_config":
        send_message(server, 'config', blend_controller.states)
    elif message_type == "set_pump_speed_ratio":
        pump_index = packet['data']['pump_index']
        speed_ratio = packet['data']['speed_ratio']
        blend_controller.set_pump_speed_ratio(pump_index, speed_ratio)
        send_message(server, 'config', blend_controller.states)
    elif message_type == "reload_config":
        blend_controller.load_states()
        send_message(server, 'config', blend_controller.states)

    else:
        send_message(server, 'unknown_message_type', {"message": f"given message type '{message_type}' is unknown"})


def main():
    server = WebsocketServer(host=ADDR, port=PORT, loglevel=logging.INFO)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(thread_threat_message)
    server.run_forever()


blend_controller = BlendController()
atexit.register(blend_controller.cleanup)

main()
