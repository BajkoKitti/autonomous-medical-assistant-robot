"""
Autonomous Medical Assistant Robot - Main Orchestrator.
"""
import time
import RPi.GPIO as GPIO
from motor_control import MotorController
from compartment import CompartmentManager
from vision import VisionPipeline

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Initialize subsystems
    motors = MotorController()
    compartments = CompartmentManager()
    vision = VisionPipeline()

    try:
        # Initial greeting & user prompt
        compartments.play_audio("BunaZiua.mp3")
        time.sleep(1)
        compartments.play_audio("ApasaEnterSaMaDuc.mp3")
        input("[SYSTEM] Press ENTER to begin mission...")

        # Stage 1: Line follow to first checkpoint (Prescription scan)
        print("[STAGE 1] Navigating to medical chart checkpoint...")
        motors.line_follow()

        # Stage 2: Capture chart and extract prescription
        print("[STAGE 2] Capturing image and running OCR...")
        frame = vision.capture_image()
        enhanced = vision.enhance_image(frame)
        vision.process_and_ocr(enhanced)
        target_medication = vision.parse_medication()

        # Step off the line marker and follow line to patient delivery stop
        print("[STAGE 3] Advancing to delivery station...")
        motors.step_forward(duration=0.2)
        motors.line_follow()

        # Stage 4: Open compartment and dispense
        print(f"[STAGE 4] Dispensing medication: {target_medication}")
        time.sleep(1)
        compartments.deliver_medication(target_medication)

        print("[SYSTEM] Mission complete. Terminating.")

    except KeyboardInterrupt:
        print("\n[SYSTEM] Emergency stop requested by user.")
    finally:
        motors.cleanup()
        compartments.cleanup()
        GPIO.cleanup()
        print("[SYSTEM] Clean shutdown completed.")

if __name__ == "__main__":
    main()