import sys
import time

from telemetrix import telemetrix

# Set up a pin for analog input and monitor its changes
ANALOG_PIN = 2  # arduino pin number (A2)

# Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3


def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """
    # date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    # print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]}
    # Time Stamp: {date}')
    print(data)


board = telemetrix.Telemetrix(com_port='/dev/ttyACM0') # Works fine, it connects to COM12
board.set_pin_mode_analog_input(ANALOG_PIN, differential=5, callback=the_callback)
print('sleep1')
time.sleep(3)
board.set_pin_mode_digital_input(12, the_callback)
time.sleep(3)
board.shutdown()
board = telemetrix.Telemetrix(com_port='/dev/ttyACM0') # Works fine, it connects to COM12
board.set_pin_mode_analog_input(ANALOG_PIN, differential=5, callback=the_callback)
print('sleep2')
time.sleep(3)
board.set_pin_mode_digital_input(12, the_callback)
time.sleep(3)
board.shutdown()

board = telemetrix.Telemetrix() # Works fine, it connects to COM12
board.set_pin_mode_analog_input(ANALOG_PIN, differential=5, callback=the_callback)
print('sleep1')
time.sleep(3)
board.set_pin_mode_digital_input(12, the_callback)
time.sleep(3)
board.shutdown()
board = telemetrix.Telemetrix() # Works fine, it connects to COM12
board.set_pin_mode_analog_input(ANALOG_PIN, differential=5, callback=the_callback)
print('sleep2')
time.sleep(3)
board.set_pin_mode_digital_input(12, the_callback)
time.sleep(3)
board.shutdown()