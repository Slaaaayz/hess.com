import cv2
import os
import numpy as np

FILES = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

def split_board(image):
    h, w = image.shape[:2]
    square_h = h // 8
    square_w = w // 8

    board_grid = []
    for row in range(8):
        line = []
        for col in range(8):
            y1 = row * square_h
            x1 = col * square_w
            square = image[y1:y1 + square_h, x1:x1 + square_w]
            line.append(square)
        board_grid.append(line)
    return board_grid

def analyze_square(board_grid, square_name):
    if len(square_name) != 2:
        raise ValueError("Nom de case invalide (ex: 'e4')")

    file, rank = square_name[0], square_name[1]
    if file not in FILES or not rank.isdigit() or not (1 <= int(rank) <= 8):
        raise ValueError("Case en dehors de l'échiquier")

    col = FILES[file]
    row = 8 - int(rank)  # rangée 8 en haut

    return board_grid[row][col]

def preprocess_gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)

def preprocess_binary(img):
    gray = preprocess_gray(img)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    return cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

def preprocess_edges(img):
    gray = preprocess_gray(img)
    return cv2.Canny(gray, 50, 150)

def compare_templates(source, template, method=cv2.TM_CCOEFF_NORMED):
    resized = cv2.resize(source, template.shape[::-1])
    result = cv2.matchTemplate(resized, template, method)
    _, val, _, _ = cv2.minMaxLoc(result)
    return val

def classify_square(square_img, templates_dir, threshold=0):
    print(f"\n🧩 Classification de la case...")

    # Prétraitement de la case
    square_gray = preprocess_gray(square_img)
    square_binary = preprocess_binary(square_img)
    square_edges = preprocess_edges(square_img)

    results = []

    for root, _, files in os.walk(templates_dir):
        for file in files:
            if not file.lower().endswith('.png'):
                continue

            path = os.path.join(root, file)
            template_img = cv2.imread(path, cv2.IMREAD_COLOR)
            if template_img is None:
                print(f"⚠️ Erreur de lecture : {file}")
                continue

            try:
                template_gray = preprocess_gray(template_img)
                template_binary = preprocess_binary(template_img)
                template_edges = preprocess_edges(template_img)

                # Comparaisons multiples
                val_gray = compare_templates(square_gray, template_gray)
                val_bin = compare_templates(square_binary, template_binary)
                val_edge = compare_templates(square_edges, template_edges)

                # Moyenne pondérée (tu peux ajuster les poids)
                total_score = (val_gray * 0.8)  + (val_edge * 0.4)

                if total_score >= threshold:
                    results.append((file.replace('.png', ''), total_score))
            except Exception as e:
                print(f"❌ Erreur sur {file}: {str(e)}")
                continue

    results.sort(key=lambda x: x[1], reverse=True)

    if results:
        print(f"\n🏆 Pièce la plus probable : {results[0][0]} (score: {results[0][1]:.3f})")
    else:
        print("\n❓ Aucune pièce reconnue (score insuffisant)")

    print("\n📋 Classement des correspondances :")
    for name, score in results:
        print(f"  {name}: {score:.3f}")

    return results
