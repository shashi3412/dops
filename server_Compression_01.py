import os
import hashlib
import bsdiff4
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QProgressBar, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor


class PatchDemoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hobis Software Update Process")
        self.setGeometry(100, 100, 400, 250)

        self.phase_labels = ['Data Integrity', 'Data Optimization', 'Secure communication']
        self.progress_bars = []

        self.label_status = QLabel()
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setText("Initializing")

        layout = QVBoxLayout()
        layout.addWidget(self.label_status)

        for phase_label in self.phase_labels:
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(QLabel(phase_label))
            layout.addWidget(progress_bar)
            self.progress_bars.append(progress_bar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.thread = PatchThread()
        self.thread.progress_update.connect(self.update_progress)
        self.thread.status_update.connect(self.update_status)
        self.thread.finished.connect(self.complete_execution)
        self.thread.start()

    def update_progress(self, phase, value):
        self.progress_bars[phase].setValue(value)

    def update_status(self, status):
        self.label_status.setText(status)

    def complete_execution(self, success):
        if success:
            self.update_status("Process Completed")
        else:
            self.update_status("Process Failed")


class PatchThread(QThread):
    progress_update = pyqtSignal(int, int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def run(self):
        try:
            file_path = 'modified.bin'
            signature = self.calculate_signature(file_path)
            self.status_update.emit("Data integrity check included")
            self.progress_update.emit(0, 100)

            # Append the signature to the modified file
            with open(file_path, 'ab') as file:
                file.write(signature)

            old_hex_file_name = 'original.bin'
            new_hex_file_name = file_path
            patch_file_name = 'patch_file.bin'
            self.create_patch(old_hex_file_name, new_hex_file_name, patch_file_name)
            self.status_update.emit("Data optimization done")
            self.progress_update.emit(1, 100)

            key = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF\xFE\xDC\xBA\x98\x76\x54\x32\x10'
            encrypted_file_path = 'patch_file_encrypted.bin'
            self.encrypt_file(patch_file_name, encrypted_file_path, key)
            self.status_update.emit("Secured Communication included")
            self.progress_update.emit(2, 100)

            self.finished.emit(True)
        except Exception as e:
            print("Error:", str(e))
            self.finished.emit(False)

    def calculate_signature(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read()
        signature = hashlib.sha256(data).digest()
        return signature

    def create_patch(self, old_hex_file_name, new_hex_file_name, patch_file_name):
        try:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            old_hex_file_path = os.path.join(script_directory, old_hex_file_name)
            new_hex_file_path = os.path.join(script_directory, new_hex_file_name)
            patch_file_path = os.path.join(script_directory, patch_file_name)

            with open(old_hex_file_path, 'rb') as old_file, open(new_hex_file_path, 'rb') as new_file, open(patch_file_path, 'wb') as patch_file:
                old_data = old_file.read()
                new_data = new_file.read()
                diff_data = bsdiff4.diff(old_data, new_data)
                patch_file.write(diff_data)

            print("Patch file created successfully.")

        except FileNotFoundError:
            print("One or more files not found.")
        except IsADirectoryError:
            print("Specified file is a directory.")
        except PermissionError:
            print("Insufficient permissions to access files.")
        except Exception as e:
            print("Error creating patch file:", str(e))

    def encrypt_file(self, file_path, encrypted_file_path, key):
        cipher = AES.new(key, AES.MODE_ECB)

        with open(file_path, 'rb') as file:
            plaintext = file.read()

        padded_plaintext = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)

        with open(encrypted_file_path, 'wb') as file:
            file.write(ciphertext)

        print(f"File encrypted and saved as '{encrypted_file_path}'.")


if __name__ == '__main__':
    import os
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication([])
    window = PatchDemoApp()
    window.show()
    app.exec_()
