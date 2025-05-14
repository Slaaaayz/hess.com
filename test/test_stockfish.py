import subprocess
import time

def send_command(process, command):
    """Envoie une commande à Stockfish et attend la réponse"""
    process.stdin.write(command + '\n')
    process.stdin.flush()
    time.sleep(0.1)  # Petit délai pour laisser Stockfish répondre

def main():
    # Démarrer Stockfish via Docker
    process = subprocess.Popen(
        ['docker', 'exec', '-i', 'stockfish-engine', 'stockfish'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    try:
        # Initialiser le protocole UCI
        send_command(process, 'uci')
        print("Initialisation du protocole UCI...")
        
        # Vérifier si le moteur est prêt
        send_command(process, 'isready')
        print("Vérification de la disponibilité du moteur...")
        
        # Définir la position initiale
        send_command(process, 'position startpos')
        print("Position initiale définie")
        
        # Demander une analyse de 5 secondes
        send_command(process, 'go movetime 5000')
        print("Analyse en cours...")
        
        # Lire la sortie pendant 5 secondes
        start_time = time.time()
        while time.time() - start_time < 5:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            time.sleep(0.1)

    finally:
        # Arrêter le moteur
        send_command(process, 'quit')
        process.terminate()

if __name__ == "__main__":
    main() 