from flask import Flask, request, jsonify
import cv2, numpy as np, os, base64
from stockfish import Stockfish

from ChessBotApi.utils.fen_builder import (
    split_board,
    analyze_square,
    classify_square,
    generate_fen_from_matrix,
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
TEMPLATES_DIR = "./ChessBotApi/templates"
STOCKFISH_PATH = "/usr/games/stockfish"  # 🔁 adapte ce chemin à ton exécutable

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(img):
    grid = split_board(img)
    if grid is None:
        return None
    files = "abcdefgh"
    ranks = "12345678"
    matrix = []
    for r in reversed(ranks):
        row = []
        for f in files:
            sq = analyze_square(grid, f + r)
            if sq is None:
                row.append("ERR")
            else:
                res = classify_square(sq, TEMPLATES_DIR)
                row.append(res[0][0] if res else "NUL")
        matrix.append(row)
    return generate_fen_from_matrix(matrix)


def best_move_from_stockfish(fen: str, skill_level=20, depth=15) -> str:
    stockfish = Stockfish(path=STOCKFISH_PATH)
    stockfish.set_skill_level(skill_level)
    stockfish.set_fen_position(fen)
    return stockfish.get_best_move_time(1000)  # 1000 ms de calcul


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        img = None
        if "image" in request.files:
            f = request.files["image"]
            if f.filename and allowed_file(f.filename):
                img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        elif request.is_json:
            data = request.get_json()
            if "image" in data:
                img = cv2.imdecode(
                    np.frombuffer(base64.b64decode(data["image"]), np.uint8),
                    cv2.IMREAD_COLOR,
                )

        if img is None:
            return jsonify({"error": "no image", "status": "error"}), 400

        fen = process_image(img)
        if fen is None:
            return jsonify({"error": "split error", "status": "error"}), 400

        move = best_move_from_stockfish(fen)
        return jsonify({
            "fen": fen,
            "best_move": move,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
