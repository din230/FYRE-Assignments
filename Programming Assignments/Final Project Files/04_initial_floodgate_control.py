# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Initial integration of the rain sensor,
# homemade PEDOT:PSS sensor, LEDs, reset button, and stepper motor
# for the automatic floodgate.
# Date code was started: 09/27/2026
# Date of last update: 09/28/2026
# Explanation of AI use: ChatGPT was used to help combine the individual
# sensors and stepper motor into one control program.

from machine import Pin, ADC
from time import sleep, sleep_us


# ==================================================
# INPUTS
# ==================================================

pedot_sensor = ADC(Pin(3))      # A2
pedot_sensor.atten(ADC.ATTN_11DB)

rain_sensor = ADC(Pin(12))      # A5
rain_sensor.atten(ADC.ATTN_11DB)

button = Pin(14, Pin.IN, Pin.PULL_UP)


# ==================================================
# OUTPUTS
# ==================================================

red_led = Pin(5, Pin.OUT)
green_led = Pin(6, Pin.OUT)


# ==================================================
# STEPPER MOTOR
# ==================================================

IN1 = Pin(7, Pin.OUT)
IN2 = Pin(8, Pin.OUT)
IN3 = Pin(9, Pin.OUT)
IN4 = Pin(10, Pin.OUT)

motor_pins = [IN1, IN2, IN3, IN4]


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


RAIN_THRESHOLD = 65500

PEDOT_CHANGE_PERCENT = 10

PEDOT_REQUIRED_READINGS = 8

GATE_TRAVEL_STEPS = 5461

STEP_DELAY_US = 700

CLOSE_DIRECTION = -1


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

        sleep_us(STEP_DELAY_US)


def motor_off():

    for pin in motor_pins:
        pin.off()


def close_gate():

    print(">>> CLOSING GATE")

    move(
        GATE_TRAVEL_STEPS,
        CLOSE_DIRECTION
    )

    motor_off()


def open_gate():

    print(">>> OPENING GATE")

    move(
        GATE_TRAVEL_STEPS,
        -CLOSE_DIRECTION
    )

    motor_off()


# ==================================================
# PEDOT CALIBRATION
# ==================================================

total = 0

for i in range(20):

    total += pedot_sensor.read_u16()

    sleep(0.1)


pedot_baseline = total / 20


print(
    "PEDOT dry baseline:",
    pedot_baseline
)


# ==================================================
# MAIN CONTROL
# ==================================================

gate_closed = False

pedot_trigger_count = 0

previous_button = 1


green_led.on()
red_led.off()


while True:

    pedot_value = pedot_sensor.read_u16()

    rain_value = rain_sensor.read_u16()

    current_button = button.value()


    rain_detected = (
        rain_value < RAIN_THRESHOLD
    )


    difference = abs(
        pedot_value - pedot_baseline
    )


    percent_change = (
        difference
        / pedot_baseline
    ) * 100


    if percent_change >= PEDOT_CHANGE_PERCENT:

        pedot_trigger_count += 1

    else:

        pedot_trigger_count = 0


    pedot_detected = (
        pedot_trigger_count
        >= PEDOT_REQUIRED_READINGS
    )


    unsafe = (
        rain_detected
        or pedot_detected
    )


    if unsafe and not gate_closed:

        red_led.on()
        green_led.off()

        close_gate()

        gate_closed = True


    button_pressed = (
        current_button == 0
        and previous_button == 1
    )


    if (
        gate_closed
        and button_pressed
        and not unsafe
    ):

        open_gate()

        gate_closed = False

        red_led.off()
        green_led.on()


    previous_button = current_button


    print(
        "PEDOT:",
        pedot_value,
        "| Change:",
        round(percent_change, 2),
        "%",
        "| Rain:",
        rain_value,
        "| Gate closed:",
        gate_closed
    )


    sleep(0.25)