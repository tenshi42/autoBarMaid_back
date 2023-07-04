from PumpController import PumpController, SEC_PER_LITER
import time


class BlendController:
    def __init__(self):
        self.pump_controller = PumpController()

        self.remaining_time = 0

    def cleanup(self):
        self.pump_controller.cleanup()

    def blend(self, data, status_callback):
        """
        ex : {'cup_size': 0.25, 'ratios': {'1': 0.2, '2': 0.1, '5': 0.7}}
        """
        if self.remaining_time > 0:
            return

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

        self.remaining_time = max(times.values())

        for pump in times.keys():
            self.pump_controller.enable_pump(int(pump), True)

        while sum(times.values()) > 0:
            self.remaining_time = max(times.values())
            status_callback(self.remaining_time)
            time.sleep(1)

            for pump in times:
                if times[pump] > 0:
                    times[pump] -= 1
        self.remaining_time = 0
        status_callback(0)

        return True
