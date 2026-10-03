# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Read the commercial rain sensor and observe how
# its ADC value changes between dry and wet conditions.
# Date code was started: 09/27/2026
# Explanation of AI use: ChatGPT was used to help organize the MicroPython
# sensor-reading code.

from machine import Pin, ADC
from time import sleep


# Rain sensor connected to A5 = GPIO 12
rain_sensor = ADC(Pin(12))
rain_sensor.atten(ADC.ATTN_11DB)


print("Rain sensor test started")
print("Lower readings indicate more water.")
print()


while True:

    rain_value = rain_sensor.read_u16()

    print(
        "Rain sensor ADC:",
        rain_value
    )

    sleep(0.5)