import socket
import time
import subprocess
import os
import hashlib
import bsdiff4
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from threading import Timer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPlainTextEdit, QMessageBox
from datetime import datetime

state = 0
Run = 0
Count = 0
Invoke = 0
Hold = 0
stage = 0

class Ui_MainWindow(object):
    
    def Socket_Init(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("192.168.1.48", 5000))

    def execute_script(self):
        subprocess.run(["python", "comm.py"])

    def getDateTime(self):
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return timestamp_str

    def client_back_ground(self):
        global stage
        if stage == 0:
            stage = 1
            message = "<UP>New Features and Software Updates available from Mobis"
            self.s.send(message.encode("utf-8"))
            print("Sending update to vehicle")
        elif stage == 1:
            stage = 2
            
        message_rec = self.s.recv(1024).decode("utf-8")
        print(message_rec)
        if message_rec == "yes":
            print("Executing script...")
            self.execute_script()
            print("Script execution completed.")

        self.timer1 = Timer(2, self.client_back_ground)
        self.timer1.start()


    def Blink(self):
        global state
        global prev
        global Run
        global Count
        global Hold 
        
        if (state != 10):
            if(Hold != 1):
                Count =  Count + 1

        if(state == 0):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps0.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps1.png"))

        elif(state == 1):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps1.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps2.png"))
        elif(state == 2):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps2.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps3.png"))
        elif(state == 3):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps3.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps4.png"))
        elif(state == 4):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps4.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps5.png"))
            
        elif(state == 5):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps5.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps6.png"))
        elif(state == 6):
            if(Run == 0):
                Run = 1
                self.label.setPixmap(QtGui.QPixmap("DevOps6.png"))
            else :
                Run = 0
                self.label.setPixmap(QtGui.QPixmap("DevOps7.png"))
        if(Count < 6):
            state = 0
        elif (Count < 12):
            state = 1
        elif (Count < 18):
            state = 2
        elif (Count < 24):
            state = 3
        elif (Count < 30):
            state = 4
        elif (Count < 36):
            state = 5
        elif (Count < 42):
            state = 6
        elif(Count == 49):
            if(state != 10):
                state = 10
                self.label.setPixmap(QtGui.QPixmap("DevOps7.png"))
        else:
            self.timer.cancel()

        self.timer10 = Timer(0.5, self.Blink)
        self.timer10.start()


    def task(self):
        global Invoke
        global state
        global Hold
        if(state == 4):
            if (Invoke == 0):
                print("Task Invoked")
                Invoke = 1
                Hold = 1
                self.run()
                self.Socket_Init()
                self.client_back_ground()
                Hold = 0
        self.timer = Timer(0.5, self.task)
        self.timer.start()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 520)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 800, 500))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("DevOps0.png"))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.textedit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.textedit.appendPlainText("Server Log")
        self.textedit.setStyleSheet("""
                                    QPlainTextEdit {
                                        background-color: #ffffff;
                                        color: #2049C4;
                                        border: 1px solid #555;
                                        border-radius: 10px;
                                        font-size: 30px;
                                    }
                                """)
        self.textedit.setGeometry(QtCore.QRect(900, 15, 950, 480))
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.Blink()
        self.task()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
    
    
    def run(self):
        try:
            timestmp = self.getDateTime()
            msg = str(timestmp) + str(": Data Integrity Check(Signature) Initiated")
            self.textedit.appendPlainText(msg)

            file_path = 'modified.bin'
            signature = self.calculate_signature(file_path)
            
            # Append the signature to the modified file
            with open(file_path, 'ab') as file:
                file.write(signature)

            #print("Data Integrity Check(Signature) Included")
            timestmp = self.getDateTime()
            msg = str(timestmp) + str(" : Data Integrity Check(Signature) Included")
            self.textedit.appendPlainText(msg)

            timestmp = self.getDateTime()
            msg = str(timestmp) + str(": Data Compression Initiated")
            self.textedit.appendPlainText(msg)
            
            old_hex_file_name = 'original.bin'
            Orgfile_size_in_bytes = os.path.getsize(old_hex_file_name)
            # convert to MB
            Orgfile_size_in_mb = Orgfile_size_in_bytes / (1024 * 1024)
            #print("Original Bin file size:", Orgfile_size_in_mb)
            timestmp = self.getDateTime()
            msg = str(timestmp) + str(" : Original Bin file size - ") + str(Orgfile_size_in_mb) + str(" MB")
            self.textedit.appendPlainText(msg)

            new_hex_file_name = file_path
            patch_file_name = 'patch_file.bin'
            #self.create_patch(old_hex_file_name, new_hex_file_name, patch_file_name)
            time.sleep(1)
            print("Data Compression Done")
            timestmp = self.getDateTime()
            msg = str(timestmp) + str(" : Data Compression Done")
            self.textedit.appendPlainText(msg)
            
            Comfile_size_in_bytes = os.path.getsize(patch_file_name)
            # convert to MB
            Comfile_size_in_mb = Comfile_size_in_bytes / (1024 * 1024)
            #print("Compressed file Size:", Comfile_size_in_mb)
            timestmp = self.getDateTime()
            msg = str(timestmp) + str(" : Compressed file Size - ") + str(Comfile_size_in_mb) + str(" MB")
            self.textedit.appendPlainText(msg)

            timestmp = self.getDateTime()
            msg = str(timestmp) + str(" : Encryption Initiated")
            self.textedit.appendPlainText(msg)

            key = b'\x01\x23\x45\x67\x89\xAB\xCD\xEF\xFE\xDC\xBA\x98\x76\x54\x32\x10'
            encrypted_file_path = 'patch_file_encrypted.bin'
            self.encrypt_file(patch_file_name, encrypted_file_path, key)
            #print("Encryption Done")
            timestmp = self.getDateTime()
            msg = str(timestmp) + str(" : Encryption Done")
            self.textedit.appendPlainText(msg)
    
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

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    MainWindow.show()
    sys.exit(app.exec_())
    
