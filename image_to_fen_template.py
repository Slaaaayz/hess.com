# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import time

CASES_DIR = "cases"
TEMPLATES_DIR = "templates"
PIECES = [
    ("wK", "K"), ("wQ", "Q"), ("wR", "R"), ("wB", "B"), ("wN", "N"), ("wP", "P"),
    ("bK", "k"), ("bQ", "q"), ("bR", "r"), ("bB", "b"), ("bN", "n"), ("bP", "p")
]
FILES = ['a','b','c','d','e','f','g','h']
RANKS = ['1','2','3','4','5','6','7','8']

# Demande à l'utilisateur qui doit jouer
TO_MOVE = input("Qui doit jouer ? (w pour blanc, b pour noir) : ").strip().lower()
if TO_MOVE not in ("w", "b"):
    print("Entrée invalide, utilisation de 'w' par défaut.")
    TO_MOVE = "w"

# Charge tous les templates dans un dict
TEMPLATES = {}
for code, _ in PIECES:
    path = os.path.join(TEMPLATES_DIR, f"{code}.png")
    if os.path.exists(path):
        TEMPLATES[code] = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    else:
        print(f"Template manquant : {path}")

# Fonction de matching simple

def match_piece(case_img):
    best_score = None
    best_piece = None
    for code, fen_letter in PIECES:
        template = TEMPLATES.get(code)
        if template is None:
            continue
        # Redimensionne le template à la taille de la case
        template_resized = cv2.resize(template, (case_img.shape[1], case_img.shape[0]))
        # Conversion en niveaux de gris
        case_gray = cv2.cvtColor(case_img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template_resized, cv2.COLOR_BGR2GRAY)
        # Matching
        res = cv2.matchTemplate(case_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if (best_score is None) or (max_val > best_score):
            best_score = max_val
            best_piece = fen_letter
    # Seuil à ajuster selon la qualité des templates
    if best_score and best_score > 0.6:
        return best_piece
    else:
        return None

WATCHED_CASE = os.path.join(CASES_DIR, "case_e1.png")
last_mtime = None
print("🔄 Surveillance des cases pour génération automatique de la FEN. Ctrl+C pour arrêter.")
while True:
    if os.path.exists(WATCHED_CASE):
        mtime = os.path.getmtime(WATCHED_CASE)
        if mtime != last_mtime:
            # --- Génération FEN ---
            fen_rows = []
            for i, rank in enumerate(reversed(RANKS)):
                row = ""
                empty = 0
                for j, file in enumerate(FILES):
                    case_path = f"{CASES_DIR}/case_{file}{rank}.png"
                    case_img = cv2.imread(case_path)
                    if case_img is None:
                        print(f"Case manquante : {case_path}")
                        row += "1"
                        continue
                    piece = match_piece(case_img)
                    if piece:
                        if empty > 0:
                            row += str(empty)
                            empty = 0
                        row += piece
                    else:
                        empty += 1
                if empty > 0:
                    row += str(empty)
                fen_rows.append(row)
            fen = "/".join(fen_rows) + f" {TO_MOVE} KQkq - 0 1"
            print(f"FEN générée : {fen}")
            with open("fen.txt", "w") as f:
                f.write(fen + "\n")
            print("FEN enregistrée dans fen.txt")
            last_mtime = mtime
    time.sleep(1) 