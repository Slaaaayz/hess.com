# -*- coding: utf-8 -*-
import chess
import chess.engine
import os
import time

FEN_FILE = "fen.txt"  # Le fichier contenant la FEN
STOCKFISH_PATH = "stockfish"  # Chemin vers l'exécutable Stockfish (ajuste si besoin)

last_mtime = None
print("🔄 Surveillance de fen.txt pour analyse Stockfish automatique. Ctrl+C pour arrêter.")
while True:
    if os.path.exists(FEN_FILE):
        mtime = os.path.getmtime(FEN_FILE)
        if mtime != last_mtime:
            with open(FEN_FILE, "r") as f:
                fen = f.read().strip()
            print(f"FEN lue : {fen}")
            board = chess.Board(fen)
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
                result = engine.analyse(board, chess.engine.Limit(time=1.0))
                best_move = result["pv"][0]
                score = result["score"].white()
                print(f"Meilleur coup : {best_move}")
                print(f"Évaluation : {score}")
            last_mtime = mtime
    time.sleep(1) 