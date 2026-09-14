from machine import Pin, ADC
from time import sleep

# Inputs
light_sensor = ADC(Pin(1))            # A0
potentiometer = ADC(Pin(2))           # A1
button = Pin(5, Pin.IN, Pin.PULL_UP)  # D2

# Outputs
red_led = Pin(9, Pin.OUT)             # D6
green_led = Pin(10, Pin.OUT)          # D7

# Thresholds
light_threshold = 30000
arm_threshold = 32768

while True:
    light_value = light_sensor.read_u16()
    pot_value = potentiometer.read_u16()
    button_pressed = button.value() == 0

    armed = pot_value > arm_threshold
    light_triggered = light_value > light_threshold

    if armed and (button_pressed or light_triggered):
        red_led.on()
        green_led.off()
        alarm = "ON"
    elif armed:
        red_led.off()
        green_led.on()
        alarm = "OFF"
    else:
        red_led.off()
        green_led.off()
        alarm = "OFF"

    print("Light:", light_value, "| Alarm:", alarm)

    sleep(0.1)