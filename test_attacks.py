import requests
import socket
import time
from datetime import datetime

class HoneypotTester:
    def __init__(self, honeypot_ip, honeypot_port=5000):
        self.honeypot_ip = honeypot_ip
        self.honeypot_port = honeypot_port
        self.base_url = f"http://{honeypot_ip}:{honeypot_port}"

    def test_ssh_connection(self):
        """Test de connexion SSH"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.honeypot_ip, 22))
            if result == 0:
                print(f"[{datetime.now()}] Test SSH: Port 22 ouvert")
            else:
                print(f"[{datetime.now()}] Test SSH: Port 22 fermé")
            sock.close()
        except Exception as e:
            print(f"[{datetime.now()}] Erreur test SSH: {str(e)}")

    def test_http_injection(self):
        """Test d'injection SQL sur le formulaire de login"""
        try:
            payloads = [
                "admin' OR '1'='1",
                "admin' --",
                "admin' #",
                "admin'/*"
            ]
            
            for payload in payloads:
                response = requests.post(
                    f"{self.base_url}/login",
                    data={"username": payload, "password": "test"}
                )
                print(f"[{datetime.now()}] Test injection SQL avec payload: {payload}")
                print(f"Status code: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] Erreur test injection: {str(e)}")

    def test_xss(self):
        """Test de XSS"""
        try:
            payloads = [
                "<script>alert('test')</script>",
                "<img src=x onerror=alert('test')>",
                "<svg onload=alert('test')>"
            ]
            
            for payload in payloads:
                response = requests.get(
                    f"{self.base_url}/search",
                    params={"q": payload}
                )
                print(f"[{datetime.now()}] Test XSS avec payload: {payload}")
                print(f"Status code: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] Erreur test XSS: {str(e)}")

    def test_port_scan(self):
        """Scan de ports courants"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432]
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.honeypot_ip, port))
                if result == 0:
                    print(f"[{datetime.now()}] Port {port} ouvert")
                sock.close()
            except Exception as e:
                print(f"[{datetime.now()}] Erreur scan port {port}: {str(e)}")

    def test_brute_force(self):
        """Test de force brute simple"""
        usernames = ["admin", "root", "user", "test"]
        passwords = ["admin", "password", "123456", "test"]
        
        for username in usernames:
            for password in passwords:
                try:
                    response = requests.post(
                        f"{self.base_url}/login",
                        data={"username": username, "password": password}
                    )
                    print(f"[{datetime.now()}] Test credentials: {username}/{password}")
                    print(f"Status code: {response.status_code}")
                    time.sleep(0.5)  # Attente pour éviter de surcharger
                except Exception as e:
                    print(f"[{datetime.now()}] Erreur test credentials: {str(e)}")

    def run_all_tests(self):
        """Exécute tous les tests"""
        print(f"[{datetime.now()}] Début des tests sur {self.honeypot_ip}")
        print("=" * 50)
        
        self.test_ssh_connection()
        print("-" * 50)
        
        self.test_http_injection()
        print("-" * 50)
        
        self.test_xss()
        print("-" * 50)
        
        self.test_port_scan()
        print("-" * 50)
        
        self.test_brute_force()
        print("=" * 50)
        print(f"[{datetime.now()}] Fin des tests")

if __name__ == "__main__":
    # Remplacez l'IP par celle de votre honeypot
    tester = HoneypotTester("127.0.0.1")
    tester.run_all_tests() 