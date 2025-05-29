import subprocess
import sys
import time

    def analyze_position(fen: str, time_limit: float = 1.0):
        """
        Analyse une position FEN avec Stockfish via Docker.
        
        Args:
            fen: Position FEN à analyser
            time_limit: Temps de réflexion en secondes
        """
        try:
            # Commande pour démarrer Stockfish dans le conteneur
            cmd = ["docker", "exec", "-i", "stockfish-engine", "stockfish"]
            
            print("Démarrage de Stockfish...")
            
            # Démarrer le processus Stockfish
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Attendre que Stockfish soit prêt
            time.sleep(0.1)
            
            # Configuration de base
            commands = [
                "uci",
                "setoption name Skill Level value 20",
                f"position fen {fen}",
                f"go movetime {int(time_limit * 1000)}"
            ]
            
            print("Envoi des commandes à Stockfish...")
            
            # Envoi des commandes
            for cmd in commands:
                print(f"Envoi: {cmd}")
                process.stdin.write(cmd + "\n")
                process.stdin.flush()
                time.sleep(0.1)
            
            print("Lecture de la sortie de Stockfish...")
            
            # Lecture de la sortie
            best_move = None
            score = None
            start_time = time.time()
            
            while time.time() - start_time < time_limit + 1:  # Attendre un peu plus que le time_limit
                line = process.stdout.readline().strip()
                if not line:
                    continue
                    
                print(f"Reçu: {line}")
                
                if line.startswith("bestmove"):
                    best_move = line.split()[1]
                    break
                elif "score cp" in line:
                    score = int(line.split("score cp")[1].split()[0])
                elif "score mate" in line:
                    mate = int(line.split("score mate")[1].split()[0])
                    score = f"mate {mate}"
            
            # Affichage des résultats
            print(f"\nPosition FEN: {fen}")
            print(f"Meilleur coup: {best_move}")
            
            if score:
                if isinstance(score, str) and score.startswith("mate"):
                    print(f"Mat en {score.split()[1]} coups")
                else:
                    print(f"Score: {score/100:+.2f} pions")
            
            # Fermeture propre
            print("Fermeture de Stockfish...")
            process.stdin.write("quit\n")
            process.stdin.flush()
            process.terminate()
            
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            if 'process' in locals():
                print("Sortie d'erreur de Stockfish:")
                print(process.stderr.read())

    if __name__ == "__main__":
        # Vérification des arguments
        if len(sys.argv) < 2:
            print("Usage: python test_stockfish.py <fen> [time_limit]")
            print("Exemple: python test_stockfish.py 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' 1.0")
            sys.exit(1)
        
        # Récupération des arguments
        fen = sys.argv[1]
        time_limit = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        
        # Analyse de la position
        analyze_position(fen, time_limit) 