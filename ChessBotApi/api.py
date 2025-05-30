from flask import Flask, request, jsonify
import cv2, numpy as np, os, base64, sys
from stockfish import Stockfish
import atexit
import signal
import logging
import traceback
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Ajouter le répertoire parent au PYTHONPATH pour permettre les imports absolus
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3307)),
    'user': os.getenv('DB_USER', 'hess_user'),
    'password': os.getenv('DB_PASSWORD', 'hess_password'),
    'database': os.getenv('DB_NAME', 'hess_db')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return None

def verify_api_key(api_key):
    logger.info(f"Vérification de la clé API reçue: {api_key!r}")
    if not api_key:
        return False
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = "SELECT isActive FROM ApiKey WHERE keyValue = %s"
        cursor.execute(query, (api_key,))
        result = cursor.fetchone()
        logger.info(f"Résultat SQL pour la clé: {result}")
        return result and result[0]
    except Error as e:
        logger.error(f"Erreur lors de la vérification de la clé API: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Vérifier si Stockfish existe
if not os.path.exists(STOCKFISH_PATH):
    raise FileNotFoundError(f"Stockfish non trouvé à {STOCKFISH_PATH}. Veuillez définir la variable d'environnement STOCKFISH_PATH.")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Stockage global de l'instance Stockfish
stockfish_instance = None

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chessbot_api.log')
    ]
)
logger = logging.getLogger(__name__)

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
    try:
        logger.info("Processing chessboard image")
        grid = split_board(img)
        if grid is None:
            logger.error("Failed to split board")
            return None
            
        files = "abcdefgh"
        ranks = "12345678"
        matrix = []
        for r in reversed(ranks):
            row = []
            for f in files:
                sq = analyze_square(grid, f + r)
                if sq is None:
                    logger.error(f"Failed to analyze square {f}{r}")
                    row.append("ERR")
                else:
                    res = classify_square(sq, TEMPLATES_DIR)
                    piece = res[0][0] if res else "NUL"
                    row.append(piece)
                    if piece == "ERR":
                        logger.error(f"Failed to classify square {f}{r}")
            matrix.append(row)
        
        fen = generate_fen_from_matrix(matrix)
        logger.info(f"Generated FEN: {fen}")
        return fen
    except Exception as e:
        error_msg = f"Image processing error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return None


def best_move_from_stockfish(fen: str, skill_level=20, depth=15) -> tuple[str, float]:
    try:
        logger.info(f"Calculating best move for FEN: {fen}")
        logger.info(f"Parameters - Skill: {skill_level}, Depth: {depth}")
        
        stockfish = get_stockfish()
        stockfish.set_skill_level(skill_level)
        stockfish.set_fen_position(fen)
        stockfish.set_depth(depth)
        
        move = stockfish.get_best_move_time(1000)  # 1000 ms de calcul
        score = stockfish.get_evaluation()['value']
        
        logger.info(f"Best move found: {move} with score: {score/100:.2f}")
        return move, score
    except Exception as e:
        error_msg = f"Stockfish error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        cleanup_stockfish()  # Réinitialiser Stockfish en cas d'erreur
        raise RuntimeError(error_msg)


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        logger.info("Received analyze request")
        
        # Vérification de la clé API
        api_key = request.headers.get('X-API-Key')
        if not verify_api_key(api_key):
            return jsonify({
                "error": "invalid_api_key",
                "status": "error",
                "details": "Invalid or missing API key"
            }), 401
        
        img = None
        
        # Log request details
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        if "image" in request.files:
            f = request.files["image"]
            if f.filename and allowed_file(f.filename):
                logger.info(f"Processing uploaded file: {f.filename}")
                img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        elif request.is_json:
            logger.info("Processing JSON request")
            data = request.get_json()
            if "image" in data:
                img = cv2.imdecode(
                    np.frombuffer(base64.b64decode(data["image"]), np.uint8),
                    cv2.IMREAD_COLOR,
                )

        if img is None:
            logger.error("No valid image found in request")
            return jsonify({
                "error": "no image",
                "status": "error",
                "details": "No valid image was provided in the request"
            }), 400

        # Récupérer les paramètres de configuration
        skill_level = int(request.args.get('skill_level', 20))
        depth = int(request.args.get('depth', 15))
        logger.info(f"Analysis parameters - Skill: {skill_level}, Depth: {depth}")

        fen = process_image(img)
        if fen is None:
            logger.error("Failed to process image into FEN")
            return jsonify({
                "error": "split error",
                "status": "error",
                "details": "Failed to process the chessboard image"
            }), 400

        try:
            move, score = best_move_from_stockfish(fen, skill_level, depth)
            response = {
                "fen": fen,
                "best_move": move,
                "score": score,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"Analysis successful: {response}")
            return jsonify(response)
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                "error": str(e),
                "status": "error",
                "details": error_msg,
                "timestamp": datetime.now().isoformat()
            }), 500

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            "error": str(e),
            "status": "error",
            "details": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/user_settings", methods=["GET"])
def get_user_settings():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({"error": "missing_api_key"}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "db_connection_failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        # 1. Trouver le userId associé à la clé
        cursor.execute("SELECT userId FROM ApiKey WHERE keyValue = %s AND isActive = 1", (api_key,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "invalid_api_key"}), 401
        user_id = row["userId"]

        # 2. Récupérer les settings
        cursor.execute("SELECT * FROM UserSettings WHERE userId = %s", (user_id,))
        settings = cursor.fetchone()
        if not settings:
            return jsonify({"error": "no_settings_found"}), 404

        return jsonify({"settings": settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/user_settings", methods=["POST"])
def update_user_settings():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({"error": "missing_api_key"}), 400

    data = request.json or {}
    skill_level = data.get("skillLevel")
    search_depth = data.get("searchDepth")

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "db_connection_failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT userId FROM ApiKey WHERE keyValue = %s AND isActive = 1", (api_key,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "invalid_api_key"}), 401
        user_id = row["userId"]

        # Mettre à jour les settings
        cursor.execute(
            "UPDATE UserSettings SET skillLevel = %s, searchDepth = %s, updatedAt = NOW() WHERE userId = %s",
            (skill_level, search_depth, user_id)
        )
        connection.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    # Désactiver le mode debug en production
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5001)