import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import geckodriver_autoinstaller

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess.com Screenshot")
        self.setFixedSize(400, 200)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Prêt à capturer")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Bouton start/stop
        self.toggle_button = QPushButton("Démarrer la capture")
        self.toggle_button.clicked.connect(self.toggle_capture)
        layout.addWidget(self.toggle_button)
        
        # Initialisation des variables
        self.driver = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_chessboard)
        self.is_capturing = False
        
        # Créer le dossier screenshots s'il n'existe pas
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
    
    def get_driver(self):
        """Crée et retourne un driver Firefox"""
        try:
            # Installation automatique de geckodriver si nécessaire
            geckodriver_autoinstaller.install()
            
            firefox_options = FirefoxOptions()
            # Retirer le mode headless pour voir le navigateur
            # firefox_options.add_argument("--headless")
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")
            firefox_options.add_argument("--start-maximized")
            
            # Ajouter des préférences Firefox
            firefox_options.set_preference("browser.startup.homepage", "https://www.chess.com/play/online")
            firefox_options.set_preference("browser.startup.homepage_override.mstone", "ignore")
            firefox_options.set_preference("browser.startup.homepage_override.bookmarks", "ignore")
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            
            # Maximiser la fenêtre
            driver.maximize_window()
            
            return driver
                
        except Exception as e:
            print(f"Erreur lors de l'initialisation du driver: {str(e)}")
            return None
    
    def capture_chessboard(self):
        """Capture l'écran de l'échiquier"""
        try:
            if not self.driver:
                self.driver = self.get_driver()
                if not self.driver:
                    raise Exception("Impossible d'initialiser le navigateur")
                
                # Charger la page chess.com
                self.driver.get("https://www.chess.com/play/online")
                print("Page chess.com chargée")
            
            # Attendre que la page soit chargée et recharger l'élément à chaque fois
            wait = WebDriverWait(self.driver, 20)
            print("Recherche de l'échiquier...")
            
            # Attendre que l'élément soit présent et interactif
            chessboard = wait.until(
                EC.presence_of_element_located((By.ID, "board-layout-chessboard"))
            )
            wait.until(
                EC.element_to_be_clickable((By.ID, "board-layout-chessboard"))
            )
            print("Échiquier trouvé!")
            
            # Nom du fichier fixe pour toujours écraser le même fichier
            filename = "screenshots/chessboard.png"
            
            # Supprimer l'ancien fichier s'il existe
            if os.path.exists(filename):
                os.remove(filename)
                print("Ancien screenshot supprimé")
            
            # Capture d'écran avec gestion des erreurs stale
            try:
                chessboard.screenshot(filename)
            except Exception as e:
                if "stale" in str(e).lower():
                    print("Élément stale détecté, nouvelle tentative...")
                    # Recharger l'élément
                    chessboard = wait.until(
                        EC.presence_of_element_located((By.ID, "board-layout-chessboard"))
                    )
                    chessboard.screenshot(filename)
                else:
                    raise e
            
            self.status_label.setText(f"Screenshot mis à jour: {filename}")
            print(f"Screenshot sauvegardé: {filename}")
            
        except Exception as e:
            error_msg = f"Erreur lors de la capture: {str(e)}"
            print(error_msg)
            self.status_label.setText(error_msg)
            self.stop_capture()
            QMessageBox.warning(self, "Erreur", error_msg)
    
    def toggle_capture(self):
        """Démarre ou arrête la capture"""
        if self.is_capturing:
            self.stop_capture()
        else:
            self.start_capture()
    
    def start_capture(self):
        """Démarre la capture toutes les 5 secondes"""
        self.is_capturing = True
        self.toggle_button.setText("Arrêter la capture")
        self.status_label.setText("Capture en cours...")
        self.timer.start(5000)  # 5000 ms = 5 secondes
    
    def stop_capture(self):
        """Arrête la capture"""
        self.is_capturing = False
        self.toggle_button.setText("Démarrer la capture")
        self.timer.stop()
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def closeEvent(self, event):
        """Gestion de la fermeture de la fenêtre"""
        self.stop_capture()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
