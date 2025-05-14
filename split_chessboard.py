# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import time

IMAGE_PATH = "chessboard_capture.png"
OUTPUT_DIR = "cases"

# Coordonnées des cases (notation échiquéenne)
files = ['a','b','c','d','e','f','g','h']
ranks = ['1','2','3','4','5','6','7','8']

def split_and_save():
    # Charger l'image
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"Erreur : impossible de charger {IMAGE_PATH}")
        return
    height, width = img.shape[:2]
    case_h = height // 8
    case_w = width // 8
    # Découper et sauvegarder chaque case
    for i, rank in enumerate(reversed(ranks)):
        for j, file in enumerate(files):
            y1 = i * case_h
            y2 = (i + 1) * case_h
            x1 = j * case_w
            x2 = (j + 1) * case_w
            case_img = img[y1:y2, x1:x2]
            case_name = f"{OUTPUT_DIR}/case_{file}{rank}.png"
            cv2.imwrite(case_name, case_img)
    print(f"✅ Découpage effectué à {time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    last_mtime = None
    print("🔄 Surveillance de chessboard_capture.png. Ctrl+C pour arrêter.")
    while True:
        if os.path.exists(IMAGE_PATH):
            mtime = os.path.getmtime(IMAGE_PATH)
            if mtime != last_mtime:
                split_and_save()
                last_mtime = mtime
        time.sleep(1) 