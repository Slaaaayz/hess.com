import threading
import socket
import paramiko
from flask import current_app
from app.models.database import db, Attack, Log, Attacker
from datetime import datetime

class HoneypotService:
    def __init__(self):
        self.services = {}
        self.running = False
        self.threads = []

    def start(self):
        """Démarre tous les services configurés"""
        if self.running:
            return

        self.running = True
        
        # Démarrer les services configurés
        if current_app.config['ENABLED_SERVICES'].get('ssh', False):
            self.start_ssh_service()
        
        if current_app.config['ENABLED_SERVICES'].get('http', False):
            self.start_http_service()
        
        if current_app.config['ENABLED_SERVICES'].get('ftp', False):
            self.start_ftp_service()

    def stop(self):
        """Arrête tous les services"""
        self.running = False
        for thread in self.threads:
            thread.join()

    def log_attack(self, source_ip, attack_type, severity, description, service):
        """Enregistre une attaque dans la base de données"""
        with current_app.app_context():
            # Vérifier si l'attaquant existe déjà
            attacker = Attacker.query.filter_by(ip_address=source_ip).first()
            if not attacker:
                attacker = Attacker(ip_address=source_ip)
                db.session.add(attacker)
                db.session.commit()

            # Créer l'enregistrement d'attaque
            attack = Attack(
                source_ip=source_ip,
                attack_type=attack_type,
                severity=severity,
                description=description,
                service=service,
                attacker_id=attacker.id
            )
            db.session.add(attack)

            # Créer le log associé
            log = Log(
                level='WARNING',
                message=f"Attaque détectée: {attack_type} depuis {source_ip}",
                source=service,
                attack=attack
            )
            db.session.add(log)
            db.session.commit()

    def start_ssh_service(self):
        """Démarre le service SSH"""
        class SSHServer(paramiko.ServerInterface):
            def __init__(self, honeypot_service):
                self.honeypot_service = honeypot_service

            def check_auth_password(self, username, password):
                client_ip = self.transport.getpeername()[0]
                self.honeypot_service.log_attack(
                    source_ip=client_ip,
                    attack_type='SSH_BRUTE_FORCE',
                    severity=3,
                    description=f'Tentative de connexion SSH avec {username}:{password}',
                    service='ssh'
                )
                return paramiko.AUTH_FAILED

            def get_allowed_auths(self, username):
                return 'password'

        def ssh_handler():
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind(('0.0.0.0', 2222))
                server_socket.listen(5)

                while self.running:
                    try:
                        client, addr = server_socket.accept()
                        transport = paramiko.Transport(client)
                        transport.add_server_key(paramiko.RSAKey.generate(2048))
                        transport.start_server(server=SSHServer(self))
                    except Exception as e:
                        print(f"Erreur SSH: {str(e)}")
                        continue

            except Exception as e:
                print(f"Erreur serveur SSH: {str(e)}")
            finally:
                server_socket.close()

        thread = threading.Thread(target=ssh_handler)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)

    def start_http_service(self):
        """Démarre le service HTTP"""
        def http_handler():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', 8080))
            server.listen(5)
            
            while self.running:
                try:
                    client, addr = server.accept()
                    data = client.recv(1024)
                    
                    if data:
                        self.log_attack(
                            source_ip=addr[0],
                            attack_type='HTTP_PROBE',
                            severity=2,
                            description=f'Requête HTTP: {data.decode()[:100]}',
                            service='http'
                        )
                    
                    # Réponse factice
                    response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Welcome</body></html>'
                    client.send(response)
                    client.close()
                except Exception as e:
                    continue

        thread = threading.Thread(target=http_handler)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)

    def start_ftp_service(self):
        """Démarre le service FTP"""
        def ftp_handler():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', 2121))
            server.listen(5)
            
            while self.running:
                try:
                    client, addr = server.accept()
                    client.send(b'220 Welcome to FTP Server\r\n')
                    
                    while True:
                        data = client.recv(1024)
                        if not data:
                            break
                        
                        self.log_attack(
                            source_ip=addr[0],
                            attack_type='FTP_PROBE',
                            severity=2,
                            description=f'Commande FTP: {data.decode().strip()}',
                            service='ftp'
                        )
                        
                        client.send(b'530 Please login with USER and PASS\r\n')
                    
                    client.close()
                except Exception as e:
                    continue

        thread = threading.Thread(target=ftp_handler)
        thread.daemon = True
        thread.start()
        self.threads.append(thread) 