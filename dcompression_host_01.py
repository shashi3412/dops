import os
import bsdiff4
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from Cryptodome.Random import get_random_bytes
import hashlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor


class PatchDemoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobis Software Update Process")
        self.setGeometry(100, 100, 400, 250)

        self.phase_labels = ['Decrypting Patch File', 'Generating Modified File', 'Data Integrity Check']
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

    def update_status(self, status, color=None):
        if color:
            self.label_status.setStyleSheet(f"color: {color.name()};")
        self.label_status.setText(status)

    def complete_execution(self, signature_match):
        if signature_match:
            self.update_status("Data integrity check successful", QColor("green"))
        else:
            self.update_status("Data integrity check Failed(Signature check failed)", QColor("red"))


class PatchThread(QThread):
    progress_update = pyqtSignal(int, int)
    status_update = pyqtSignal(str, QColor)
    finished = pyqtSignal(bool)

    def run(self):
        key = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF\xFE\xDC\xBA\x98\x76\x54\x32\x10'
        encrypted_file_path = 'patch_file_encrypted.bin'
        decrypted_file_path = os.path.splitext(encrypted_file_path)[0] + '_decrypted.bin'
        self.decrypt_file(encrypted_file_path, decrypted_file_path, key)
        self.status_update.emit("Patch file decrypted", QColor("black"))
        self.progress_update.emit(0, 100)

        original_file_path = 'original.bin'
        modified_file_path = 'modified_sign.bin'
        self.apply_patch(original_file_path, decrypted_file_path, modified_file_path)
        self.status_update.emit("Modified file generated", QColor("black"))
        self.progress_update.emit(1, 100)

        modified_file_without_sign_path = 'modified_Woutsign.bin'
        self.remove_last_32_bytes(modified_file_path, modified_file_without_sign_path)
        self.status_update.emit("calculating Data Integrity Check", QColor("black"))
        self.progress_update.emit(2, 100)

        received_signature = self.read_last_32_bytes(modified_file_path)
        calculated_signature = self.calculate_signature(modified_file_without_sign_path)
        signature_match = self.compare_signatures(received_signature, calculated_signature)
        self.finished.emit(signature_match)

    def decrypt_file(self, encrypted_file_path, decrypted_file_path, key):
        cipher = AES.new(key, AES.MODE_ECB)
        with open(encrypted_file_path, 'rb') as file:
            ciphertext = file.read()
            decrypted_data = cipher.decrypt(ciphertext)
            plaintext = unpad(decrypted_data, AES.block_size)

        with open(decrypted_file_path, 'wb') as file:
            file.write(plaintext)

    def apply_patch(self, old_file_path, patch_file_path, new_file_path):
        with open(old_file_path, 'rb') as old_file, open(new_file_path, 'wb') as new_file, open(patch_file_path, 'rb') as patch_file:
            old_data = old_file.read()
            patch_data = patch_file.read()
            new_data = bsdiff4.patch(old_data, patch_data)
            new_file.write(new_data)

    def read_last_32_bytes(self, file_path):
        with open(file_path, 'rb') as file:
            file.seek(-32, 2)
            last_32_bytes = file.read()
            return last_32_bytes

    def calculate_signature(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read()
            signature = hashlib.sha256(data).digest()
            return signature

    def remove_last_32_bytes(self, file_path, output_file_path):
        with open(file_path, 'rb') as file:
            content = file.read()[:-32]

        with open(output_file_path, 'wb') as output_file:
            output_file.write(content)

    def compare_signatures(self, received_signature, calculated_signature):
        return received_signature == calculated_signature


if __name__ == "__main__":
    app = QApplication([])
    window = PatchDemoApp()
    window.show()
    app.exec_()
