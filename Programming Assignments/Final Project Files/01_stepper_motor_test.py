# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Test the 28BYJ-48 stepper motor in both directions
# before integrating it into the automatic floodgate.
# Date code was started: 09/27/2026
# Explanation of AI use: ChatGPT was used to help organize and troubleshoot
# the stepper motor sequence.

from machine import Pin
from time import sleep_ms, sleep_us


# ULN2003 stepper driver connections
IN1 = Pin(7, Pin.OUT)
IN2 = Pin(8, Pin.OUT)
IN3 = Pin(9, Pin.OUT)
IN4 = Pin(10, Pin.OUT)

motor_pins = [IN1, IN2, IN3, IN4]


# Half-step sequence for the 28BYJ-48
sequence = [
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1)
]


def apply_step(step):

    for pin, value in zip(motor_pins, step):
        pin.value(value)


def move(steps, direction):

    for i in range(steps):

        if direction == 1:
            step = sequence[i % 8]

        else:
            step = sequence[7 - (i % 8)]

        apply_step(step)

        sleep_us(700)


def motor_off():

    for pin in motor_pins:
        pin.off()


# Test first direction
print("Moving direction 1")

move(16384, 1)

motor_off()

sleep_ms(1000)


# Test opposite direction
print("Moving direction -1")

move(16384, -1)

motor_off()

print("Motor test complete")