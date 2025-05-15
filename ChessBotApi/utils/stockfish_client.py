import docker
import chess
import chess.engine
import time
from typing import Optional, Tuple

class StockfishClient:
    def __init__(self, container_name: str = "stockfish", skill_level: int = 20):
        """
        Initialise le client Stockfish.
        
        Args:
            container_name: Nom du conteneur Docker Stockfish
            skill_level: Niveau de jeu (0-20)
        """
        self.container_name = container_name
        self.skill_level = skill_level
        self.client = docker.from_env()
        self.engine = None
        self._connect()

    def _connect(self):
        """Établit la connexion avec le moteur Stockfish via Docker."""
        try:
            # Vérifier si le conteneur existe
            container = self.client.containers.get(self.container_name)
            
            # Créer le transport pour communiquer avec Stockfish
            transport = chess.engine.SimpleTransport(
                lambda: container.exec_run("stockfish", stdin=True, tty=True)
            )
            
            # Initialiser le moteur
            self.engine = chess.engine.SimpleEngine(transport)
            
            # Configurer le niveau de jeu
            self.engine.configure({"Skill Level": self.skill_level})
            
        except docker.errors.NotFound:
            raise Exception(f"Le conteneur {self.container_name} n'existe pas. "
                          "Assurez-vous que le conteneur Stockfish est en cours d'exécution.")
        except Exception as e:
            raise Exception(f"Erreur lors de la connexion à Stockfish: {str(e)}")

    def get_best_move(self, fen: str, time_limit: float = 1.0) -> Tuple[str, float]:
        """
        Obtient le meilleur coup pour une position FEN donnée.
        
        Args:
            fen: Position FEN
            time_limit: Temps de réflexion en secondes
            
        Returns:
            Tuple contenant le meilleur coup en notation UCI et son score
        """
        if not self.engine:
            self._connect()
            
        try:
            # Créer un objet Board à partir du FEN
            board = chess.Board(fen)
            
            # Obtenir le meilleur coup
            result = self.engine.play(
                board,
                chess.engine.Limit(time=time_limit),
                info=chess.engine.INFO_SCORE
            )
            
            # Extraire le coup et le score
            best_move = result.move.uci()
            score = result.info.get("score", None)
            
            # Convertir le score en nombre
            if score:
                if score.is_mate():
                    score_value = float("inf") if score.mate() > 0 else float("-inf")
                else:
                    score_value = score.score() / 100.0  # Convertir en pions
            else:
                score_value = 0.0
                
            return best_move, score_value
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse de la position: {str(e)}")

    def close(self):
        """Ferme la connexion avec le moteur."""
        if self.engine:
            self.engine.quit()
            self.engine = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
