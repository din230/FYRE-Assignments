# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Read the analog output of a rain-drop sensor using the ADC,
# convert the readings to volts, collect 10 samples, and save the data to a CSV file.
# Date code was started: 09/16/2026
# Date of last update: 09/16/2026
# Explanation of AI use: ChatGPT was used to help generate and organize the MicroPython
# code for ADC sampling, voltage conversion, and saving the measurements to a CSV file.
# The code and collected data were tested and verified by the team.

from machine import Pin, ADC
from time import sleep

# A5 on the Arduino Nano ESP32 is GPIO 12
sensor = ADC(Pin(12))

# Allow measurement of a wider voltage range
sensor.atten(ADC.ATTN_11DB)

# Change this filename for each experimental condition
filename = "blowing_on_it2.csv"

# Number of samples required
number_of_samples = 10

with open(filename, "w") as file:

    # CSV header
    file.write("Sample,Voltage (V)\n")

    for sample in range(1, number_of_samples + 1):

        # Read sensor voltage and convert microvolts to volts
        voltage = sensor.read_uv() / 1000000

        # Display measurement in terminal
        print("Sample", sample, ":", voltage, "V")

        # Save measurement to CSV
        file.write("{},{}\n".format(sample, voltage))

        sleep(0.1)

print("Data saved to", filename)