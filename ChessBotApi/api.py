from flask import Flask, request, jsonify
import cv2
import numpy as np
from ChessBotApi.utils.fen_builder import split_board, analyze_square, classify_square, generate_fen_from_matrix
import os
import base64
import subprocess
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
TEMPLATES_DIR = './ChessBotApi/templates'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_data):
    grid = split_board(image_data)
    if grid is None:
        return None, "Impossible de diviser l'échiquier"

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

            best_piece = results[0][0]
            row_pieces.append(best_piece)

        pieces_matrix.append(row_pieces)

    fen = generate_fen_from_matrix(pieces_matrix)
    return fen, None

def get_best_move(fen: str, time_limit: float = 1.0):
    try:
        cmd = ["docker", "exec", "-i", "stockfish-engine", "stockfish"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        time.sleep(0.1)

        commands = [
            "uci",
            "setoption name Skill Level value 20",
            f"position fen {fen}",
            f"go movetime {int(time_limit * 1000)}"
        ]

        for command in commands:
            process.stdin.write(command + "\n")
            process.stdin.flush()
            time.sleep(0.1)

        best_move = None
        start_time = time.time()

        while time.time() - start_time < time_limit + 1:
            line = process.stdout.readline().strip()
            if not line:
                continue

            if line.startswith("bestmove"):
                best_move = line.split()[1]
                break

        process.stdin.write("quit\n")
        process.stdin.flush()
        process.terminate()

        return best_move or "no_move_found"

    except Exception as e:
        return f"Erreur Stockfish: {str(e)}"

@app.route('/analyze', methods=['POST'])
def analyze_chess_position():
    try:
        image = None

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                file_bytes = file.read()
                nparr = np.frombuffer(file_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None and request.is_json:
            data = request.get_json()
            if 'image' in data:
                try:
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

        fen, error = process_image(image)
        if error:
            return jsonify({
                'error': error,
                'status': 'error'
            }), 400

        best_move = get_best_move(fen)
        return jsonify({
            'best_move': best_move,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de l\'analyse: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
