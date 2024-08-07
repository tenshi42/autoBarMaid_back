import RPi.GPIO as GPIO


class PumpController:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.pump_pins = [7, 11, 12, 13, 15, 16, 18, 22]
        for pin in self.pump_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

    def cleanup(self):
        GPIO.cleanup()

    def enable_pump(self, pump_number, state):
        GPIO.output(self.pump_pins[pump_number], GPIO.HIGH if not state else GPIO.LOW)
