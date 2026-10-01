# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Automatically close a floodgate when the moisture sensor
# detects water. A red LED indicates a flood condition, a green LED indicates
# a safe condition, and a pushbutton resets/reopens the gate after the sensor is dry.
# Date code was started: 09/23/2026
# Date of last update: 09/23/2026
# Explanation of AI use: ChatGPT was used to help develop and organize the
# MicroPython code for sensor input, servo control, LEDs, and manual reset.
# The team tested and adjusted the system for the physical prototype.

from machine import Pin, ADC, PWM
from time import sleep

# --------------------------------------------------
# PIN SETUP
# --------------------------------------------------

# Pushbutton: A7 = GPIO 14
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Moisture sensor: A5 = GPIO 12
moisture_sensor = ADC(Pin(12))
moisture_sensor.atten(ADC.ATTN_11DB)

# LEDs
red_led = Pin(5, Pin.OUT)       # D2
green_led = Pin(6, Pin.OUT)     # D3

# Servo: D12 = GPIO 47
servo = PWM(Pin(47), freq=50)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

# Adjust this after testing your dry and wet readings.
# Dry should normally give a HIGHER reading than wet.
WATER_THRESHOLD = 65530

# Change these if your gate moves in the opposite direction.
GATE_CLOSED_ANGLE = 0
GATE_OPEN_ANGLE = 180


# --------------------------------------------------
# SERVO FUNCTION
# --------------------------------------------------

def set_servo_angle(angle):
    # Convert 0-180 degrees to approximately
    # 500-2500 microsecond servo pulses.
    pulse_us = 500 + int((angle / 180) * 2000)

    # Servo period at 50 Hz = 20,000 microseconds.
    duty = int((pulse_us / 20000) * 65535)

    servo.duty_u16(duty)


# --------------------------------------------------
# INITIAL STATE
# --------------------------------------------------

flood_detected = False
previous_button = 1

# Start safe with gate open.
set_servo_angle(GATE_OPEN_ANGLE)

green_led.on()
red_led.off()

print("Flood protection system started")
print("Gate OPEN")


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

while True:

    # Read moisture sensor.
    moisture_value = moisture_sensor.read_u16()

    # The sensor reading decreases when it gets wet.
    water_present = moisture_value < WATER_THRESHOLD

    # ----------------------------------------------
    # WATER DETECTION
    # ----------------------------------------------

    if water_present:
        flood_detected = True

    # ----------------------------------------------
    # RESET BUTTON
    # ----------------------------------------------

    current_button = button.value()

    # Detect a new button press.
    if current_button == 0 and previous_button == 1:

        if not water_present:
            flood_detected = False
            print("System RESET")

        else:
            print("Cannot reset: water is still detected")

    previous_button = current_button

    # ----------------------------------------------
    # CONTROL FLOODGATE
    # ----------------------------------------------

    if flood_detected:

        # Flood condition
        set_servo_angle(GATE_CLOSED_ANGLE)

        red_led.on()
        green_led.off()

        gate_status = "CLOSED"
        system_status = "FLOOD"

    else:

        # Safe condition
        set_servo_angle(GATE_OPEN_ANGLE)

        red_led.off()
        green_led.on()

        gate_status = "OPEN"
        system_status = "SAFE"

    # ----------------------------------------------
    # TERMINAL OUTPUT
    # ----------------------------------------------

    print(
        "Moisture:", moisture_value,
        "| Status:", system_status,
        "| Gate:", gate_status
    )

    sleep(0.2)