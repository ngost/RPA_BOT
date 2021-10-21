import time
import asyncio
import PyQt5
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QByteArray
from PyQt5.QtGui import QIcon, QFont, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLayout, QBoxLayout, \
    QGridLayout, QLabel, QProgressBar, QLineEdit
from PyQt5 import QtCore
import sys
from pynput import mouse
import json
import threading, socket

serverIP = "161.122.112.178"
serverPort = "9999"

class MacroClient(QWidget):

    class Worker(QWidget):
        finished = pyqtSignal()

        def run(self):
            MacroClient.tryConnect(self, self.ip, self.port)

        def __init__(self, ip, port, parent=None):
            super().__init__(parent)
            self.ip = ip
            self.port = port

    def __init__(self, parent=None):
        super().__init__(parent)

        self.isConnected = False

        # 녹화 리스너
        self.setStyleSheet("background-color: #494949;")
        self.setWindowTitle("MacroClient")
        self.resize(1280, 840)

        # self.state_ = QLabel("상태")
        # self.state_.setAlignment(QtCore.Qt.AlignCenter)
        # self.state_.setFont(QFont('Arial', 10))
        # self.state_.setStyleSheet('QLabel { color : white;}')

        # UI 기본 요소 setting
        self.ip_title = QLabel("IP ADDRESS")
        self.ip_title.setStyleSheet('QLabel {color : white;}')
        self.ip_title.setAlignment(QtCore.Qt.AlignCenter)
        self.port_title = QLabel("PORT")
        self.port_title.setStyleSheet('QLabel {color : white;}')
        self.port_title.setAlignment(QtCore.Qt.AlignCenter)
        self.ip_edit_text = QLineEdit(serverIP)
        self.port_edit_text = QLineEdit(serverPort)
        self.port_edit_text.setStyleSheet('QLineEdit { color : white;}')
        self.ip_edit_text.setAlignment(QtCore.Qt.AlignCenter)
        self.ip_edit_text.setStyleSheet('QLineEdit { color : white;}')
        self.port_edit_text.setAlignment(QtCore.Qt.AlignCenter)

        self.state_msg = QLabel("연결 안됨")
        self.state_msg.setFont(QFont('Arial', 10))
        self.state_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.state_msg.setStyleSheet('QLabel { color : white;}')

        #label
        self.loading_label = QLabel()
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        self.loading_label.setGeometry(QtCore.QRect(25, 25, 200, 200))
        self.loading_label.setMinimumSize(QtCore.QSize(200, 200))
        self.loading_label.setMaximumSize(QtCore.QSize(200, 200))

        # Loading the GIF
        self.movie = QMovie("./imgs/loading2.gif",QByteArray(),self)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.loading_label.setMovie(self.movie)

        self.btn_conn = QPushButton("Try Connect")
        self.btn_conn.resize(300,300)
        self.btn_conn.setIcon(QIcon('./imgs/try_conn_btn.png'))
        self.btn_conn.setStyleSheet('QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {color: white;}')

        layout = QGridLayout()
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 1)
        layout.setRowStretch(6, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)

        layout.addWidget(self.ip_title,0,1)
        layout.addWidget(self.port_title,0,3)
        layout.addWidget(self.ip_edit_text,1,1)
        layout.addWidget(self.port_edit_text,1,3)

        layout.addWidget(self.loading_label, 2, 2)
        # layout.addWidget(self.state_, 1, 2)
        layout.addWidget(self.state_msg, 3, 2)
        layout.addWidget(self.btn_conn, 4, 2)

        self.setLayout(layout)


        self.btn_conn.clicked.connect(self.on_try_connection_click)

    def on_try_connection_click(self):
        self.startLoadingAnimation()
        self.thread = QThread()
        self.worker = self.Worker(self.ip_edit_text.text(),self.port_edit_text.text())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()

#     def btn_conn_Clicked(self):
#         if self.btn_conn.text() == "Stop Connecting":
#             #연결 중단하기
#             self.stopLoadingAnimation(False)
#         else:
#             self.startLoadingAnimation()
#             self.tryConnect()
# #            self.startListen()

    def startLoadingAnimation(self):
        self.state_msg.setText("연결중")
        self.loading_label.setVisible(True)
        self.movie.start()
        self.btn_conn.setStyleSheet('QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#FF9800; color: white;}')
        self.btn_conn.setText("Stop Connecting")

    # Stop Animation(According to need)
    def stopLoadingAnimation(self, isConnected):
        self.loading_label.setVisible(False)
        if isConnected is True:
            self.state_msg.setText("연결 완료")
            self.btn_conn.setStyleSheet(
                'QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#03A9F4; color: white;}')
            self.btn_conn.setText("Stop Connecting")
            self.movie.stop()
            self.isConnected = True
        else:
            try:
                self.state_msg.setText("연결 안됨")
                self.btn_conn.setText("Start Connecting")
                self.btn_conn.setStyleSheet(
                    'QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#FF9800; color: white;}')
                self.movie.stop()
                self.isConnected = False
            except:
                pass


    def print_test(self):
        print("checking")

    def tryConnect(self, ip, port):

        print("---Try Connect---")
        print(ip)
        print(port)
        print("---Try Connect---")

        try:
            #background 동작을 위한 QThread와 Worker 생성
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, int(port)))  # 서버에 접속
            self.th = threading.Thread(target=binder, args=(self.client_socket,))
            # th.daemon = True
            self.th.start()

        except ConnectionRefusedError as e:
            win.stopLoadingAnimation(False)
            print(e)


def is_socket_closed(sock: socket.socket) -> bool:
    try:
        RECV_BUFFER_SIZE = 1024
        buff = memoryview(bytearray(RECV_BUFFER_SIZE))
        sock.setblocking(0)

        data = sock.recv_into(buff, RECV_BUFFER_SIZE, 0)

        if data == 0:
            return True
    except BlockingIOError:
        return False  # 들어온 데이터가 없음
    except ConnectionResetError:
        print("reset")
        return True  # socket was closed for some other reason
    except TypeError:
        print(data)
        print("type error")
        return True
    except Exception as e:
        print("exception")
        #logger.exception("unexpected exception when checking if a socket is closed")
        return False
    return False



#Connection 되었을 때 Routine
def binder(client_socket):
    win.stopLoadingAnimation(True)
    client_socket.send('ping'.encode())  # 서버에 메시지 전송
    while True:
        try:
            rdata = client_socket.recv(256)
            print("receive : ", rdata.decode('utf8'), '\n')

            if is_socket_closed(client_socket):
                print("Client 응답 없음")
                win.stopLoadingAnimation(False)
                break
            else:
                pass  # print("연결 정상")

            if win.isConnected is False:
                break

        except BlockingIOError as block_error:
            print("들어온 데이터가 없음")
        time.sleep(2)


if __name__ == '__main__':
        app = QApplication(sys.argv)
        win = MacroClient()
        win.show()
        sys.exit(app.exec_())