import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///honeypot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration TLS/SSL
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', 'certs/server.crt')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', 'certs/server.key')

    # Configuration des services
    HONEYPOT_HOST = os.getenv('HONEYPOT_HOST', '0.0.0.0')
    HONEYPOT_PORT = int(os.getenv('HONEYPOT_PORT', 5000))
    
    # Services à simuler
    ENABLED_SERVICES = {
        'ssh': True,
        'http': True,
        'ftp': True
    }

    # Configuration de l'IA
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/attack_detector.pkl')
    TRAINING_INTERVAL = int(os.getenv('TRAINING_INTERVAL', 3600))  # en secondes

    # Configuration des logs
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 30))
    LOG_PATH = os.getenv('LOG_PATH', 'logs/')

    # Configuration de sécurité
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True 