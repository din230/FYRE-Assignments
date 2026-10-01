# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Control a servo motor using a switch. When the switch is pressed,
# the servo moves to 0 degrees, and when the switch is not pressed, it moves to 180 degrees.
# Date code was started: 09/16/2026
# Date of last update: 09/16/2026
# Explanation of AI use: ChatGPT was used to help generate the MicroPython code for reading
# the switch input and controlling the servo position using PWM. The code was tested by the team.

from machine import Pin, PWM
from time import sleep

# Inputs
switch = Pin(5, Pin.IN, Pin.PULL_UP)   # D2

# Servo
servo = PWM(Pin(8), freq=50)          # D5


def set_angle(angle):
    # Convert 0-180 degrees to a servo pulse width
    pulse_us = 500 + int((angle / 180) * 2000)

    # Convert pulse width to 16-bit PWM duty cycle
    duty = int((pulse_us / 20000) * 65535)

    servo.duty_u16(duty)


while True:

    if switch.value() == 0:   # Switch pressed
        set_angle(0)
        print("Switch pressed | Servo: 0 degrees")

    else:                     # Switch not pressed
        set_angle(180)
        print("Switch not pressed | Servo: 180 degrees")

    sleep(0.1)