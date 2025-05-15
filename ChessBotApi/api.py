from flask import Flask, request, jsonify
import cv2, numpy as np, os, base64, subprocess, time

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


def best_move_from_stockfish(fen, depth=20):
    p = subprocess.Popen(
        ["docker", "exec", "-i", "stockfish-engine", "stockfish"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    def send(cmd):
        p.stdin.write(cmd + "\n")
        p.stdin.flush()

    send("uci")
    while True:
        if p.stdout.readline().strip() == "uciok":
            break
    send("isready")
    while True:
        if p.stdout.readline().strip() == "readyok":
            break
    send(f"position fen {fen}")
    send(f"go depth {depth}")

    best = None
    while True:
        line = p.stdout.readline().strip()
        if line.startswith("bestmove"):
            best = line.split()[1]
            break

    send("quit")
    p.terminate()

    if best is None:
        raise RuntimeError("bestmove not found")

    return best


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        img = None
        if "image" in request.files:
            f = request.files["image"]
            if f.filename and allowed_file(f.filename):
                img = cv2.imdecode(
                    np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR
                )
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
        return jsonify({"best_move": move, "status": "success"})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
