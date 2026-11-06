"""
Edge vision pipeline: Camera capture, preprocessing, OCR and prescription parsing.
"""
import time
import csv
import cv2
import pytesseract
from picamera2 import Picamera2

class VisionPipeline:
    def __init__(self, output_img="PozaFacuta.jpg", csv_output="ocr_output.csv"):
        self.output_img = output_img
        self.csv_output = csv_output

    def capture_image(self):
        picam2 = Picamera2()
        config = picam2.create_still_configuration(
            main={"format": "RGB888", "size": (1280, 720)},
            controls={"AfMode": 2}
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(2)
        print("[VISION] Autofocus cycle triggered...")
        picam2.autofocus_cycle()
        time.sleep(2)

        frame = picam2.capture_array()
        picam2.stop()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(self.output_img, frame_bgr)
        return frame_bgr

    def enhance_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)
        blurred = cv2.GaussianBlur(gray_eq, (5, 5), 0)
        return cv2.addWeighted(gray_eq, 1.5, blurred, -0.5, 0)

    def process_and_ocr(self, img):
        if len(img.shape) == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 2))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 35))
        
        detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        detect_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        grid = cv2.add(detect_horizontal, detect_vertical)

        contours, _ = cv2.findContours(grid, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        results = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if 1600 > w > 100 and 500 > h > 40:
                cell = img[y:y+h, x:x+w]
                cell_gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if len(cell.shape) == 3 else cell.copy()
                _, cell_bin = cv2.threshold(cell_gray, 180, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                
                text = pytesseract.image_to_string(cell_bin, config="--psm 11")
                results.append(((x, y), text.strip()))

        # Save OCR text to CSV
        with open(self.csv_output, "w", newline="") as f:
            writer = csv.writer(f)
            for (pos, text) in sorted(results, key=lambda x: (x[0][1], x[0][0])):
                writer.writerow([text])

    def parse_medication(self):
        try:
            with open(self.csv_output, "r") as file:
                content = file.read().lower()

            if "paracetamol" in content:
                print("[OCR] Identified: Paracetamol")
                return "paracetamol"
            elif "nurofen" in content:
                print("[OCR] Identified: Nurofen")
                return "nurofen"
            elif "nurofen" not in content and any(k in content for k in ["varsta", "nume pacient", "timp"]):
                print("[OCR] Fallback Identified: Paracetamol")
                return "paracetamol"
            else:
                return "citire nereusita"
        except FileNotFoundError:
            return "citire nereusita"