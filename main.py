import subprocess

p1 = subprocess.Popen(["python3", "capture_chessboard.py"])
p2 = subprocess.Popen(["python3", "split_chessboard.py"])
p3 = subprocess.Popen(["python3", "image_to_fen_template.py"])
p4 = subprocess.Popen(["python3", "fen_to_bestmove.py"])

try:
    p1.wait()
    p2.wait()
    p3.wait()
    p4.wait()
except KeyboardInterrupt:
    print("Arrêt demandé, fermeture des processus…")
    p1.terminate()
    p2.terminate()
    p3.terminate()
    p4.terminate()