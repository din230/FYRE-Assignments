# Team member names: Diego Chuquillanqui, Diane Ngo, Artur Kis
# Purpose of the code: Control an automatic floodgate prototype using a
# rain sensor and a homemade PEDOT:PSS humidity sensor. Either sensor can
# automatically close the gate. A red LED indicates a flood condition,
# a green LED indicates safe conditions, and a pushbutton manually
# reopens the gate when the rain sensor is dry.
# Date code was started: 09/27/2026
# Date of last update: 10/01/2026
# Explanation of AI use: ChatGPT was used to help combine the sensors,
# LEDs, stepper motor, and reset button and to revise the PEDOT:PSS
# control logic because the sensor has a slow recovery after humidity exposure.

from machine import Pin, ADC
from time import sleep, sleep_us, ticks_ms, ticks_diff


# ==================================================
# INPUTS
# ==================================================

# Homemade PEDOT:PSS humidity sensor
# A2 = GPIO 3
homemade_sensor = ADC(Pin(3))
homemade_sensor.atten(ADC.ATTN_11DB)

# Commercial rain sensor
# A5 = GPIO 12
rain_sensor = ADC(Pin(12))
rain_sensor.atten(ADC.ATTN_11DB)

# Manual reset button
# A7 = GPIO 14
# PULL_UP means:
# 1 = not pressed
# 0 = pressed
button = Pin(14, Pin.IN, Pin.PULL_UP)


# ==================================================
# OUTPUTS
# ==================================================

red_led = Pin(5, Pin.OUT)       # D2
green_led = Pin(6, Pin.OUT)     # D3


# ==================================================
# STEPPER MOTOR
# ==================================================

# GPIO pins connected to the ULN2003 stepper driver
IN1 = Pin(7, Pin.OUT)
IN2 = Pin(8, Pin.OUT)
IN3 = Pin(9, Pin.OUT)
IN4 = Pin(10, Pin.OUT)

motor_pins = [IN1, IN2, IN3, IN4]

# Half-step sequence for the 28BYJ-48 stepper motor
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


# ==================================================
# SENSOR SETTINGS
# ==================================================

# Rain sensor:
# Dry is approximately 65535.
# Lower values indicate more water.
RAIN_THRESHOLD = 35000


# PEDOT:PSS sensor:
# Close the gate if the sensor changes by at least
# 25% compared with its dry baseline.
PEDOT_TRIGGER_PERCENT = 25

# After triggering, the PEDOT sensor will not be
# used again until it returns close to its baseline.
PEDOT_REARM_PERCENT = 10

# Number of consecutive readings required before
# triggering the PEDOT sensor.
PEDOT_REQUIRED_READINGS = 8

# Number of safe readings required before the
# PEDOT sensor becomes active again.
PEDOT_REARM_READINGS = 8


# ==================================================
# MOTOR SETTINGS
# ==================================================

# Number of stepper half-steps used to move the gate
GATE_TRAVEL_STEPS = 7000

# Delay between steps.
# Larger number = slower motor but generally more reliable.
STEP_DELAY_US = 900

# Motor is forced off after this amount of time.
MAX_MOTOR_TIME_MS = 8000

# Direction experimentally determined to close gate
CLOSE_DIRECTION = -1


# ==================================================
# MOTOR FUNCTIONS
# ==================================================

def apply_step(step):
    """Send one step pattern to the motor driver."""

    for pin, value in zip(motor_pins, step):
        pin.value(value)


def motor_off():
    """Turn off all four motor outputs."""

    for pin in motor_pins:
        pin.off()


def move(steps, direction):
    """Move the stepper while enforcing a safety timeout."""

    start_time = ticks_ms()
    steps_completed = 0

    try:

        for i in range(steps):

            # Stop the motor if it runs for too long.
            elapsed = ticks_diff(
                ticks_ms(),
                start_time
            )

            if elapsed >= MAX_MOTOR_TIME_MS:

                print()
                print("!!! MOTOR SAFETY STOP !!!")
                print("Maximum motor time reached.")
                print()

                break


            # Select motor sequence based on direction.
            if direction == 1:

                step = sequence[i % 8]

            else:

                step = sequence[7 - (i % 8)]


            apply_step(step)

            sleep_us(STEP_DELAY_US)

            steps_completed += 1


    finally:

        # Always remove power from the motor coils
        # when movement is finished.
        motor_off()


    return steps_completed


def close_gate():
    """Move the motor in the closing direction."""

    print()
    print("==============================")
    print(">>> CLOSING GATE")
    print("==============================")

    completed = move(
        GATE_TRAVEL_STEPS,
        CLOSE_DIRECTION
    )

    print("Steps completed:", completed)
    print(">>> MOTOR OFF")
    print(">>> GATE CLOSED")
    print()


def open_gate():
    """Move the motor in the opening direction."""

    print()
    print("==============================")
    print(">>> OPENING GATE")
    print("==============================")

    completed = move(
        GATE_TRAVEL_STEPS,
        -CLOSE_DIRECTION
    )

    print("Steps completed:", completed)
    print(">>> MOTOR OFF")
    print(">>> GATE OPEN")
    print()


# ==================================================
# PEDOT:PSS CALIBRATION
# ==================================================

def calibrate_homemade_sensor():
    """Measure the dry PEDOT:PSS value at startup."""

    print()
    print("Calibrating PEDOT:PSS sensor...")
    print("KEEP THE SENSOR DRY")
    print()

    total = 0
    samples = 20

    for i in range(samples):

        value = homemade_sensor.read_u16()

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
    print(
        "PEDOT:PSS dry baseline:",
        baseline
    )
    print()

    return baseline


