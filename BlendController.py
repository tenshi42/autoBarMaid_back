from PumpController import PumpController, SEC_PER_LITER
import time
from math import ceil


class BlendAction:
    Idle = 0
    Blend = 1
    Refill = 2


class BlendController:
    def __init__(self):
        self.pump_controller = PumpController()

        self.initial_time = 0
        self.remaining_time = 0
        self.current_action = BlendAction.Idle

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
            k: int(v * SEC_PER_LITER)
            for k, v
            in quantities.items()
        }

        self.initial_time = max(times.values())
        self.remaining_time = int(self.remaining_time)

        for pump in times.keys():
            self.pump_controller.enable_pump(int(pump), True)

        while sum(times.values()) > 0:
            self.remaining_time = max(times.values())
            status_callback({"Action": self.current_action, "initial_time": self.initial_time, "remaining_time": self.remaining_time})
            time.sleep(1)

            for pump in times:
                if times[pump] > 0:
                    times[pump] -= 1
                else:
                    self.pump_controller.enable_pump(int(pump), False)

        self.remaining_time = 0
        status_callback({"Action": self.current_action, "initial_time": self.initial_time, "remaining_time": self.remaining_time})
        self.current_action = BlendAction.Idle

        return True

    def refill(self, data, status_callback):
        pump = data['pump']

        status_callback({"Action": self.current_action, "initial_time": self.initial_time, "remaining_time": self.remaining_time})

        common_time = 1  # to adjust with real data
        flow_speed = 1

        self.initial_time = common_time + ceil((int(pump) + 1) / 2) * flow_speed
        self.remaining_time = int(self.remaining_time)

        self.pump_controller.enable_pump(int(pump), True)
        self.current_action = BlendAction.Refill
        time.sleep(self.remaining_time)
        self.pump_controller.enable_pump(int(pump), False)

        self.remaining_time = 0
        status_callback({"Action": self.current_action, "initial_time": self.initial_time, "remaining_time": self.remaining_time})

        self.current_action = BlendAction.Idle
