"""
DC Motor driver and closed-loop line tracking controller.
"""
import time
import RPi.GPIO as GPIO
from config import MOTOR_PINS, PIN_LINE_LEFT, PIN_LINE_MIDDLE, PIN_LINE_RIGHT, PWM_FREQ_MOTOR

class MotorController:
    def __init__(self):
        self.pwms = []
        self._setup_gpio()

    def _setup_gpio(self):
        for motor in MOTOR_PINS:
            GPIO.setup(motor["A"], GPIO.OUT)
            GPIO.setup(motor["B"], GPIO.OUT)
            GPIO.setup(motor["E"], GPIO.OUT)
            pwm = GPIO.PWM(motor["E"], PWM_FREQ_MOTOR)
            pwm.start(0)
            self.pwms.append(pwm)

        GPIO.setup(PIN_LINE_LEFT, GPIO.IN)
        GPIO.setup(PIN_LINE_MIDDLE, GPIO.IN)
        GPIO.setup(PIN_LINE_RIGHT, GPIO.IN)

    def _set_motors(self, states, speed):
        for i, motor in enumerate(MOTOR_PINS):
            GPIO.output(motor["A"], states[i][0])
            GPIO.output(motor["B"], states[i][1])
            self.pwms[i].ChangeDutyCycle(speed)

    def stop(self):
        for pwm in self.pwms:
            pwm.ChangeDutyCycle(0)

    def line_follow(self):
        while True:
            left = GPIO.input(PIN_LINE_LEFT)
            middle = GPIO.input(PIN_LINE_MIDDLE)
            right = GPIO.input(PIN_LINE_RIGHT)

            if left == 1 and middle == 1 and right == 1:
                # Forward
                states = [(GPIO.HIGH, GPIO.LOW)] * 4
                self._set_motors(states, 70)
            elif left == 0 and right == 1:
                # Turn Right
                states = [
                    (GPIO.HIGH, GPIO.LOW),
                    (GPIO.LOW, GPIO.LOW),
                    (GPIO.LOW, GPIO.LOW),
                    (GPIO.HIGH, GPIO.LOW)
                ]
                self._set_motors(states, 65)
            elif right == 0 and left == 1:
                # Turn Left
                states = [
                    (GPIO.LOW, GPIO.LOW),
                    (GPIO.HIGH, GPIO.LOW),
                    (GPIO.HIGH, GPIO.LOW),
                    (GPIO.LOW, GPIO.LOW)
                ]
                self._set_motors(states, 65)
            else:
                # Stop on white indicator line
                time.sleep(0.5)
                print("[NAV] Stop line detected.")
                self.stop()
                time.sleep(1)
                return

    def step_forward(self, duration=0.2, speed=60):
        states = [(GPIO.HIGH, GPIO.LOW)] * 4
        self._set_motors(states, speed)
        time.sleep(duration)
        self.stop()
        time.sleep(0.5)

    def cleanup(self):
        self.stop()
        for pwm in self.pwms:
            pwm.stop()