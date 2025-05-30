import sys, os, platform, io, zipfile, requests
import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider, QTextEdit, QLineEdit, QFileDialog, QPushButton, QStackedWidget, QColorDialog, QDialog, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut, QPixmap, QFont
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

        # Style général Pawned
        self.root.configure(bg='#0a0f0d')
        self.root.option_add("*Font", "SegoeUI 11")

        # Appliquer le style néon/futuriste sur les widgets Tkinter
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#0a0f0d')
        style.configure('TLabel', background='#0a0f0d', foreground='#00ff99', font=('Segoe UI', 11, 'bold'))
        style.configure('TButton', background='#101a14', foreground='#00ff99', borderwidth=2, focusthickness=3, focuscolor='#00ff99')
        style.map('TButton', background=[('active', '#00ff99')], foreground=[('active', '#101a14')])

        # Configuration de la fenêtre
        self.root.overrideredirect(True)  # Supprime la barre de titre
        self.root.attributes('-topmost', True)  # Garde la fenêtre au-dessus
        self.root.attributes('-alpha', 0.92)  # Transparence
        self.root.geometry('350x400+50+50')

        # Création du conteneur principal
        self.main_frame = ttk.Frame(self.root, style='TFrame')
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

        # Labels pour les informations
        self.move_label = ttk.Label(self.main_frame, text="Next Move:", style='TLabel')
        self.move_label.pack(anchor='w', pady=2)
        self.score_label = ttk.Label(self.main_frame, text="Score:", style='TLabel')
        self.score_label.pack(anchor='w', pady=2)
        self.fen_label = ttk.Label(self.main_frame, text="FEN:", style='TLabel')
        self.fen_label.pack(anchor='w', pady=2)

        # Zone de logs stylée
        self.log_text = tk.Text(self.main_frame, height=10, bg='#181a20', fg='#00ff99',
                               font=('Consolas', 10), insertbackground='#00ff99',
                               borderwidth=2, relief='groove')
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

class UiCustomizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personnaliser l'UI")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        # Thème
        theme_label = QLabel("Thème :")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Pawned (sombre)", "Clair"])
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        # Couleur principale
        color_label = QLabel("Couleur principale :")
        self.color_btn = QPushButton("Choisir la couleur")
        self.color_btn.clicked.connect(self.pick_color)
        self.selected_color = "#00ff99"
        layout.addWidget(color_label)
        layout.addWidget(self.color_btn)
        # Taille de police
        font_label = QLabel("Taille de police :")
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 24)
        self.font_slider.setValue(14)
        layout.addWidget(font_label)
        layout.addWidget(self.font_slider)
        # Appliquer
        apply_btn = QPushButton("Appliquer")
        apply_btn.clicked.connect(self.apply_changes)
        layout.addWidget(apply_btn)
        self.setLayout(layout)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(f"background: {self.selected_color}; color: #101a14;")

    def apply_changes(self):
        # Signal custom ou accès direct au parent
        parent = self.parent()
        if parent:
            theme = self.theme_combo.currentText()
            color = self.selected_color
            font_size = self.font_slider.value()
            parent.apply_ui_customization(theme, color, font_size)
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("klar.gg")
        self.setMinimumSize(900, 600)
        self.capture_thread = None
        self.voice_thread = None
        self.skill_level = 20
        self.depth = 15
        self.auto_play = False
        self.voice_enabled = False
        self.move_executor = None
        self.api_key = ""

        # Overlay flottant
        self.overlay = OverlayWindow()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_overlay)
        self.update_timer.start(100)
        self.shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        self.shortcut.activated.connect(self.toggle_overlay)

        # Widgets partagés (toujours initialisés)
        self.bestmove_label = QLabel("")
        self.score_label = QLabel("")
        self.fen_label = QLabel("")
        self.enabled_switch = ModernSwitch("Enabled")
        self.bot_switch = ModernSwitch("Bot")
        self.voice_switch = ModernSwitch("Voice")
        self.skill_slider = QSlider(Qt.Orientation.Horizontal)
        self.skill_value_label = QLabel(str(self.skill_level))
        self.depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.depth_value_label = QLabel(str(self.depth))
        self.api_key_input = QLineEdit()
        self.log_text = QTextEdit()

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (menu vertical)
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 32, 16, 32)
        sidebar_layout.setSpacing(24)
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet("background: #101a14;")

        # Logo en haut de la sidebar
        logo_label = QLabel()
        pixmap = QPixmap("./ChessBotSite/Pawned.png")
        pixmap = pixmap.scaled(64, 64)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(20)

        # Boutons menu
        self.dashboard_btn = QPushButton("Dashboard")
        self.options_btn = QPushButton("Options")
        for btn in [self.dashboard_btn, self.options_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("QPushButton { color: #00ff99; background: #181a20; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; } QPushButton:hover { background: #00ff99; color: #101a14; }")
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch(1)

        main_layout.addWidget(sidebar)

        # Zone principale (contenu)
        self.stack = QStackedWidget()
        # Page Dashboard
        dashboard_page = QWidget()
        dash_layout = QVBoxLayout(dashboard_page)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        dash_layout.setSpacing(28)
        dash_layout.addStretch(2)
        dash_label = QLabel("Dashboard")
        dash_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        dash_label.setStyleSheet("font-size: 22px; color: #00ff99; font-weight: bold;")
        dash_layout.addWidget(dash_label)
        dash_layout.addSpacing(18)

        # Switches sur une ligne
        switches_layout = QHBoxLayout()
        switches_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.enabled_switch.setFixedWidth(100)
        self.enabled_switch.stateChanged.connect(self.toggle_capture)
        self.bot_switch.setFixedWidth(100)
        self.bot_switch.stateChanged.connect(self.toggle_bot)
        self.voice_switch.setFixedWidth(100)
        self.voice_switch.stateChanged.connect(self.toggle_voice)
        for sw in [self.enabled_switch, self.bot_switch, self.voice_switch]:
            switches_layout.addWidget(sw)
            switches_layout.addSpacing(12)
        dash_layout.addLayout(switches_layout)
        dash_layout.addSpacing(18)

        # Best move
        move_layout = QHBoxLayout()
        move_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        move_label = QLabel("Next Move:")
        move_layout.addWidget(move_label)
        move_layout.addWidget(self.bestmove_label)
        dash_layout.addLayout(move_layout)
        dash_layout.addSpacing(8)

        # Score
        score_layout = QHBoxLayout()
        score_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        score_label = QLabel("Score:")
        score_layout.addWidget(score_label)
        score_layout.addWidget(self.score_label)
        dash_layout.addLayout(score_layout)
        dash_layout.addSpacing(8)

        # FEN
        fen_layout = QHBoxLayout()
        fen_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        fen_label = QLabel("FEN:")
        fen_layout.addWidget(fen_label)
        fen_layout.addWidget(self.fen_label)
        dash_layout.addLayout(fen_layout)
        dash_layout.addSpacing(18)

        # Boutons Export/Import sur une ligne
        config_layout = QHBoxLayout()
        config_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        export_btn = QPushButton("Exporter config")
        import_btn = QPushButton("Importer config")
        export_btn.setMinimumWidth(140)
        import_btn.setMinimumWidth(140)
        export_btn.setFixedHeight(32)
        import_btn.setFixedHeight(32)
        export_btn.clicked.connect(self.export_config)
        import_btn.clicked.connect(self.import_config)
        config_layout.addWidget(export_btn)
        config_layout.addSpacing(16)
        config_layout.addWidget(import_btn)
        dash_layout.addLayout(config_layout)
        dash_layout.addStretch(3)

        # Page Options
        options_page = QWidget()
        opt_main_layout = QVBoxLayout(options_page)
        opt_main_layout.setContentsMargins(0, 0, 0, 0)
        opt_main_layout.setSpacing(0)
        opt_main_layout.addStretch(2)

        # Conteneur centré avec marges
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(60, 0, 60, 0)  # marges latérales
        center_layout.setSpacing(28)

        opt_label = QLabel("Options")
        opt_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        opt_label.setStyleSheet("font-size: 22px; color: #00ff99; font-weight: bold;")
        center_layout.addWidget(opt_label)
        center_layout.addSpacing(28)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        api_key_label = QLabel("API Key:")
        self.api_key_input.setPlaceholderText("Enter your API key")
        self.api_key_input.setMinimumWidth(320)
        self.api_key_input.setFixedHeight(32)
        self.api_key_input.textChanged.connect(self.update_api_key)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        center_layout.addLayout(api_key_layout)
        center_layout.addSpacing(28)

        # Skill Level slider
        skill_layout = QHBoxLayout()
        skill_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        skill_label = QLabel("Skill Level:")
        skill_label.setFixedWidth(110)
        self.skill_slider.setRange(1, 20)
        self.skill_slider.setValue(self.skill_level)
        self.skill_slider.setMinimumWidth(260)
        self.skill_slider.setFixedHeight(28)
        self.skill_slider.valueChanged.connect(self.update_skill)
        self.skill_value_label.setText(str(self.skill_level))
        self.skill_value_label.setFixedWidth(40)
        self.skill_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        skill_layout.addWidget(skill_label)
        skill_layout.addWidget(self.skill_slider)
        skill_layout.addWidget(self.skill_value_label)
        center_layout.addLayout(skill_layout)
        center_layout.addSpacing(18)

        # Depth slider
        depth_layout = QHBoxLayout()
        depth_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        depth_label = QLabel("Depth:")
        depth_label.setFixedWidth(110)
        self.depth_slider.setRange(1, 30)
        self.depth_slider.setValue(self.depth)
        self.depth_slider.setMinimumWidth(260)
        self.depth_slider.setFixedHeight(28)
        self.depth_slider.valueChanged.connect(self.update_depth)
        self.depth_value_label.setText(str(self.depth))
        self.depth_value_label.setFixedWidth(40)
        self.depth_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(self.depth_slider)
        depth_layout.addWidget(self.depth_value_label)
        center_layout.addLayout(depth_layout)
        center_layout.addSpacing(28)

        log_label = QLabel("Logs:")
        log_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        center_layout.addWidget(log_label)
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(100)
        self.log_text.setMinimumWidth(400)
        center_layout.addWidget(self.log_text)

        customize_btn = QPushButton("Personnaliser l'UI")
        customize_btn.setMinimumWidth(180)
        customize_btn.setFixedHeight(32)
        customize_btn.clicked.connect(self.open_ui_customization)
        center_layout.addWidget(customize_btn)

        opt_main_layout.addWidget(center_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        opt_main_layout.addStretch(3)

        # Ajout des pages au stack
        self.stack.addWidget(dashboard_page)
        self.stack.addWidget(options_page)
        main_layout.addWidget(self.stack)

        # Connexion des boutons
        self.dashboard_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.options_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        # Par défaut, afficher Dashboard
        self.stack.setCurrentIndex(0)

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
        color = "#ff6b6b" if is_error else "#00ff99"
        self.log_text.append(f'<span style="color: {color}">[{timestamp}]</span> {message}')
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

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

    def open_ui_customization(self):
        dlg = UiCustomizationDialog(self)
        dlg.exec()

    def apply_ui_customization(self, theme, color, font_size):
        # Applique le style selon le thème et la couleur
        if theme == "Clair":
            self.setStyleSheet(f'''
                QMainWindow, QWidget {{
                    background: #f5f5f5;
                    color: {color};
                    font-family: "Orbitron", "Montserrat", Arial, sans-serif;
                    font-size: {font_size}px;
                }}
                QLabel {{ color: {color}; font-weight: bold; }}
                QPushButton {{ background: #fff; color: {color}; border: 2px solid {color}; border-radius: 8px; padding: 8px 16px; font-weight: bold; }}
                QPushButton:hover {{ background: {color}; color: #fff; }}
                QSlider::groove:horizontal {{ border: 1px solid {color}; height: 8px; background: #eee; border-radius: 4px; }}
                QSlider::handle:horizontal {{ background: {color}; border: 2px solid {color}; width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; }}
                QTextEdit {{ background: #fff; color: {color}; border: 1px solid {color}; border-radius: 8px; font-family: "Consolas", "Courier New", monospace; font-size: {font_size-1}px; }}
            ''')
        else:
            self.setStyleSheet(f'''
                QMainWindow, QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0f0d, stop:1 #101a14);
                    color: {color};
                    font-family: "Orbitron", "Montserrat", Arial, sans-serif;
                    font-size: {font_size}px;
                }}
                QLabel {{ color: {color}; font-weight: bold; }}
                QPushButton {{ background: #101a14; color: {color}; border: 2px solid {color}; border-radius: 8px; padding: 8px 16px; font-weight: bold; }}
                QPushButton:hover {{ background: {color}; color: #101a14; }}
                QSlider::groove:horizontal {{ border: 1px solid {color}; height: 8px; background: #222; border-radius: 4px; }}
                QSlider::handle:horizontal {{ background: {color}; border: 2px solid {color}; width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; }}
                QTextEdit {{ background: rgba(10, 15, 13, 0.8); color: {color}; border: 1px solid {color}; border-radius: 8px; font-family: "Consolas", "Courier New", monospace; font-size: {font_size-1}px; }}
            ''')
        # Applique la police à tous les widgets principaux
        font = QFont("Orbitron", font_size)
        self.setFont(font)

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