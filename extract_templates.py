# -*- coding: utf-8 -*-
import os
import shutil

CASES_DIR = "cases"
TEMPLATES_DIR = "templates"

# Mapping case -> nom de template
TEMPLATE_MAP = {
    # Blancs
    "case_e1.png": "wK.png",
    "case_d1.png": "wQ.png",
    "case_a1.png": "wR.png",
    "case_h1.png": "wR2.png",  # Pour avoir deux tours
    "case_c1.png": "wB.png",
    "case_f1.png": "wB2.png",  # Pour avoir deux fous
    "case_b1.png": "wN.png",
    "case_g1.png": "wN2.png",  # Pour avoir deux cavaliers
    "case_a2.png": "wP.png",
    # Noirs
    "case_e8.png": "bK.png",
    "case_d8.png": "bQ.png",
    "case_a8.png": "bR.png",
    "case_h8.png": "bR2.png",
    "case_c8.png": "bB.png",
    "case_f8.png": "bB2.png",
    "case_b8.png": "bN.png",
    "case_g8.png": "bN2.png",
    "case_a7.png": "bP.png",
}

if __name__ == "__main__":
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    for src, dst in TEMPLATE_MAP.items():
        src_path = os.path.join(CASES_DIR, src)
        dst_path = os.path.join(TEMPLATES_DIR, dst)
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
            print(f"Copié {src_path} -> {dst_path}")
        else:
            print(f"Manquant : {src_path}")
    print("✅ Extraction des templates terminée. Pense à renommer les fichiers 'wR2', 'wB2', etc. si besoin.") 