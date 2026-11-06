"""
Hardware pinout and system configurations.
"""

# DC Motors (Direction and Enable/PWM pins)
MOTOR_PINS = [
    {"A": 27, "B": 17, "E": 22},  # Motor 1
    {"A": 6,  "B": 5,  "E": 13},  # Motor 2
    {"A": 19, "B": 26, "E": 12},  # Motor 3
    {"A": 24, "B": 23, "E": 25}   # Motor 4
]

# Line Tracking Sensors (Digital Inputs)
PIN_LINE_LEFT = 16
PIN_LINE_MIDDLE = 4
PIN_LINE_RIGHT = 18

# Compartment Actuators (Servos) & Drawer State Sensors
SERVO_PINS = [20, 8, 14]
DRAWER_SENSOR_PINS = [15, 10, 9]

# PWM Parameters
PWM_FREQ_MOTOR = 100  # Hz
PWM_FREQ_SERVO = 50   # Hz