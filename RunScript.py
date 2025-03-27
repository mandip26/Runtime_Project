import sys
import os
import threading
import psutil
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from time import sleep, time

# Functions to run Streamlit and Windows app
def run_streamlit():
    try:
        python_path = os.path.join(os.getcwd(), "bin", "Scripts", "python.exe")
        os.system(f"{python_path} -m streamlit run app.py --server.headless true")
    except Exception as e:
        print(f"Streamlit error: {e}")

def run_windows():
    try:
        streamlit_path = os.path.join(os.getcwd(), "StreamlitApp.exe")
        os.system(f"{streamlit_path}")
    except Exception as e:
        print(f"Windows app error: {e}")

# Function to terminate Streamlit
def terminate_streamlit():
    try:
        for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
            cmdline = proc.info.get("cmdline")
            if cmdline and "streamlit" in cmdline:
                proc.terminate()
        print("Streamlit terminated.")
    except Exception as e:
        print(f"Error terminating Streamlit: {e}")

# Main PyQt6 application class
def window_terminate():
    tasklist_output = os.popen('tasklist /FI "IMAGENAME eq StreamlitApp.exe"').read()
    lines = tasklist_output.splitlines()
    if len(lines) > 3:
        pid = lines[3].split()[1]
        psutil.Process(int(pid)).terminate()
    else:
        print("Streamlit app not found in tasklist.")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.run_button = None
        self.stop_button = None
        self.user_interface()

    def user_interface(self):
        self.setWindowTitle("Streamlit Controller")
        self.setGeometry(100, 100, 400, 300)

        # Set window background and alignment
        self.setStyleSheet("background-color: #f5f5f5;")
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Modern Button Styles
        button_style = """
            QPushButton {
                color: white;
                background-color: #0078d7;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003f6b;
            }
            QPushButton:disabled {
                background-color: #d3d3d3;
                color: #7f7f7f;
            }
        """

        # Run Button
        self.run_button = QPushButton("Run")
        self.run_button.setStyleSheet(button_style)
        self.run_button.clicked.connect(self.run_applications)
        layout.addWidget(self.run_button)

        # Stop Button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.setEnabled(False)  # Initially disabled
        self.stop_button.clicked.connect(self.stop_streamlit)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def run_applications(self):
        try:
            # Disable Run button and enable Stop button
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            streamlit_thread = threading.Thread(target=run_streamlit)
            windows_thread = threading.Thread(target=run_windows)

            # Start threads
            streamlit_thread.start()
            sleep(2)  # Ensures Streamlit starts first
            windows_thread.start()

            # QMessageBox.information(self, "Success", "Applications started successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def stop_streamlit(self):
        try:
            terminate_streamlit()
            window_terminate()
            # QMessageBox.information(self, "Success", "Streamlit stopped successfully!")
            # Reset buttons
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

# Entry point of the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    sys.exit(app.exec())
