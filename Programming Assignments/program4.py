# Blinking program

# Incorperate/include modules
## Module with all the microcontroller stuff
import machine

## Module with time methods
import time

# Make the LED object
## Green LED is GPIO Pin 0
led = machine.Pin(0, machine.Pin.OUT)

# Infinite loop
while True:
  ## Turns on the LED
  led.value(1)

  ## Controls the speed with a 0.25 second delay
  time.sleep(0.25)

  ## Turns off the LED
  led.value(0)
  
  ## 0.25 second delay
  time.sleep(0.25)