from flask import Flask, request, jsonify
import cv2
import numpy as np
from .fen_builder import image_to_fen
from .stockfish_client import get_best_moves

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    try:
        fen = image_to_fen(img)
        moves = get_best_moves(fen)
        return jsonify({'fen': fen, 'best_moves': moves})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    app.run(host="0.0.0.0", port=5000)
