import sys, os, platform, io, zipfile, requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess.com Screenshot")
        self.setFixedSize(400, 200)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.status_label = QLabel("Prêt")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        self.toggle_button = QPushButton("Démarrer")
        self.toggle_button.clicked.connect(self.toggle_capture)
        layout.addWidget(self.toggle_button)
        self.driver = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_chessboard)
        self.is_capturing = False
        os.makedirs("screenshots", exist_ok=True)

    def download_geckodriver(self):
        system = platform.system().lower()
        platform_name, ext = ("win64", ".zip") if system == "windows" else (("linux64", ".tar.gz") if system == "linux" else ("macos", ".tar.gz"))
        version = "v0.33.0"
        url = f"https://github.com/mozilla/geckodriver/releases/download/{version}/geckodriver-{version}-{platform_name}{ext}"
        data = requests.get(url, timeout=30).content
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drivers")
        os.makedirs(driver_dir, exist_ok=True)
        if ext == ".zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(driver_dir)
        else:
            import tarfile, io as _io
            with tarfile.open(fileobj=_io.BytesIO(data), mode="r:gz") as t:
                t.extractall(driver_dir)
        if system != "windows":
            os.chmod(os.path.join(driver_dir, "geckodriver"), 0o755)
        return os.path.join(driver_dir, "geckodriver" + (".exe" if system == "windows" else ""))

    def get_driver(self):
        try:
            path = self.download_geckodriver()
            firefox_opts = FirefoxOptions()
            firefox_opts.add_argument("--width=1920")
            firefox_opts.add_argument("--height=1080")
            firefox_opts.add_argument("--start-maximized")
            srv = FirefoxService(executable_path=path)
            d = webdriver.Firefox(service=srv, options=firefox_opts)
            d.maximize_window()
            return d
        except Exception:
            chrome_opts = ChromeOptions()
            chrome_opts.add_argument("--start-maximized")
            srv = ChromeService(ChromeDriverManager().install())
            d = webdriver.Chrome(service=srv, options=chrome_opts)
            d.maximize_window()
            return d

    def capture_chessboard(self):
        try:
            if not self.driver:
                self.driver = self.get_driver()
                self.driver.get("https://www.chess.com/play/online")
            wait = WebDriverWait(self.driver, 20)
            board = wait.until(EC.presence_of_element_located((By.ID, "board-layout-chessboard")))
            filename = "screenshots/chessboard.png"
            if os.path.exists(filename):
                os.remove(filename)
            board.screenshot(filename)
            self.status_label.setText("Screenshot OK")
            self.send_to_api(filename)
        except Exception as e:
            self.status_label.setText(str(e))
            self.stop_capture()
            QMessageBox.warning(self, "Erreur", str(e))

    def send_to_api(self, image_path):
        try:
            with open(image_path, "rb") as img:
                r = requests.post("http://localhost:5000/analyze", files={"image": img}, timeout=10)
            if r.ok:
                data = r.json()
                move = data.get("best_move") or data.get("fen") or ""
                self.status_label.setText(f"Meilleur coup: {move}" if move else "Réponse vide")
                print(f"Réponse API: {data}")
            else:
                self.status_label.setText(f"API {r.status_code}")
                print(r.text)
        except Exception as e:
            self.status_label.setText("Erreur API")
            print(e)

    def toggle_capture(self):
        (self.stop_capture() if self.is_capturing else self.start_capture())

    def start_capture(self):
        self.is_capturing = True
        self.toggle_button.setText("Arrêter")
        self.timer.start(5000)

    def stop_capture(self):
        self.is_capturing = False
        self.toggle_button.setText("Démarrer")
        self.timer.stop()
        if self.driver:
            self.driver.quit()
            self.driver = None

    def closeEvent(self, e):
        self.stop_capture()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())