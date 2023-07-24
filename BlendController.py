from PumpController import PumpController
import time
from math import ceil
from enum import Enum
import json


class BlendAction(Enum):
    Idle = 0
    Blend = 1
    Refill = 2


class BlendController:
    def __init__(self):
        self.pump_controller = PumpController()

        self.initial_time = 0
        self.remaining_time = 0
        self.current_action = BlendAction.Idle

        self.states = {}
        self.load_states()

    def cleanup(self):
        self.pump_controller.cleanup()

    def blend(self, data, status_callback):
        """
        ex : {'cup_size': 0.25, 'ratios': {'1': 0.2, '2': 0.1, '5': 0.7}}
        """
        self.current_action = BlendAction.Blend

        cup_size = data['cup_size']
        quantities = {
            k: v * cup_size
            for k, v
            in data['ratios'].items()
        }
        times = {
            k: int(v * self.states["sec_per_liter"] * self.states["pumps"][int(k)]["speed_ratio"])
            for k, v
            in quantities.items()
        }

        self.initial_time = max(times.values())
        self.remaining_time = int(self.initial_time)

        for pump in times.keys():
            self.pump_controller.enable_pump(int(pump), True)

        while sum(times.values()) > 0:
            self.remaining_time = max(times.values())
            status_callback({"Action": self.current_action.name, "initial_time": self.initial_time, "remaining_time": self.remaining_time})
            time.sleep(1)

            for pump in times:
                if times[pump] > 0:
                    times[pump] -= 1
                else:
                    self.pump_controller.enable_pump(int(pump), False)

        self.remaining_time = 0
        status_callback({"Action": self.current_action.name, "initial_time": self.initial_time, "remaining_time": self.remaining_time})
        self.current_action = BlendAction.Idle

        return True

    def get_blend_status(self, status_callback):
        status_callback({"Action": self.current_action.name, "initial_time": self.initial_time, "remaining_time": self.remaining_time})

    def refill(self, data, status_callback):
        pump = data['pump']

        self.initial_time = self.states["pumps"][pump]["refill_time"]
        self.remaining_time = int(self.initial_time)

        self.pump_controller.enable_pump(int(pump), True)
        self.current_action = BlendAction.Refill
        while self.remaining_time > 0:
            status_callback({"Action": self.current_action.name, "initial_time": self.initial_time, "remaining_time": self.remaining_time})
            time.sleep(0.5)
            self.remaining_time -= 0.5
        self.pump_controller.enable_pump(int(pump), False)

        self.remaining_time = 0
        status_callback({"Action": self.current_action.name, "initial_time": self.initial_time, "remaining_time": self.remaining_time})
        self.current_action = BlendAction.Idle

    def change_pump_state(self, pump_index, enabled):
        self.states["pumps"][pump_index]["enabled"] = enabled
        self.save_states()

    def get_pump_states(self):
        return self.states["pumps"]

    def load_states(self):
        with open("states.json", 'r') as f:
            self.states = json.load(f)

    def save_states(self):
        with open("states.json", 'w') as f:
            json.dump(self.states, f)

    def set_pump_refill_time(self, pump_index, refill_time):
        self.states["pumps"][pump_index]["refill_time"] = refill_time
        self.save_states()

    def set_sec_per_liter(self, sec_per_liter):
        self.states["sec_per_liter"] = sec_per_liter
        self.save_states()

    def get_sec_per_liter(self):
        return self.states["sec_per_liter"]

    def set_pump_speed_ratio(self, pump_index, speed_ratio):
        self.states["pumps"][pump_index]["speed_ratio"] = speed_ratio
        self.save_states()