homemade_baseline = calibrate_homemade_sensor()


# ==================================================
# INITIAL STATE
# ==================================================

# Gate physically begins open.
gate_closed = False

# Prevent multiple motor commands at the same time.
motor_busy = False

# PEDOT sensor begins active.
pedot_armed = True

# Consecutive trigger readings
pedot_trigger_count = 0

# Consecutive safe readings used to re-arm PEDOT
pedot_rearm_count = 0

# Used to detect a new button press
previous_button = 1


red_led.off()
green_led.on()


print()
print("==============================")
print("FLOODGATE SYSTEM STARTED")
print("==============================")
print("Gate should begin physically OPEN")
print()


# ==================================================
# MAIN LOOP
# ==================================================

while True:

    # ------------------------------------------------
    # READ INPUTS
    # ------------------------------------------------

    homemade_value = homemade_sensor.read_u16()

    rain_value = rain_sensor.read_u16()

    current_button = button.value()


    # ------------------------------------------------
    # RAIN SENSOR
    # ------------------------------------------------

    rain_detected = (
        rain_value < RAIN_THRESHOLD
    )


    # ------------------------------------------------
    # PEDOT:PSS PERCENT CHANGE
    # ------------------------------------------------

    homemade_difference = (
        homemade_value
        - homemade_baseline
    )

    homemade_absolute_difference = abs(
        homemade_difference
    )


    if homemade_baseline > 0:

        homemade_percent_change = (
            homemade_absolute_difference
            / homemade_baseline
        ) * 100

    else:

        homemade_percent_change = 0


    # ------------------------------------------------
    # PEDOT TRIGGER / RE-ARM LOGIC
    # ------------------------------------------------

    pedot_detected = False


    if pedot_armed:

        # Count how many readings remain above
        # the PEDOT trigger threshold.
        if (
            homemade_percent_change
            >= PEDOT_TRIGGER_PERCENT
        ):

            pedot_trigger_count += 1

        else:

            pedot_trigger_count = 0


        # Trigger only after several readings in a row.
        if (
            pedot_trigger_count
            >= PEDOT_REQUIRED_READINGS
        ):

            pedot_detected = True

            # Disarm the PEDOT sensor after triggering.
            # This prevents its slow recovery from
            # repeatedly closing the gate.
            pedot_armed = False

            pedot_rearm_count = 0


    else:

        # PEDOT is currently disarmed.
        pedot_trigger_count = 0


        # Wait until it has recovered close to the
        # original dry baseline.
        if (
            homemade_percent_change
            <= PEDOT_REARM_PERCENT
        ):

            pedot_rearm_count += 1

        else:

            pedot_rearm_count = 0


        # Re-arm only after several stable dry readings.
        if (
            pedot_rearm_count
            >= PEDOT_REARM_READINGS
        ):

            pedot_armed = True

            pedot_rearm_count = 0

            print()
            print(
                ">>> PEDOT:PSS SENSOR RE-ARMED"
            )
            print()


    # ------------------------------------------------
    # AUTOMATIC GATE CLOSING
    # ------------------------------------------------

    # Either sensor can initially close the gate.
    close_condition = (
        rain_detected
        or pedot_detected
    )


    if (
        close_condition
        and not gate_closed
        and not motor_busy
    ):

        # Latch the closed state before moving.
        # This prevents repeated close commands.
        gate_closed = True
        motor_busy = True


        red_led.on()
        green_led.off()


        print()
        print("!!! MOISTURE WARNING !!!")


        if rain_detected:

            print("Rain sensor triggered")


        if pedot_detected:

            print("PEDOT:PSS sensor triggered")


        close_gate()

        motor_busy = False


    # ------------------------------------------------
    # MANUAL RESET BUTTON
    # ------------------------------------------------

    # Detect the moment the button changes from
    # not pressed to pressed.
    button_pressed = (
        current_button == 0
        and previous_button == 1
    )


    if (
        gate_closed
        and button_pressed
        and not motor_busy
    ):

        # Because PEDOT:PSS can take several minutes
        # to recover, reset depends only on the rain
        # sensor being dry.
        if not rain_detected:

            print()
            print("Reset accepted")
            print("Rain sensor is dry")


            # Keep PEDOT disarmed after reopening.
            # It will automatically re-arm after
            # returning close to its dry baseline.
            pedot_armed = False
            pedot_trigger_count = 0
            pedot_rearm_count = 0


            motor_busy = True

            open_gate()

            gate_closed = False
            motor_busy = False


            red_led.off()
            green_led.on()


        else:

            print()
            print("Cannot reset")
            print("Rain sensor still detects water")
            print()


    previous_button = current_button


    # ------------------------------------------------
    # TERMINAL OUTPUT
    # ------------------------------------------------

    if gate_closed:

        gate_status = "CLOSED"

    else:

        gate_status = "OPEN"


    print(
        "PEDOT:",
        homemade_value,

        "| Baseline:",
        round(homemade_baseline),

        "| Change:",
        round(
            homemade_percent_change,
            2
        ),
        "%",

        "| Armed:",
        pedot_armed,

        "| Trigger Count:",
        pedot_trigger_count,

        "| Rearm Count:",
        pedot_rearm_count,

        "| Rain:",
        rain_value,

        "| Rain Trigger:",
        rain_detected,

        "| Gate:",
        gate_status
    )


    sleep(0.25)