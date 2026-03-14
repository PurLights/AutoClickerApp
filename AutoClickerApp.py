import threading
import time
import sys
import pyautogui
import keyboard
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QVBoxLayout, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings

class AutoClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyClicker", "AutoClickerApp")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #f0f0f0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }

            QLineEdit, QComboBox {
                background-color: #2e2e3e;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
                color: #ffffff;
            }

            QPushButton {
                background-color: #A019C2;
                border: none;
                padding: 8px;
                border-radius: 6px;
            }
-BC/";l
           QPushButton:hover {
                background-color: #E099F2;
            }
        """)
        self.setWindowTitle("PyQt6 Autoclicker with Keyboard + Interval Input")
        self.setGeometry(100, 100, 400, 320)

        self.clicking = False
        self.hotkey_registered = False

        # Interval input
        self.interval_label = QLabel("Interval (seconds, min 0.01):")
        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("e.g., 1.0")
        self.interval_input.setText("1.0")
        self.cps_display = QLabel("→ 1.00 clicks/sec")

        self.interval_input.textChanged.connect(self.update_cps_display)

        # Key to press
        self.key_label = QLabel("Key to press (optional):")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("e.g., a, enter, space")

        # Action type
        self.action_label = QLabel("Action:")
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Mouse Click", "Key Press", "Both"])
    # Hotkey input
        self.hotkey_label = QLabel("Toggle Hotkey (e.g., f6):")
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText("f6")

        # Buttons
        self.start_button = QPushButton("Register Hotkey")
        self.stop_button = QPushButton("Stop Clicking")

        self.start_button.clicked.connect(self.register_hotkey)
        self.stop_button.clicked.connect(self.stop_clicking)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_input)
        layout.addWidget(self.cps_display)
        layout.addWidget(self.key_label)
        layout.addWidget(self.key_input)
        layout.addWidget(self.action_label)
        layout.addWidget(self.action_combo)
        layout.addWidget(self.hotkey_label)
        layout.addWidget(self.hotkey_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.load_settings()
        self.auto_register_hotkey()

    def update_cps_display(self):
        try:
            val = float(self.interval_input.text())
            if val >= 0.01:
                cps = round(1 / val, 2)
                self.cps_display.setText(f"→ {cps:.2f} clicks/sec")
            else:
                self.cps_display.setText("⚠ Minimum is 0.01 sec")
        except ValueError:
            self.cps_display.setText("⚠ Enter a number")

    def register_hotkey(self):
        if self.hotkey_registered:
            keyboard.unhook_all_hotkeys()
            self.hotkey_registered = False

        hotkey = self.hotkey_input.text().strip().lower()
        if not hotkey:
            QMessageBox.warning(self, "Invalid Hotkey", "Please enter a valid hotkey.")
            return

        try:
            keyboard.add_hotkey(hotkey, self.toggle_clicking)
            self.hotkey_registered = True
            QMessageBox.information(self, "Hotkey Registered", f"Hotkey '{hotkey}' registered.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to register hotkey: {e}")

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def auto_register_hotkey(self):
        hotkey = self.hotkey_input.text().strip().lower()
        if not hotkey:
            return

        try:
            keyboard.add_hotkey(hotkey, self.toggle_clicking)
            self.hotkey_registered = True
        except Exception as e:
            print(f"[!] Failed to auto-register hotkey: {e}")

    def start_clicking(self):
        try:
            interval = float(self.interval_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for interval.")
            return

        if interval < 0.01:
            QMessageBox.warning(self, "Too Fast", "Minimum interval is 0.01 seconds.")
            return

        self.clicking = True
        threading.Thread(target=self.click_loop, args=(interval,), daemon=True).start()

    def stop_clicking(self):
        self.clicking = False

    def click_loop(self, interval):
        key = self.key_input.text().strip().lower()
        action = self.action_combo.currentText()

        while self.clicking:
            if action == "Mouse Click":
                pyautogui.click()
            elif action == "Key Press" and key:
                keyboard.send(key)
            elif action == "Both":
                pyautogui.click()
                if key:
                    keyboard.send(key)
            time.sleep(interval)

    def load_settings(self):
        self.interval_input.setText(self.settings.value("interval", "1.0"))
        self.key_input.setText(self.settings.value("key_to_press", ""))
        self.hotkey_input.setText(self.settings.value("hotkey", "f6"))
        self.action_combo.setCurrentText(self.settings.value("action", "Mouse Click"))
        self.update_cps_display()

    def closeEvent(self, event):
        self.settings.setValue("interval", self.interval_input.text())
        self.settings.setValue("key_to_press", self.key_input.text())
        self.settings.setValue("hotkey", self.hotkey_input.text())
        self.settings.setValue("action", self.action_combo.currentText())
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.jpg"))
    window = AutoClicker()
    window.show()
    sys.exit(app.exec())