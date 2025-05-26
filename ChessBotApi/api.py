from flask import Flask, request, jsonify
import cv2, numpy as np, os, base64
from stockfish import Stockfish
import atexit
import signal

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
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "C:/Users/trist/Desktop/stockfish/stockfish-windows-x86-64-avx2.exe")

# Vérifier si Stockfish existe
if not os.path.exists(STOCKFISH_PATH):
    raise FileNotFoundError(f"Stockfish non trouvé à {STOCKFISH_PATH}. Veuillez définir la variable d'environnement STOCKFISH_PATH.")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Stockage global de l'instance Stockfish
stockfish_instance = None

def get_stockfish():
    global stockfish_instance
    if stockfish_instance is None:
        try:
            stockfish_instance = Stockfish(path=STOCKFISH_PATH)
            stockfish_instance.set_skill_level(20)
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'initialisation de Stockfish: {str(e)}")
    return stockfish_instance

def cleanup_stockfish():
    global stockfish_instance
    if stockfish_instance is not None:
        try:
            stockfish_instance.quit()
        except:
            pass
        stockfish_instance = None

# Enregistrer la fonction de nettoyage
atexit.register(cleanup_stockfish)

def signal_handler(signum, frame):
    cleanup_stockfish()
    exit(0)

# Gérer les signaux de terminaison
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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


def best_move_from_stockfish(fen: str, skill_level=20, depth=15) -> tuple[str, float]:
    try:
        stockfish = get_stockfish()
        stockfish.set_skill_level(skill_level)
        stockfish.set_fen_position(fen)
        stockfish.set_depth(depth)
        move = stockfish.get_best_move_time(1000)  # 1000 ms de calcul
        score = stockfish.get_evaluation()['value']
        return move, score
    except Exception as e:
        cleanup_stockfish()  # Réinitialiser Stockfish en cas d'erreur
        raise RuntimeError(f"Erreur Stockfish: {str(e)}")


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

        # Récupérer les paramètres de configuration
        skill_level = int(request.args.get('skill_level', 20))
        depth = int(request.args.get('depth', 15))

        fen = process_image(img)
        if fen is None:
            return jsonify({"error": "split error", "status": "error"}), 400

        move, score = best_move_from_stockfish(fen, skill_level, depth)
        return jsonify({
            "fen": fen,
            "best_move": move,
            "score": score,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


if __name__ == "__main__":
    # Désactiver le mode debug en production
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
