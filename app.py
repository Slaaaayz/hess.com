from app import create_app
from app.services.honeypot import HoneypotService
import threading

app = create_app()
honeypot = HoneypotService()

def run_honeypot():
    with app.app_context():
        honeypot.start()

if __name__ == '__main__':
    # Démarrer le honeypot dans un thread séparé
    honeypot_thread = threading.Thread(target=run_honeypot)
    honeypot_thread.daemon = True
    honeypot_thread.start()
    
    # Démarrer l'application Flask
    app.run(host=app.config['HONEYPOT_HOST'], 
            port=app.config['HONEYPOT_PORT'],
            ssl_context=(app.config['SSL_CERT_PATH'], 
                        app.config['SSL_KEY_PATH'])) 