import sys, os, platform, io, zipfile, requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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
import time

class ModernSwitch(QCheckBox):
    def __init__(self, label=""):
        super().__init__(label)
        self.setTristate(False)
        self.setStyleSheet('''
            QCheckBox::indicator {
                width: 40px; height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border-radius: 10px;
                background: #444;
                border: 2px solid #666;
            }
            QCheckBox::indicator:checked {
                border-radius: 10px;
                background: #4e8cff;
                border: 2px solid #4e8cff;
            }
        ''')

class CaptureThread(QThread):
    move_found = pyqtSignal(str, str, float)  # move, fen, score
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self.driver = None

    def stop(self):
        self._running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def download_geckodriver(self):
        import platform
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
            firefox_opts.add_argument("--disable-blink-features=AutomationControlled")
            srv = FirefoxService(executable_path=path)
            d = webdriver.Firefox(service=srv, options=firefox_opts)
            d.maximize_window()
            return d
        except Exception:
            chrome_opts = ChromeOptions()
            chrome_opts.add_argument("--start-maximized")
            chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
            srv = ChromeService(ChromeDriverManager().install())
            d = webdriver.Chrome(service=srv, options=chrome_opts)
            d.maximize_window()
            return d

    def run(self):
        try:
            os.makedirs("screenshots", exist_ok=True)
            self.driver = self.get_driver()
            self.driver.get("https://www.chess.com/play/online")
            while self._running:
                try:
                    wait = WebDriverWait(self.driver, 20)
                    board = wait.until(EC.presence_of_element_located((By.ID, "board-layout-chessboard")))
                    filename = "screenshots/chessboard.png"
                    if os.path.exists(filename):
                        os.remove(filename)
                    board.screenshot(filename)
                    move, fen, score = self.send_to_api(filename)
                    self.move_found.emit(move, fen, score)
                except Exception as e:
                    self.error.emit(f"Erreur capture: {e}")
                    try:
                        self.driver.get("https://www.chess.com/play/online")
                    except Exception:
                        pass
                for _ in range(30):
                    if not self._running:
                        break
                    self.msleep(100)
        except Exception as e:
            self.error.emit(f"Erreur navigateur: {e}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

    def send_to_api(self, image_path):
        try:
            with open(image_path, "rb") as img:
                params = {
                    'skill_level': self.skill_level,
                    'depth': self.depth
                }
                r = requests.post("http://localhost:5000/analyze", 
                                files={"image": img}, 
                                params=params,
                                timeout=10)
            if r.ok:
                data = r.json()
                move = data.get("best_move") or ""
                fen = data.get("fen") or ""
                score = data.get("score", 0)
                return move, fen, score
            else:
                return f"API {r.status_code}", "", 0
        except Exception as e:
            return f"Erreur API: {e}", "", 0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("klar.gg")
        self.setFixedSize(350, 250)
        self.capture_thread = None
        self.skill_level = 20
        self.depth = 15
        self.setStyleSheet('''
            QMainWindow, QWidget {
                background: #181a20;
                color: #e0e0e0;
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3a3d45;
                height: 8px;
                background: #2a2d35;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4e8cff;
                border: none;
                width: 16px;
                height: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #5e9cff;
            }
            QSlider::sub-page:horizontal {
                background: #4e8cff;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #2a2d35;
                border-radius: 4px;
            }
        ''')
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Enabled switch
        enabled_layout = QHBoxLayout()
        enabled_layout.addWidget(QLabel("Enabled:"))
        self.enabled_switch = ModernSwitch()
        self.enabled_switch.stateChanged.connect(self.toggle_capture)
        enabled_layout.addWidget(self.enabled_switch)
        enabled_layout.addStretch(1)
        layout.addLayout(enabled_layout)

        # Skill Level
        skill_layout = QHBoxLayout()
        skill_label = QLabel("Skill Level:")
        skill_label.setFixedWidth(80)
        skill_layout.addWidget(skill_label)
        
        self.skill_slider = QSlider(Qt.Orientation.Horizontal)
        self.skill_slider.setRange(1, 20)
        self.skill_slider.setValue(self.skill_level)
        self.skill_slider.setFixedWidth(180)
        self.skill_slider.valueChanged.connect(self.update_skill)
        skill_layout.addWidget(self.skill_slider)
        
        self.skill_value_label = QLabel(str(self.skill_level))
        self.skill_value_label.setFixedWidth(30)
        self.skill_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        skill_layout.addWidget(self.skill_value_label)
        skill_layout.addStretch(1)
        layout.addLayout(skill_layout)

        # Depth
        depth_layout = QHBoxLayout()
        depth_label = QLabel("Depth:")
        depth_label.setFixedWidth(80)
        depth_layout.addWidget(depth_label)
        
        self.depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.depth_slider.setRange(1, 30)
        self.depth_slider.setValue(self.depth)
        self.depth_slider.setFixedWidth(180)
        self.depth_slider.valueChanged.connect(self.update_depth)
        depth_layout.addWidget(self.depth_slider)
        
        self.depth_value_label = QLabel(str(self.depth))
        self.depth_value_label.setFixedWidth(30)
        self.depth_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        depth_layout.addWidget(self.depth_value_label)
        depth_layout.addStretch(1)
        layout.addLayout(depth_layout)

        # Best move
        move_layout = QHBoxLayout()
        move_layout.addWidget(QLabel("Next Move:"))
        self.bestmove_label = QLabel("")
        move_layout.addWidget(self.bestmove_label)
        move_layout.addStretch(1)
        layout.addLayout(move_layout)

        # Score
        score_layout = QHBoxLayout()
        score_layout.addWidget(QLabel("Score:"))
        self.score_label = QLabel("")
        score_layout.addWidget(self.score_label)
        score_layout.addStretch(1)
        layout.addLayout(score_layout)

        # FEN
        fen_layout = QHBoxLayout()
        fen_layout.addWidget(QLabel("FEN:"))
        self.fen_label = QLabel("")
        fen_layout.addWidget(self.fen_label)
        fen_layout.addStretch(1)
        layout.addLayout(fen_layout)

    def toggle_capture(self):
        if self.enabled_switch.isChecked():
            self.start_capture()
        else:
            self.stop_capture()

    def start_capture(self):
        if self.capture_thread and self.capture_thread.isRunning():
            return
        self.capture_thread = CaptureThread()
        self.capture_thread.move_found.connect(self.update_move)
        self.capture_thread.error.connect(self.show_error)
        self.capture_thread.start()

    def stop_capture(self):
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
            self.capture_thread = None
        self.bestmove_label.setText("")
        self.fen_label.setText("")
        self.score_label.setText("")

    def update_skill(self, value):
        self.skill_level = value
        self.skill_value_label.setText(str(value))

    def update_depth(self, value):
        self.depth = value
        self.depth_value_label.setText(str(value))

    def update_move(self, move, fen, score):
        self.bestmove_label.setText(move)
        self.fen_label.setText(fen)
        score_str = f"{'+' if score > 0 else ''}{score/100:.2f}"
        self.score_label.setText(score_str)

    def show_error(self, msg):
        self.bestmove_label.setText(msg)
        self.fen_label.setText("")
        self.score_label.setText("")

    def closeEvent(self, e):
        self.stop_capture()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())