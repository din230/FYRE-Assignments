# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Measure the response of the homemade PEDOT:PSS
# humidity sensor relative to its dry baseline.
# Date code was started: 09/27/2026
# Explanation of AI use: ChatGPT was used to help calculate and display
# the percent change from the dry PEDOT:PSS baseline.

from machine import Pin, ADC
from time import sleep


# PEDOT:PSS sensor connected to A2 = GPIO 3
pedot_sensor = ADC(Pin(3))
pedot_sensor.atten(ADC.ATTN_11DB)


# ----------------------------------------------
# CALIBRATION
# ----------------------------------------------

print("Calibrating PEDOT:PSS sensor")
print("Keep sensor dry.")
print()


total = 0
samples = 20


for i in range(samples):

    value = pedot_sensor.read_u16()

    total += value

    print(
        "Calibration sample",
        i + 1,
        ":",
        value
    )

    sleep(0.1)


baseline = total / samples


print()
print("Dry baseline:", baseline)
print()


# ----------------------------------------------
# SENSOR TEST
# ----------------------------------------------

while True:

    value = pedot_sensor.read_u16()

    difference = value - baseline

    absolute_difference = abs(difference)


    if baseline > 0:

        percent_change = (
            absolute_difference
            / baseline
        ) * 100

    else:

        percent_change = 0


    print(
        "PEDOT:",
        value,
        "| Baseline:",
        round(baseline),
        "| Delta:",
        round(difference),
        "| Change:",
        round(percent_change, 2),
        "%"
    )


    sleep(0.25)