from flask import Flask, request, jsonify
import cv2
import numpy as np
from ChessBotApi.utils.fen_builder import split_board, analyze_square, classify_square, generate_fen_from_matrix
import os
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
TEMPLATES_DIR = './ChessBotApi/templates'

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite à 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_data):
    """Traite l'image et retourne la notation FEN"""
    # Analyser l'échiquier
    grid = split_board(image_data)
    if grid is None:
        return None, "Impossible de diviser l'échiquier"
    
    # Créer la matrice des pièces
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    pieces_matrix = []
    
    for rank in reversed(ranks):
        row_pieces = []
        for file in files:
            square_name = f"{file}{rank}"
            square = analyze_square(grid, square_name)
            if square is None:
                row_pieces.append("ERR")
                continue
            
            results = classify_square(square, TEMPLATES_DIR)
            if not results:
                row_pieces.append("NUL")
                continue
            
            # Prendre la pièce avec le meilleur score
            best_piece = results[0][0]
            row_pieces.append(best_piece)
        
        pieces_matrix.append(row_pieces)
    
    # Générer le FEN
    fen = generate_fen_from_matrix(pieces_matrix)
    return fen, None

@app.route('/analyze', methods=['POST'])
def analyze_chess_position():
    """
    Endpoint pour analyser une position d'échecs.
    Accepte une image en POST (fichier ou base64) et retourne la notation FEN.
    """
    try:
        image = None
        
        # Essayer de lire l'image depuis un fichier uploadé
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                file_bytes = file.read()
                nparr = np.frombuffer(file_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Si pas d'image uploadée, essayer de lire depuis le JSON (base64)
        if image is None and request.is_json:
            data = request.get_json()
            if 'image' in data:
                try:
                    # Décoder l'image base64
                    image_data = base64.b64decode(data['image'])
                    nparr = np.frombuffer(image_data, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception as e:
                    return jsonify({
                        'error': f'Erreur de décodage base64: {str(e)}',
                        'status': 'error'
                    }), 400
        
        if image is None:
            return jsonify({
                'error': 'Aucune image valide fournie',
                'status': 'error'
            }), 400
        
        # Traiter l'image
        fen, error = process_image(image)
        if error:
            return jsonify({
                'error': error,
                'status': 'error'
            }), 400
        
        return jsonify({
            'fen': fen,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de l\'analyse: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 