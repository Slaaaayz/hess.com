import sys, os, platform, io, zipfile, requests
import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider, QTextEdit, QLineEdit, QFileDialog, QPushButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import speech_recognition as sr
import json
import hmac
import hashlib

# Rediriger stderr vers /dev/null pour supprimer les messages ALSA/JACK
if platform.system() == 'Linux':
    sys.stderr = open(os.devnull, 'w')

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

class MoveExecutor:
    def __init__(self, driver):
        self.driver = driver
        self.board = None

    def update_board_info(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            self.board = wait.until(
                EC.presence_of_element_located((By.ID, "board-layout-chessboard"))
            )
            wait.until(EC.visibility_of(self.board))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", self.board)
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour des informations du plateau: {e}")
            return False

    def get_board_orientation(self):
        board_class = self.board.get_attribute('class')
        return 'black' if 'flipped' in board_class else 'white'

    def algebraic_to_square_class(self, square):
        file = ord(square[0]) - ord('a') + 1
        rank = square[1]
        return f"square-{file}{rank}"

    def algebraic_to_coords(self, square, square_size, orientation):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        if orientation == 'white':
            x = file * square_size + square_size / 2
            y = (7 - rank) * square_size + square_size / 2
        else:  # black
            x = (7 - file) * square_size + square_size / 2
            y = rank * square_size + square_size / 2
        return x, y

    def execute_move(self, move):
        if not self.update_board_info():
            return False
        try:
            from_square = move[:2]
            to_square = move[2:]
            print(f"Tentative de mouvement de {from_square} à {to_square}")

            from_class = self.algebraic_to_square_class(from_square)
            wait = WebDriverWait(self.driver, 10)
            from_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f".piece.{from_class}")))

            board_rect = self.board.rect
            square_size = board_rect['width'] / 8
            orientation = self.get_board_orientation()

            from_x, from_y = self.algebraic_to_coords(from_square, square_size, orientation)
            to_x, to_y = self.algebraic_to_coords(to_square, square_size, orientation)

            offset_x = to_x - from_x
            offset_y = to_y - from_y

            actions = ActionChains(self.driver)
            actions.move_to_element(from_elem).click_and_hold().pause(0.1)
            actions.move_by_offset(offset_x, offset_y).pause(0.1)
            actions.release().perform()
            print(f"Drag & drop de {from_square} vers {to_square} effectué.")
            return True
        except Exception as e:
            print(f"Erreur lors de l'exécution du coup (drag & drop): {e}")
            return False

class CaptureThread(QThread):
    move_found = pyqtSignal(str, str, float)  # move, fen, score
    error = pyqtSignal(str)

    def __init__(self, parent=None, skill_level=20, depth=15, auto_play=False, api_key=""):
        super().__init__(parent)
        self._running = True
        self.driver = None
        self.skill_level = skill_level
        self.depth = depth
        self.auto_play = auto_play
        self.move_executor = None
        self.api_key = api_key

    def update_parameters(self, skill_level, depth, auto_play=None, api_key=None):
        self.skill_level = skill_level
        self.depth = depth
        if auto_play is not None:
            self.auto_play = auto_play
        if api_key is not None:
            self.api_key = api_key

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
        driver_path = os.path.join(driver_dir, "geckodriver" + (".exe" if system == "windows" else ""))
        
        # Vérifier si le driver existe déjà et est en cours d'utilisation
        if os.path.exists(driver_path):
            try:
                # Essayer de supprimer l'ancien driver
                os.remove(driver_path)
            except PermissionError:
                # Si on ne peut pas le supprimer, on essaie de le renommer
                try:
                    os.rename(driver_path, driver_path + ".old")
                except:
                    raise RuntimeError("Impossible d'accéder au geckodriver existant. Veuillez redémarrer l'application.")
        
        if ext == ".zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                z.extractall(driver_dir)
        else:
            import tarfile, io as _io
            with tarfile.open(fileobj=_io.BytesIO(data), mode="r:gz") as t:
                t.extractall(driver_dir)
        
        if system != "windows":
            os.chmod(driver_path, 0o755)
        
        return driver_path

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
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'initialisation de Firefox: {str(e)}")

    def run(self):
        try:
            os.makedirs("screenshots", exist_ok=True)
            self.driver = self.get_driver()
            self.driver.get("https://www.chess.com/play/online")
            self.move_executor = MoveExecutor(self.driver)
            
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
                    
                    # Exécuter le coup si auto_play est activé
                    if self.auto_play and move and len(move) == 4:
                        self.move_executor.execute_move(move)
                        
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
                headers = {
                    'X-API-Key': self.api_key
                }
                r = requests.post("http://127.0.0.1:5001/analyze", 
                                files={"image": img}, 
                                params=params,
                                headers=headers,
                                timeout=10)
            if r.ok:
                data = r.json()
                move = data.get("best_move") or ""
                fen = data.get("fen") or ""
                score = data.get("score", 0)
                return move, fen, score
            else:
                error_msg = f"API {r.status_code}"
                if r.status_code == 401:
                    error_msg = "Invalid API key"
                return error_msg, "", 0
        except Exception as e:
            return f"Erreur API: {e}", "", 0

class OverlayWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Cache la fenêtre initialement
        
        # Configuration de la fenêtre
        self.root.overrideredirect(True)  # Supprime la barre de titre
        self.root.attributes('-topmost', True)  # Garde la fenêtre au-dessus
        self.root.attributes('-alpha', 0.9)  # Transparence
        
        # Position initiale
        self.root.geometry('350x400+50+50')
        
        # Style
        self.root.configure(bg='#181a20')
        
        # Création du conteneur principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variables
        self.visible = True
        self.ctrl_pressed = False
        
        # Bindings
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.on_move)
        
        # Raccourci global avec pynput
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        
        # Style ttk
        style = ttk.Style()
        style.configure('TFrame', background='#181a20')
        style.configure('TLabel', background='#181a20', foreground='#e0e0e0')
        
        # Labels pour les informations
        self.move_label = ttk.Label(self.main_frame, text="Next Move: ")
        self.move_label.pack(anchor='w', pady=2)
        
        self.score_label = ttk.Label(self.main_frame, text="Score: ")
        self.score_label.pack(anchor='w', pady=2)
        
        self.fen_label = ttk.Label(self.main_frame, text="FEN: ")
        self.fen_label.pack(anchor='w', pady=2)
        
        # Zone de logs
        self.log_text = tk.Text(self.main_frame, height=10, bg='#1a1c22', fg='#a0a0a0',
                               font=('Consolas', 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Afficher la fenêtre
        self.root.deiconify()
        
    def on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.space and self.ctrl_pressed:
                self.toggle_visibility()
        except AttributeError:
            pass
            
    def on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False
        except AttributeError:
            pass
        
    def toggle_visibility(self):
        self.visible = not self.visible
        if self.visible:
            self.root.deiconify()
        else:
            self.root.withdraw()
            
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def update_info(self, move, fen, score):
        self.move_label.config(text=f"Next Move: {move}")
        self.score_label.config(text=f"Score: {score}")
        self.fen_label.config(text=f"FEN: {fen}")
        
    def log_message(self, message, is_error=False):
        timestamp = time.strftime("%H:%M:%S")
        color = "#ff6b6b" if is_error else "#4e8cff"
        self.log_text.insert(tk.END, f'[{timestamp}] {message}\n')
        self.log_text.see(tk.END)
        
    def update(self):
        self.root.update()
        
    def destroy(self):
        if self.listener:
            self.listener.stop()
        self.root.destroy()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("klar.gg")
        self.setFixedSize(350, 400)
        self.capture_thread = None
        self.voice_thread = None
        self.skill_level = 20
        self.depth = 15
        self.auto_play = False
        self.voice_enabled = False
        self.move_executor = None
        self.api_key = ""
        
        # Création de l'overlay
        self.overlay = OverlayWindow()
        
        # Timer pour mettre à jour l'overlay
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_overlay)
        self.update_timer.start(100)  # Mise à jour toutes les 100ms
        
        # Raccourci global pour masquer/afficher l'overlay
        self.shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        self.shortcut.activated.connect(self.toggle_overlay)
        
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
            QLineEdit {
                background: #1a1c22;
                color: #e0e0e0;
                border: 1px solid #2a2d35;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #4e8cff;
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
            QTextEdit {
                background: #1a1c22;
                color: #a0a0a0;
                border: 1px solid #2a2d35;
                border-radius: 4px;
                padding: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        ''')
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key")
        self.api_key_input.textChanged.connect(self.update_api_key)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Enabled switch
        enabled_layout = QHBoxLayout()
        enabled_layout.addWidget(QLabel("Enabled:"))
        self.enabled_switch = ModernSwitch()
        self.enabled_switch.stateChanged.connect(self.toggle_capture)
        enabled_layout.addWidget(self.enabled_switch)
        enabled_layout.addStretch(1)
        layout.addLayout(enabled_layout)

        # Bot switch
        bot_layout = QHBoxLayout()
        bot_layout.addWidget(QLabel("Bot:"))
        self.bot_switch = ModernSwitch()
        self.bot_switch.stateChanged.connect(self.toggle_bot)
        bot_layout.addWidget(self.bot_switch)
        bot_layout.addStretch(1)
        layout.addLayout(bot_layout)

        # Voice Recognition switch
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_switch = ModernSwitch()
        self.voice_switch.stateChanged.connect(self.toggle_voice)
        voice_layout.addWidget(self.voice_switch)
        voice_layout.addStretch(1)
        layout.addLayout(voice_layout)

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

        # Boutons Export/Import
        config_layout = QHBoxLayout()
        export_btn = QPushButton("Exporter config")
        import_btn = QPushButton("Importer config")
        export_btn.clicked.connect(self.export_config)
        import_btn.clicked.connect(self.import_config)
        config_layout.addWidget(export_btn)
        config_layout.addWidget(import_btn)
        layout.addLayout(config_layout)

        # Logs
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Logs:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(100)
        log_layout.addWidget(self.log_text)
        layout.addLayout(log_layout)

    def toggle_capture(self):
        if self.enabled_switch.isChecked():
            self.start_capture()
            self.log_message("Capture started")
        else:
            self.stop_capture()
            self.log_message("Capture stopped")

    def toggle_bot(self, state):
        self.auto_play = bool(state)
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.update_parameters(self.skill_level, self.depth, self.auto_play)
        self.log_message(f"Bot {'activé' if self.auto_play else 'désactivé'}")

    def toggle_voice(self, state):
        self.voice_enabled = bool(state)
        if self.voice_enabled:
            self.start_voice_recognition()
            self.log_message("Reconnaissance vocale activée")
        else:
            self.stop_voice_recognition()
            self.log_message("Reconnaissance vocale désactivée")

    def start_capture(self):
        if self.capture_thread and self.capture_thread.isRunning():
            return
        self.capture_thread = CaptureThread(
            skill_level=self.skill_level,
            depth=self.depth,
            auto_play=self.auto_play,
            api_key=self.api_key
        )
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
        self.log_message(f"Skill level updated to {value}")
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.update_parameters(self.skill_level, self.depth, self.auto_play)
        # Sauvegarde côté API
        self.save_user_settings()

    def update_depth(self, value):
        self.depth = value
        self.depth_value_label.setText(str(value))
        self.log_message(f"Depth updated to {value}")
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.update_parameters(self.skill_level, self.depth, self.auto_play)
        # Sauvegarde côté API
        self.save_user_settings()

    def save_user_settings(self):
        import requests
        try:
            requests.post(
                "http://127.0.0.1:5001/user_settings",
                headers={"X-API-Key": self.api_key, "Content-Type": "application/json"},
                json={"skillLevel": self.skill_level, "searchDepth": self.depth},
                timeout=3
            )
        except Exception as e:
            self.log_message(f"Erreur sauvegarde settings: {e}", is_error=True)

    def update_overlay(self):
        self.overlay.update()

    def update_move(self, move, fen, score):
        self.bestmove_label.setText(move)
        self.fen_label.setText(fen)
        score_str = f"{'+' if score > 0 else ''}{score/100:.2f}"
        self.score_label.setText(score_str)
        self.log_message(f"Move: {move} | Score: {score_str} | FEN: {fen}")
        
        # Mise à jour de l'overlay
        self.overlay.update_info(move, fen, score_str)
        self.overlay.log_message(f"Move: {move} | Score: {score_str} | FEN: {fen}")

    def show_error(self, msg):
        self.bestmove_label.setText(msg)
        self.fen_label.setText("")
        self.score_label.setText("")
        self.log_message(msg, is_error=True)

    def log_message(self, message, is_error=False):
        timestamp = time.strftime("%H:%M:%S")
        color = "#ff6b6b" if is_error else "#4e8cff"
        self.log_text.append(f'<span style="color: {color}">[{timestamp}]</span> {message}')
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Mise à jour des logs de l'overlay
        self.overlay.log_message(message, is_error)

    def closeEvent(self, e):
        self.stop_capture()
        self.stop_voice_recognition()
        self.overlay.destroy()
        e.accept()

    def toggle_overlay(self):
        self.overlay.toggle_visibility()

    def start_voice_recognition(self):
        if self.voice_thread and self.voice_thread.isRunning():
            return
        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.text_recognized.connect(self.handle_voice_command)
        self.voice_thread.error.connect(self.show_error)
        self.voice_thread.start()

    def stop_voice_recognition(self):
        if self.voice_thread:
            self.voice_thread.stop()
            self.voice_thread.wait()
            self.voice_thread = None

    def handle_voice_command(self, text):
        self.log_message(f"Commande vocale détectée: {text}")
        
        # Convertir le texte en minuscules pour la cohérence
        text = text.lower()
        
        # Patterns de reconnaissance pour les mouvements
        patterns = [
            r"([a-h][1-8])\s*(?:en|à|vers)\s*([a-h][1-8])",  # d2 en d4
            r"([a-h][1-8])\s*([a-h][1-8])",                  # d2 d4
            r"([a-h][1-8])\s*-\s*([a-h][1-8])"              # d2-d4
        ]
        
        import re
        move = None
        
        # Essayer chaque pattern
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                from_square = match.group(1)
                to_square = match.group(2)
                move = from_square + to_square
                break
        
        if move:
            self.log_message(f"Mouvement détecté: {move}")
            if self.capture_thread and self.capture_thread.move_executor:
                # Utiliser le move_executor du capture_thread pour exécuter le mouvement
                success = self.capture_thread.move_executor.execute_move(move)
                if success:
                    self.log_message(f"Mouvement {move} exécuté avec succès")
                else:
                    self.log_message(f"Échec de l'exécution du mouvement {move}", is_error=True)
        else:
            self.log_message(f"Format de mouvement non reconnu: {text}", is_error=True)

    def update_api_key(self, text):
        self.api_key = text
        self.log_message("API key updated")
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.update_parameters(
                self.skill_level, 
                self.depth, 
                self.auto_play, 
                self.api_key
            )
        # --- AJOUT : récupération des settings utilisateur ---
        try:
            r = requests.get(
                "http://127.0.0.1:5001/user_settings",
                headers={"X-API-Key": text},
                timeout=5
            )
            if r.ok:
                data = r.json()
                settings = data.get("settings", {})
                # Appliquer les settings à l'UI
                if "skillLevel" in settings:
                    self.skill_level = int(settings["skillLevel"])
                    self.skill_slider.setValue(self.skill_level)
                if "searchDepth" in settings:
                    self.depth = int(settings["searchDepth"])
                    self.depth_slider.setValue(self.depth)
                # Forcer la mise à jour des labels
                self.skill_value_label.setText(str(self.skill_level))
                self.depth_value_label.setText(str(self.depth))
                self.log_message("User settings loaded depuis l'API")
            else:
                self.log_message("Clé API non reconnue ou pas de settings", is_error=True)
        except Exception as e:
            self.log_message(f"Erreur lors du chargement des settings: {e}", is_error=True)

    def sign_config(self, config):
        msg = f"{config['skillLevel']}|{config['searchDepth']}".encode()
        return hmac.new(b"ma_cle_secrete_ultra_longue", msg, hashlib.sha256).hexdigest()

    def export_config(self):
        config = {
            "skillLevel": self.skill_level,
            "searchDepth": self.depth
        }
        config["signature"] = self.sign_config(config)
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter la config", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(config, f, indent=2)
                self.log_message(f"Config exportée vers {file_path}")
            except Exception as e:
                self.log_message(f"Erreur export config: {e}", is_error=True)

    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importer une config", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    config = json.load(f)
                # Vérification de la signature
                signature = config.pop("signature", None)
                if signature != self.sign_config(config):
                    self.log_message("Fichier de config modifié ou corrompu !", is_error=True)
                    return
                if "skillLevel" in config:
                    self.skill_level = int(config["skillLevel"])
                    self.skill_slider.setValue(self.skill_level)
                if "searchDepth" in config:
                    self.depth = int(config["searchDepth"])
                    self.depth_slider.setValue(self.depth)
                self.skill_value_label.setText(str(self.skill_level))
                self.depth_value_label.setText(str(self.depth))
                self.save_user_settings()
                self.log_message(f"Config importée depuis {file_path}")
            except Exception as e:
                self.log_message(f"Erreur import config: {e}", is_error=True)

class VoiceRecognitionThread(QThread):
    text_recognized = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self.recognizer = sr.Recognizer()

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source)
                    try:
                        text = self.recognizer.recognize_google(audio, language="fr-FR")
                        self.text_recognized.emit(text)
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        self.error.emit(f"Erreur de reconnaissance vocale: {e}")
            except Exception as e:
                self.error.emit(f"Erreur microphone: {e}")
            self.msleep(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())