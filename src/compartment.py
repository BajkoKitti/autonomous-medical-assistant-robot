"""
Medicine compartment actuation, drawer sensor monitoring, and audio feedback.
"""
import time
import os
import pygame
import RPi.GPIO as GPIO
from config import SERVO_PINS, DRAWER_SENSOR_PINS, PWM_FREQ_SERVO

class CompartmentManager:
    def __init__(self):
        pygame.mixer.init()
        os.system("amixer sset 'Master' 100%")
        self.servo_pwms = []
        self._setup_hardware()

    def _setup_hardware(self):
        for pin in SERVO_PINS:
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, PWM_FREQ_SERVO)
            pwm.start(0)
            self.servo_pwms.append(pwm)

        for pin in DRAWER_SENSOR_PINS:
            GPIO.setup(pin, GPIO.IN)

    def play_audio(self, audio_file):
        if not os.path.exists(audio_file):
            print(f"[AUDIO] Warning: {audio_file} not found.")
            return
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        time.sleep(0.5)
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.stop()

    def set_angle(self, servo_idx, angle):
        duty = 2 + (angle / 18.0)
        self.servo_pwms[servo_idx].ChangeDutyCycle(duty)
        time.sleep(2)
        self.servo_pwms[servo_idx].ChangeDutyCycle(0)

    def calibrate_servos(self):
        for i in range(len(self.servo_pwms)):
            self.set_angle(i, 1)
            print(f"[SERVO] Calibrating compartment {i+1}. Press ENTER...")
            input()
            self.set_angle(i, 80)

    def deliver_medication(self, medication_name):
        servo_map = {
            "paracetamol": 0,
            "nurofen": 1
        }

        if medication_name not in servo_map:
            print(f"[DISPENSE] Unknown or unreadable medication: {medication_name}")
            return

        idx = servo_map[medication_name]
        print(f"[DISPENSE] Opening compartment for {medication_name}...")
        self.play_audio("SertarulSaDeschis.mp3")
        self.set_angle(idx, 1)

        # Wait up to 10 seconds for user pickup
        timeout = time.time() + 10
        item_taken = False

        while time.time() < timeout:
            if GPIO.input(DRAWER_SENSOR_PINS[idx]) == 0:
                print("[DISPENSE] Medicine successfully retrieved!")
                self.play_audio("MultumimCaAtiLuat.mp3")
                time.sleep(3)
                self.set_angle(idx, 80)
                item_taken = True
                return
            time.sleep(0.3)

        if not item_taken:
            print("[DISPENSE] Timeout expired. Closing compartment.")
            self.play_audio("NuVatiLuatMed.mp3")
            self.set_angle(idx, 80)

    def cleanup(self):
        for pwm in self.servo_pwms:
            pwm.stop()