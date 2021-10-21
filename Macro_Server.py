import time
import asyncio
import PyQt5
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QByteArray
from PyQt5.QtGui import QIcon, QFont, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QLayout, QBoxLayout, \
    QGridLayout, QLabel, QProgressBar
from PyQt5 import QtCore
import sys
from pynput import mouse
import json
import threading, socket

import logging


logger = logging.getLogger(__name__)

class MacroServer(QWidget):

    class Worker(QObject):
        finished = pyqtSignal()

        def run(self):
            MacroServer.startSocketListen(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.isConnected = False

        # 녹화 리스너
        self.setStyleSheet("background-color: #292929;")
        self.setWindowTitle("MacroServer")
        self.resize(1280, 840)

        # self.state_ = QLabel("상태")
        # self.state_.setAlignment(QtCore.Qt.AlignCenter)
        # self.state_.setFont(QFont('Arial', 10))
        # self.state_.setStyleSheet('QLabel { color : white;}')

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

        layout.addWidget(self.loading_label, 0, 2)
        # layout.addWidget(self.state_, 1, 2)
        layout.addWidget(self.state_msg, 2, 2)
        layout.addWidget(self.btn_conn, 3, 2)

        self.setLayout(layout)

        self.btn_conn.clicked.connect(self.btn_conn_Clicked)

    def btn_conn_Clicked(self):
        if self.btn_conn.text() == "Stop Connecting":
            #연결 중단하기
            self.stopLoadingAnimation(False)
        else:
            self.startLoadingAnimation()
            self.startListen()

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
                self.stopSocketListen()
                self.thread.quit()
                self.isConnected = False
            except:
                pass



    def startListen(self):
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = self.Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets

    def startSocketListen(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 소켓 레벨과 데이터 형태를 설정한다.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 서버는 복수 ip를 사용하는 pc의 경우는 ip를 지정하고 그렇지 않으면 None이 아닌 ''로 설정한다.
        # 포트는 pc내에서 비어있는 포트를 사용한다. cmd에서 netstat -an | find "LISTEN"으로 확인할 수 있다.
        self.server_socket.bind(('161.122.112.178', 9999))
        # server 설정이 완료되면 listen를 시작한다.
        self.server_socket.listen()
        try:
            print("연결 시도중..")
            # client로 접속이 발생하면 accept가 발생한다.
            # 그럼 client 소켓과 addr(주소)를 튜플로 받는다.
            self.client_socket, self.addr = self.server_socket.accept()
            # 쓰레드를 이용해서 client 접속 대기를 만들고 다시 accept로 넘어가서 다른 client를 대기한다.
            # asyncio.run(binder(client_socket, addr))
            self.th = threading.Thread(target=binder, args=(self.client_socket, self.addr))
            # th.daemon = True
            self.th.start()
        except:
            print("연결 오류..")


    def stopSocketListen(self):
        self.server_socket.close()
        self.client_socket.close()
        print("연결 종료")


def connectionCheck(cs):
    try:
        cs.send("some more data")
        return True
    except:
        return False

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
def binder(client_socket, addr):
    # 커넥션이 되면 접속 주소가 나온다.
    print('Connected by', addr)
    win.stopLoadingAnimation(True)
    client_socket.send('pong'.encode())

    while True:

        try:
            rdata = client_socket.recv(256)
            print("receive : ", rdata.decode('utf8'), '\n')

        except BlockingIOError as block_error:
            print("들어온 데이터가 없음")


        if is_socket_closed(client_socket):
            print("Client 응답 없음")
            win.stopLoadingAnimation(False)
            break
        else:
            pass # print("연결 정상")

        if win.isConnected is False:
            break

        time.sleep(2)

if __name__ == '__main__':
        app = QApplication(sys.argv)
        win = MacroServer()
        win.show()
        sys.exit(app.exec_())