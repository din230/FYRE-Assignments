# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Test whether a raw ADC difference (delta)
# is more reliable than percentage change for detecting humidity
# with the homemade PEDOT:PSS sensor.
# Date code was started: 09/28/2026
# Explanation of AI use: ChatGPT was used to help compare raw ADC
# difference and percentage-change detection methods.

from machine import Pin, ADC
from time import sleep


pedot_sensor = ADC(Pin(3))
pedot_sensor.atten(ADC.ATTN_11DB)


DELTA_THRESHOLD = 600

REQUIRED_READINGS = 8


# ----------------------------------------------
# CALIBRATION
# ----------------------------------------------

total = 0

samples = 20


print("Keep PEDOT:PSS sensor dry.")


for i in range(samples):

    value = pedot_sensor.read_u16()

    total += value

    sleep(0.1)


baseline = total / samples


print(
    "Dry baseline:",
    baseline
)


# ----------------------------------------------
# DELTA TEST
# ----------------------------------------------

trigger_count = 0


while True:

    value = pedot_sensor.read_u16()


    difference = (
        value - baseline
    )


    absolute_difference = abs(
        difference
    )


    if absolute_difference >= DELTA_THRESHOLD:

        trigger_count += 1

    else:

        trigger_count = 0


    detected = (
        trigger_count
        >= REQUIRED_READINGS
    )


    # Percentage is displayed for comparison,
    # but the trigger uses raw delta.
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
        "%",
        "| Count:",
        trigger_count,
        "| Trigger:",
        detected
    )


    sleep(0.25)