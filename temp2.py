import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                           QComboBox, QMessageBox, QScrollBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
import speech_recognition as sr
import pyttsx3
from temp1 import process_command  # Import the process_command function

class VoiceThread(QThread):
    """Thread for handling voice recognition to keep GUI responsive"""
    command_detected = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer
        self.is_listening = True
        
    def run(self):
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    self.status_update.emit("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                try:
                    command = self.recognizer.recognize_google(audio).lower()
                    self.command_detected.emit(command)
                except sr.UnknownValueError:
                    self.status_update.emit("Could not understand audio")
                except sr.RequestError:
                    self.status_update.emit("Could not request results")
            except Exception as e:
                self.status_update.emit(f"Error: {str(e)}")
                
    def stop(self):
        self.is_listening = False
        self.wait()

class JarvisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Assistant")
        self.setMinimumSize(800, 600)
        
        # Initialize speech components
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.voice_thread = None
        
        # Set dark theme colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
            }
            QTextEdit {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QComboBox {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3b3b3b;
                color: #ffffff;
            }
        """)
        
        self.setup_ui()
    
    def handle_mode_change(self, mode):
        """Handle changes between text and voice modes"""
        if mode == "Voice Mode":
            self.input_area.setEnabled(False)
            self.send_button.setEnabled(False)
            self.voice_button.setEnabled(True)
            self.status_label.setText("Voice Mode Active")
        else:
            self.input_area.setEnabled(True)
            self.send_button.setEnabled(True)
            self.voice_button.setEnabled(False)
            if self.voice_thread:
                self.stop_voice_recognition()
            self.status_label.setText("Text Mode Active")
    
    def toggle_voice_recognition(self):
        """Toggle voice recognition on/off"""
        if self.voice_thread and self.voice_thread.isRunning():
            self.stop_voice_recognition()
        else:
            self.start_voice_recognition()
    
    def start_voice_recognition(self):
        """Start voice recognition"""
        self.voice_button.setText("Stop Voice")
        self.voice_thread = VoiceThread(self.recognizer)
        self.voice_thread.command_detected.connect(self.handle_voice_command)
        self.voice_thread.status_update.connect(self.update_status)
        self.voice_thread.start()
        self.status_label.setText("Voice Recognition Active")
    
    def stop_voice_recognition(self):
        """Stop voice recognition"""
        if self.voice_thread:
            self.voice_thread.stop()
            self.voice_thread = None
        self.voice_button.setText("Start Voice")
        self.status_label.setText("Voice Recognition Stopped")
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("Jarvis AI Assistant")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #00ff00;")
        layout.addWidget(title)
        
        # Add mode selection
        mode_layout = QHBoxLayout()
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Text Mode", "Voice Mode"])
        self.mode_selector.currentTextChanged.connect(self.handle_mode_change)
        mode_layout.addWidget(QLabel("Interaction Mode:"))
        mode_layout.addWidget(self.mode_selector)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Add output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet("""
            background-color: #2b2b2b;
            color: #00ff00;
            border: 1px solid #555555;
            padding: 10px;
            font-family: Consolas, monospace;
            font-size: 14px;
        """)
        layout.addWidget(self.output_display)
        
        # Add input area
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Type your command here...")
        self.input_area.setMaximumHeight(100)
        self.input_area.setStyleSheet("""
            background-color: #3b3b3b;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 10px;
            font-family: Consolas, monospace;
            font-size: 14px;
        """)
        layout.addWidget(self.input_area)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send Command")
        self.send_button.clicked.connect(self.handle_command)
        
        self.voice_button = QPushButton("Start Voice")
        self.voice_button.clicked.connect(self.toggle_voice_recognition)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_output)
        
        for button in [self.send_button, self.voice_button, self.clear_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4a4a4a;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 10px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            button_layout.addWidget(button)
        
        layout.addLayout(button_layout)
        
        # Add status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            padding: 5px;
            background-color: #3b3b3b;
            color: #00ff00;
            border: 1px solid #555555;
        """)
        layout.addWidget(self.status_label)
    
    def handle_command(self):
        """Handle text commands"""
        command = self.input_area.toPlainText().strip()
        if command:
            self.output_display.append(f"\nYou: {command}")
            try:
                from temp1 import process_command  # Import the correct process_command
                response = process_command(command, is_voice=False)
                if response:
                    self.output_display.append(f"Jarvis: {response}")
            except Exception as e:
                self.output_display.append(f"Jarvis: Error processing command - {str(e)}")
            self.input_area.clear()
            # Scroll to bottom
            scrollbar = self.output_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def handle_voice_command(self, command):
        """Handle voice commands"""
        self.output_display.append(f"\nVoice Command: {command}")
        try:
            from temp1 import process_command  # Import the correct process_command
            response = process_command(command, is_voice=True)
            if response:
                self.output_display.append(f"Jarvis: {response}")
        except Exception as e:
            self.output_display.append(f"Jarvis: Error processing command - {str(e)}")
        # Scroll to bottom
        scrollbar = self.output_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.setText(message)
    
    def clear_output(self):
        """Clear the output display"""
        self.output_display.clear()
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.voice_thread:
            self.stop_voice_recognition()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = JarvisGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()