import serial
import time

DATA_TYPE_LEVEL = 1
DATA_TYPE_SERVE = 2
DATA_TYPE_LEVEL_TIME = 3
DATA_TYPE_DEBUG_SERVE = 50
DATA_TYPE_DEBUG_LEVEL = 51
DATA_TYPE_DEBUG_ONE = 52
DATA_TYPE_DEBUG_ALL = 53
DATA_TYPE_MSG = 98
DATA_TYPE_END = 99


PUMP_START_TIME = 3
PUMP_END_TIME = 7


class PumpControllerPlus:
    def __init__(self):
        # self.ser = serial.Serial('COM3', 9600)
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.msg_callback = None

    def cleanup(self):
        self.ser.close()

    def read_all(self):
        buffer = b''
        while self.ser.inWaiting():
            buffer += self.ser.read()
        return buffer

    def send_one(self, bb):
        self.ser.write(bb)
        time.sleep(1)

    def treat_sub_buffer(self, sub_buffer):
        cmd = sub_buffer[0]
        if cmd == DATA_TYPE_END:
            print("gonna stop !")
            self.msg_callback(DATA_TYPE_END, None)
            return False
        elif cmd == DATA_TYPE_LEVEL:
            print(f"level : {str(sub_buffer[1])}")
            self.msg_callback(DATA_TYPE_LEVEL, sub_buffer[1:])
            return True
        elif cmd == DATA_TYPE_LEVEL_TIME:
            # print(sub_buffer[1])
            # print(sub_buffer[2])
            val = (int(sub_buffer[2]) << 8) + int(sub_buffer[1])
            print(f"level time : {val}")
            self.msg_callback(DATA_TYPE_LEVEL_TIME, val)
            return True
        elif cmd == DATA_TYPE_MSG:
            print(f"msg : {sub_buffer[1:].decode()}")
            self.msg_callback(DATA_TYPE_MSG, sub_buffer[1:])
            return True
        elif cmd == DATA_TYPE_SERVE:
            self.msg_callback(DATA_TYPE_SERVE, None)
            return True

    def treat_recv(self, endless=True):
        while True:
            buffer = self.read_all()
            if not endless and not buffer:
                return
            while buffer:
                size = buffer[0]
                sub_buffer, buffer = buffer[1:size+1], buffer[size+1:]
                should_continue = self.treat_sub_buffer(sub_buffer)
                if not should_continue:
                    break
            time.sleep(1)

    def serve(self, pump_index, quantity):
        print(f"serve | pump : {pump_index} | time : {quantity}")
        b = bytearray()
        b.append(3)  # size
        b.append(DATA_TYPE_SERVE)  # data type
        b.append(pump_index)  # pump index
        b.append(quantity)  # value
        self.send_one(b)

    def debug_one(self, pump_index):
        b = bytearray()
        b.append(2)  # size
        b.append(DATA_TYPE_DEBUG_ONE)  # data type
        b.append(pump_index)  # pump index
        self.send_one(b)
