import cv2
import os
import numpy as np

FILES = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

def split_board(image):
    """
    Découpe l'image en 64 cases d'échecs.
    L'image est rognée à 816x816 pixels en commençant à 46 pixels du bord gauche.
    """
    # Dimensions cibles
    target_size = 816
    left_offset = 44  # Décalage à partir du bord gauche
    
    # Obtenir les dimensions actuelles
    h, w = image.shape[:2]
    
    # Calculer les coordonnées pour le rognage
    start_x = left_offset
    start_y = max(0, (h - target_size) // 2)  # Toujours centrer verticalement
    
    # S'assurer que nous ne dépassons pas les limites de l'image
    end_x = min(w, start_x + target_size)
    end_y = min(h, start_y + target_size)
    
    # Vérifier si nous avons assez d'espace horizontal
    if end_x - start_x < target_size:
        print("⚠️ Attention: L'image n'est pas assez large pour le rognage demandé")
        # Ajuster pour prendre le maximum possible
        start_x = max(0, w - target_size)
        end_x = w
    
    # Rogner l'image
    cropped_image = image[start_y:end_y, start_x:end_x]
    
    # Redimensionner si nécessaire (au cas où l'image était plus petite)
    if cropped_image.shape[0] != target_size or cropped_image.shape[1] != target_size:
        print("⚠️ Redimensionnement de l'image à", target_size, "x", target_size)
        cropped_image = cv2.resize(cropped_image, (target_size, target_size))
    
    # Diviser en cases de 102x102 pixels (816/8 = 102)
    square_size = target_size // 8
    board_grid = []
    
    for row in range(8):
        line = []
        for col in range(8):
            y1 = row * square_size
            x1 = col * square_size
            square = cropped_image[y1:y1 + square_size, x1:x1 + square_size]
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
                total_score = (val_gray * 0.8) + (val_edge * 0.4)

                # Réduire le score des cases vides
                piece_name = file.replace('.png', '')
                if piece_name in ['blackcase', 'whitecase']:
                    total_score = total_score / 1.25

                if total_score >= threshold:
                    results.append((piece_name, total_score))
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

def generate_fen_from_matrix(pieces_matrix):
    """
    Génère la notation FEN à partir de la matrice des pièces.
    Gère les noms de fichiers spécifiques (WhiteQueen1, BlackRock2, blackcase, whitecase)
    """
    fen_parts = []
    
    # Mapping des noms de fichiers vers la notation FEN
    def piece_to_fen(piece_name):
        if piece_name in ['blackcase', 'whitecase']:
            return '1'  # Case vide
        
        # Extraire la couleur et le type de pièce
        if piece_name.startswith('White'):
            color = 'W'
            piece_type = piece_name[5:]  # Enlève 'White'
        elif piece_name.startswith('Black'):
            color = 'B'
            piece_type = piece_name[5:]  # Enlève 'Black'
        else:
            return '1'  # Cas par défaut
        
        # Enlever les numéros à la fin (ex: Queen1 -> Queen)
        piece_type = ''.join(c for c in piece_type if not c.isdigit())
        
        # Mapping des types de pièces
        piece_map = {
            'Pawn': 'P',
            'Queen': 'Q',
            'King': 'K',
            'Rock': 'R',  # Gestion de l'orthographe alternative
            'Rook': 'R',
            'Bishop': 'B',
            'Knight': 'N'
        }
        
        # Convertir en notation FEN
        fen_piece = piece_map.get(piece_type, '1')
        return fen_piece if color == 'W' else fen_piece.lower()
    
    # Pour chaque rangée (de haut en bas, comme dans FEN)
    for row in pieces_matrix:
        fen_row = []
        empty_count = 0
        
        for piece in row:
            if piece == 'ERR':
                empty_count += 1
                continue
                
            fen_piece = piece_to_fen(piece)
            
            if fen_piece == '1':
                empty_count += 1
            else:
                # Si on a accumulé des cases vides, les ajouter
                if empty_count > 0:
                    fen_row.append(str(empty_count))
                    empty_count = 0
                fen_row.append(fen_piece)
        
        # Ajouter les cases vides restantes
        if empty_count > 0:
            fen_row.append(str(empty_count))
        
        fen_parts.append(''.join(fen_row))
    
    # Assembler le FEN complet
    # Pour l'instant, on met des valeurs par défaut pour les autres parties du FEN
    fen = '/'.join(fen_parts) + ' w KQkq - 0 1'
    
    return fen
