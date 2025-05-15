import cv2
import numpy as np
from ChessBotApi.utils.fen_builder import split_board, analyze_square, classify_square, generate_fen_from_matrix

# Définition des constantes pour l'échiquier
files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
ranks = ['1', '2', '3', '4', '5', '6', '7', '8']

def compare_images(img1, img2):
    """Compare deux images et retourne leur similarité (0 à 1)"""
    if img1 is None or img2 is None:
        return 0.0
    
    # S'assurer que les images ont la même taille
    img1 = cv2.resize(img1, (100, 100))
    img2 = cv2.resize(img2, (100, 100))
    
    # Calculer la différence absolue
    diff = cv2.absdiff(img1, img2)
    
    # Calculer la similarité (1 - moyenne des différences normalisée)
    similarity = 1 - (np.mean(diff) / 255.0)
    return similarity

print("Début du test...")
image = cv2.imread("./test/image.png")
if image is None:
    print("ERREUR: L'image n'a pas pu être chargée. Vérifiez le chemin: ./test/image.png")
    exit()

print("Image chargée avec succès")
grid = split_board(image)
if grid is None:
    print("ERREUR: Impossible de diviser l'échiquier")
    exit()

print("Échiquier divisé avec succès")

# Création de la matrice des pièces
print("\nMatrice des pièces détectées:")
print("    a    b    c    d    e    f    g    h")
print("  ───────────────────────────────────────")

pieces_matrix = []
for rank in reversed(ranks):
    row_pieces = []
    for file in files:
        square_name = f"{file}{rank}"
        square = analyze_square(grid, square_name)
        if square is None:
            row_pieces.append("ERR")
            continue
        
        results = classify_square(square, "./ChessBotApi/templates")
        if not results:
            row_pieces.append("NUL")
            continue
            
        # Prendre la pièce avec le meilleur score
        best_piece = results[0][0]
        row_pieces.append(best_piece)
    
    pieces_matrix.append(row_pieces)

# Affichage de la matrice des pièces
for i, row in enumerate(pieces_matrix):
    print(f"{8-i} │", end=" ")
    for piece in row:
        print(f"{piece:4}", end=" ")
    print(f"│ {8-i}")
print("  ───────────────────────────────────────")
print("    a    b    c    d    e    f    g    h")

# Générer et afficher le FEN
fen = generate_fen_from_matrix(pieces_matrix)
print("\nNotation FEN générée:")
print(fen)

print("\nLégende des pièces:")
print("ERR : Erreur d'analyse")
print("NUL : Aucune pièce détectée")

# Création de la matrice des résultats
print("\nAnalyse de toutes les cases de l'échiquier:")

# Stocker toutes les images des cases
squares_images = {}
for rank in ranks:
    for file in files:
        square_name = f"{file}{rank}"
        square = analyze_square(grid, square_name)
        if square is not None:
            squares_images[square_name] = square

# Créer une matrice de similarité
print("\nMatrice de similarité entre les cases:")
print("    a    b    c    d    e    f    g    h")
print("  ───────────────────────────────────────")

# Pour chaque case, comparer avec toutes les autres
for rank in reversed(ranks):
    print(f"{rank} │", end=" ")
    for file in files:
        current_square = f"{file}{rank}"
        if current_square not in squares_images:
            print(" ERR ", end=" ")
            continue
            
        # Trouver la case la plus similaire (différente de la case actuelle)
        best_similarity = 0
        best_match = None
        
        for other_square, other_img in squares_images.items():
            if other_square != current_square:
                similarity = compare_images(squares_images[current_square], other_img)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = other_square
        
        if best_match:
            # Afficher la case la plus similaire et son score
            print(f"{best_match}({best_similarity:.2f})", end=" ")
        else:
            print(" NUL ", end=" ")
    print(f"│ {rank}")

print("  ───────────────────────────────────────")
print("    a    b    c    d    e    f    g    h")

print("\nLégende:")
print("ERR : Erreur d'analyse")
print("NUL : Aucune comparaison possible")
print("Format : case_similaire(score)")

# Afficher quelques exemples de cases similaires
print("\nExemples de cases similaires:")
print("Appuyez sur 'q' pour quitter, ou une autre touche pour continuer...")

try:
    for rank in ['1', '8']:
        for file in ['a', 'h']:
            square = f"{file}{rank}"
            if square in squares_images:
                print(f"\nCase {square}:")
                # Afficher l'image
                display_size = (200, 200)
                display_img = cv2.resize(squares_images[square], display_size)
                cv2.imshow(f"Case {square}", display_img)
                
                # Attendre une touche, 'q' pour quitter
                key = cv2.waitKey(0) & 0xFF
                cv2.destroyAllWindows()
                if key == ord('q'):
                    print("\nAffichage des images interrompu par l'utilisateur.")
                    break
        if key == ord('q'):
            break
except KeyboardInterrupt:
    print("\nAffichage des images interrompu par l'utilisateur.")
finally:
    cv2.destroyAllWindows()  # S'assurer que toutes les fenêtres sont fermées
