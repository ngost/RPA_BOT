import time

from PyQt5.QtWidgets import QApplication,QWidget,QTextEdit,QVBoxLayout,QPushButton
import sys
import keyboard
import pyautogui
import PyQt5
from pynput import mouse



class TextEditDemo(QWidget):
        def __init__(self,parent=None):
                super().__init__(parent)

                #녹화 리스너
                self.listener = mouse.Listener(on_click=self.on_click)
                
                self.setWindowTitle("QTextEdit")
                self.resize(1280,840)

                self.textEdit = QTextEdit()
                self.btnPress1 = QPushButton("START RECORD")
                self.btnPress2 = QPushButton("STOP RECORD")
                self.btnPress3 = QPushButton("기록 초기화")
                self.btnPress4 = QPushButton("EXPORT")

                layout = QVBoxLayout()
                layout.addWidget(self.textEdit)
                layout.addWidget(self.btnPress1)
                layout.addWidget(self.btnPress2)
                layout.addWidget(self.btnPress3)
                layout.addWidget(self.btnPress4)
                self.setLayout(layout)

                self.btnPress1.clicked.connect(self.btnPress1_Clicked)
                self.btnPress2.clicked.connect(self.btnPress2_Clicked)
                self.btnPress3.clicked.connect(self.btnPress3_Clicked)
                self.btnPress4.clicked.connect(self.btnPress4_Clicked)

        def btnPress1_Clicked(self):
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            self.textEdit.append('기록 시작')

        def btnPress2_Clicked(self):
            self.listener.stop()
            self.textEdit.append('기록 종료')

            
        def btnPress3_Clicked(self):
            self.textEdit.clear()


        def btnPress4_Clicked(self):
            import os
            desktop_path = ''

            if os.name == 'nt':
                desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
            elif os.name == 'posix':
                desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

            with open(os.path.join(desktop_path, "record.txt"), "w") as file1:
                toFile = self.textEdit.toPlainText()
                file1.write(toFile)

        def on_click(self, x, y, button, pressed):
            import datetime
            if button == mouse.Button.left:
                self.textEdit.append(str((x, y))+ '왼쪽 마우스 클릭, Pressed' + str(pressed) + str(datetime.datetime.now()))

                #print('{} at {}'.format('Pressed Left Click' if pressed else 'Released Left Click', (x, y)))
            else:
                self.textEdit.append(str((x, y))+ '오른쪽 마우스 클릭, Pressed' + str(pressed) + str(datetime.datetime.now()))


if __name__ == '__main__':
        app = QApplication(sys.argv)
        win = TextEditDemo()
        win.show()
        sys.exit(app.exec_())






