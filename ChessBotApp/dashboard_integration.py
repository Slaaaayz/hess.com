#!/usr/bin/env python3
"""
Script d'intégration pour connecter ChessBotApp avec le Dashboard Web
Ce script modifie le main.py existant pour envoyer des données en temps réel au dashboard
"""

import requests
import json
import time
import threading
from datetime import datetime
import os
import sys

class DashboardAPI:
    def __init__(self, dashboard_url="http://localhost:5000"):
        self.dashboard_url = dashboard_url
        self.api_url = f"{dashboard_url}/api/dashboard"
        self.session = requests.Session()
        
    def send_bot_status(self, status_data):
        """Envoie le statut du bot au dashboard"""
        try:
            response = self.session.post(
                f"{self.api_url}/bot-status",
                json=status_data,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ Statut envoyé: {status_data}")
            else:
                print(f"❌ Erreur envoi statut: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur connexion dashboard: {e}")
    
    def send_log(self, log_type, message, details=None):
        """Envoie un log au dashboard"""
        log_data = {
            "id": str(time.time()) + str(hash(message)),
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "message": message,
            "details": details
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/logs",
                json=log_data,
                timeout=5
            )
            if response.status_code == 200:
                print(f"📝 Log envoyé: [{log_type}] {message}")
        except Exception as e:
            print(f"❌ Erreur envoi log: {e}")
    
    def send_move_executed(self, move, fen, score):
        """Envoie l'information d'un coup exécuté"""
        move_data = {
            "move": move,
            "fen": fen,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/move-executed",
                json=move_data,
                timeout=5
            )
            if response.status_code == 200:
                print(f"♟️ Coup envoyé: {move} (score: {score})")
        except Exception as e:
            print(f"❌ Erreur envoi coup: {e}")

class DashboardIntegration:
    def __init__(self):
        self.api = DashboardAPI()
        self.bot_running = False
        self.auto_play = False
        self.voice_enabled = False
        self.current_move = ""
        self.current_fen = ""
        self.current_score = 0
        self.games_played = 0
        self.win_rate = 0.0
        
        # Thread pour envoyer des mises à jour périodiques
        self.update_thread = None
        self.running = True
        
    def start_integration(self):
        """Démarre l'intégration avec le dashboard"""
        print("🚀 Démarrage de l'intégration dashboard...")
        self.api.send_log("info", "Dashboard integration started")
        
        # Démarrer le thread de mise à jour
        self.update_thread = threading.Thread(target=self._periodic_updates)
        self.update_thread.daemon = True
        self.update_thread.start()
        
    def stop_integration(self):
        """Arrête l'intégration"""
        print("🛑 Arrêt de l'intégration dashboard...")
        self.running = False
        self.api.send_log("info", "Dashboard integration stopped")
        
    def update_bot_status(self, **kwargs):
        """Met à jour le statut du bot"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        status_data = {
            "isRunning": self.bot_running,
            "autoPlay": self.auto_play,
            "voiceEnabled": self.voice_enabled,
            "currentMove": self.current_move,
            "currentFen": self.current_fen,
            "currentScore": self.current_score,
            "gamesPlayed": self.games_played,
            "winRate": self.win_rate,
            "lastActivity": datetime.now().isoformat()
        }
        
        self.api.send_bot_status(status_data)
    
    def log_message(self, message, log_type="info", details=None):
        """Envoie un message de log"""
        self.api.send_log(log_type, message, details)
    
    def execute_move(self, move, fen, score):
        """Signale qu'un coup a été exécuté"""
        self.current_move = move
        self.current_fen = fen
        self.current_score = score
        
        self.api.send_move_executed(move, fen, score)
        self.update_bot_status()
    
    def _periodic_updates(self):
        """Thread qui envoie des mises à jour périodiques"""
        while self.running:
            try:
                # Envoyer le statut actuel
                self.update_bot_status()
                
                # Attendre 5 secondes avant la prochaine mise à jour
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Erreur dans periodic_updates: {e}")
                time.sleep(10)

# Instance globale pour l'intégration
dashboard_integration = DashboardIntegration()

def patch_main_py():
    """
    Fonction pour patcher le main.py existant avec l'intégration dashboard
    Cette fonction ajoute les appels API nécessaires
    """
    
    main_py_path = "main.py"
    if not os.path.exists(main_py_path):
        print("❌ main.py non trouvé dans le répertoire actuel")
        return False
    
    # Lire le fichier existant
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter l'import en haut du fichier
    import_line = "from dashboard_integration import dashboard_integration"
    if import_line not in content:
        # Trouver la fin des imports
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
        
        lines.insert(insert_index, import_line)
        content = '\n'.join(lines)
    
    # Patcher les méthodes importantes
    patches = [
        # Patch pour le démarrage du bot
        ('self.driver = self.get_driver()', 
         'self.driver = self.get_driver()\n        dashboard_integration.start_integration()\n        dashboard_integration.update_bot_status(bot_running=True)'),
        
        # Patch pour l'arrêt du bot
        ('self.driver.quit()', 
         'self.driver.quit()\n        dashboard_integration.update_bot_status(bot_running=False)\n        dashboard_integration.stop_integration()'),
        
        # Patch pour les logs
        ('print(f"Erreur lors de l\'exécution du coup (drag & drop): {e}")', 
         'print(f"Erreur lors de l\'exécution du coup (drag & drop): {e}")\n        dashboard_integration.log_message(f"Erreur exécution coup: {e}", "error")'),
        
        # Patch pour les mouvements réussis
        ('print(f"Drag & drop de {from_square} vers {to_square} effectué.")', 
         'print(f"Drag & drop de {from_square} vers {to_square} effectué.")\n        dashboard_integration.log_message(f"Coup exécuté: {move}", "success")'),
    ]
    
    for old, new in patches:
        if old in content and new not in content:
            content = content.replace(old, new)
    
    # Sauvegarder le fichier modifié
    backup_path = "main_backup.py"
    if not os.path.exists(backup_path):
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup créé: {backup_path}")
    
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ main.py patché avec succès pour l'intégration dashboard")
    return True

def create_dashboard_server():
    """Crée un serveur simple pour recevoir les données du bot"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                print(f"📨 Données reçues: {data}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
                
            except Exception as e:
                print(f"❌ Erreur traitement requête: {e}")
                self.send_response(500)
                self.end_headers()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
    
    server = HTTPServer(('localhost', 5000), DashboardHandler)
    print("🌐 Serveur dashboard démarré sur http://localhost:5000")
    return server

def main():
    """Fonction principale pour tester l'intégration"""
    print("🔧 Configuration de l'intégration ChessBot Dashboard")
    print("=" * 60)
    
    # Option 1: Patcher le main.py existant
    if len(sys.argv) > 1 and sys.argv[1] == "patch":
        success = patch_main_py()
        if success:
            print("\n✅ Installation terminée!")
            print("Vous pouvez maintenant lancer votre bot normalement.")
            print("Les données seront automatiquement envoyées au dashboard.")
        return
    
    # Option 2: Tester l'intégration
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 Test de l'intégration...")
        
        # Démarrer l'intégration
        dashboard_integration.start_integration()
        
        # Simuler quelques actions
        time.sleep(2)
        dashboard_integration.update_bot_status(bot_running=True)
        
        time.sleep(1)
        dashboard_integration.log_message("Test de connexion", "info")
        
        time.sleep(1)
        dashboard_integration.execute_move("e2e4", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", 25)
        
        time.sleep(1)
        dashboard_integration.log_message("Test terminé avec succès", "success")
        
        time.sleep(2)
        dashboard_integration.stop_integration()
        
        print("✅ Test terminé!")
        return
    
    # Option 3: Serveur dashboard simple
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = create_dashboard_server()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Serveur arrêté")
            server.shutdown()
        return
    
    # Usage
    print("Usage:")
    print("  python dashboard_integration.py patch   - Patcher main.py pour l'intégration")
    print("  python dashboard_integration.py test    - Tester l'intégration")
    print("  python dashboard_integration.py server  - Démarrer un serveur de test")

if __name__ == "__main__":
    main() 