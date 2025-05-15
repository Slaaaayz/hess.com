import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import zipfile
import io
import platform

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess.com Screenshot")
        self.setFixedSize(400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Prêt à capturer")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.toggle_button = QPushButton("Démarrer la capture")
        self.toggle_button.clicked.connect(self.toggle_capture)
        layout.addWidget(self.toggle_button)

        self.driver = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_chessboard)
        self.is_capturing = False

        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def download_geckodriver(self):
        try:
            system = platform.system().lower()
            if system == "windows":
                platform_name = "win64"
                extension = ".zip"
            elif system == "linux":
                platform_name = "linux64"
                extension = ".tar.gz"
            else:
                platform_name = "macos"
                extension = ".tar.gz"

            version = "v0.33.0"
            url = f"https://github.com/mozilla/geckodriver/releases/download/{version}/geckodriver-{version}-{platform_name}{extension}"

            response = requests.get(url)
            response.raise_for_status()

            driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers")
            if not os.path.exists(driver_dir):
                os.makedirs(driver_dir)

            if extension == ".zip":
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    zip_file.extractall(driver_dir)
            else:
                import tarfile
                with tarfile.open(fileobj=io.BytesIO(response.content), mode='r:gz') as tar:
                    tar.extractall(driver_dir)

            if system != "windows":
                geckodriver_path = os.path.join(driver_dir, "geckodriver")
                os.chmod(geckodriver_path, 0o755)

            return os.path.join(driver_dir, "geckodriver" + (".exe" if system == "windows" else ""))

        except Exception as e:
            print(f"Erreur lors du téléchargement de geckodriver: {str(e)}")
            return None

    def get_driver(self):
        try:
            try:
                print("Tentative d'initialisation de Firefox...")
                geckodriver_path = self.download_geckodriver()
                if not geckodriver_path:
                    raise Exception("Impossible de télécharger geckodriver")

                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--width=1920")
                firefox_options.add_argument("--height=1080")
                firefox_options.add_argument("--start-maximized")
                firefox_options.set_preference("browser.startup.homepage", "https://www.chess.com/play/online")
                firefox_options.set_preference("browser.startup.homepage_override.mstone", "ignore")
                firefox_options.set_preference("browser.startup.homepage_override.bookmarks", "ignore")

                service = FirefoxService(executable_path=geckodriver_path)
                driver = webdriver.Firefox(service=service, options=firefox_options)
                driver.maximize_window()
                print("Firefox initialisé avec succès!")
                return driver

            except Exception as firefox_error:
                print(f"Erreur avec Firefox: {str(firefox_error)}")
                print("Tentative d'initialisation de Chrome...")

                chrome_options = ChromeOptions()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")

                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.maximize_window()
                print("Chrome initialisé avec succès!")
                return driver

        except Exception as e:
            print(f"Erreur lors de l'initialisation des drivers: {str(e)}")
            return None

    def capture_chessboard(self):
        try:
            if not self.driver:
                self.driver = self.get_driver()
                if not self.driver:
                    raise Exception("Impossible d'initialiser le navigateur")
                self.driver.get("https://www.chess.com/play/online")
                print("Page chess.com chargée")

            wait = WebDriverWait(self.driver, 20)
            print("Recherche de l'échiquier...")

            chessboard = wait.until(
                EC.presence_of_element_located((By.ID, "board-layout-chessboard"))
            )
            wait.until(
                EC.element_to_be_clickable((By.ID, "board-layout-chessboard"))
            )
            print("Échiquier trouvé!")

            filename = "screenshots/chessboard.png"
            if os.path.exists(filename):
                os.remove(filename)
                print("Ancien screenshot supprimé")

            try:
                chessboard.screenshot(filename)
            except Exception as e:
                if "stale" in str(e).lower():
                    print("Élément stale détecté, nouvelle tentative...")
                    chessboard = wait.until(
                        EC.presence_of_element_located((By.ID, "board-layout-chessboard"))
                    )
                    chessboard.screenshot(filename)
                else:
                    raise e

            self.status_label.setText(f"Screenshot mis à jour: {filename}")
            print(f"Screenshot sauvegardé: {filename}")

            self.send_to_api(filename)

        except Exception as e:
            error_msg = f"Erreur lors de la capture: {str(e)}"
            print(error_msg)
            self.status_label.setText(error_msg)
            self.stop_capture()
            QMessageBox.warning(self, "Erreur", error_msg)

    def send_to_api(self, image_path):
        try:
            with open(image_path, "rb") as img:
                files = {'image': img}
                response = requests.post("http://localhost:5000/analyze", files=files)
                if response.status_code == 200:
                    data = response.json()
                    fen = data.get("fen", "")
                    print(f"FEN reçu: {fen}")
                else:
                    print(f"Erreur API: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Erreur lors de l'envoi à l'API: {str(e)}")

    def toggle_capture(self):
        if self.is_capturing:
            self.stop_capture()
        else:
            self.start_capture()

    def start_capture(self):
        self.is_capturing = True
        self.toggle_button.setText("Arrêter la capture")
        self.status_label.setText("Capture en cours...")
        self.timer.start(5000)

    def stop_capture(self):
        self.is_capturing = False
        self.toggle_button.setText("Démarrer la capture")
        self.timer.stop()
        if self.driver:
            self.driver.quit()
            self.driver = None

    def closeEvent(self, event):
        self.stop_capture()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
