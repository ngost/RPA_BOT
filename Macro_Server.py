import time
import asyncio
import keyboard
import PyQt5
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QByteArray, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QLayout, QBoxLayout, \
    QGridLayout, QLabel, QProgressBar, QLineEdit, QSizePolicy
from PyQt5 import QtCore
import sys
import threading, socket
import logging
import pyautogui as pat
import pyperclip
import numpy as np

logger = logging.getLogger(__name__)

class GlobalHotkeyManager(QObject):
    StopSignal = pyqtSignal()
    
    def start(self):
        keyboard.add_hotkey('ctrl+f1', self.StopSignal.emit)

class CommandSet:
    def __init__(self):
        # 명령어 입력 부분 (계산기 sample
        self._list = list()

        self._list.insert(0, Command("move", [83, 343]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [123, 491]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("pause"))

class Command:
    def __init__(self, command_type="m", command_data=["0,0"]):
        # m : mouse command, h : keyboard commnad, k : keyboard typing, lc : click
        self._type = command_type
        self._data = command_data

    def work(self):
        if self._type == "move":
            _pos = np.array([self._data[0], self._data[1]])
            print("- mouse input -")
            print(_pos)
            pat.moveTo(_pos[0], _pos[1])
            return False
        elif self._type == "lc":
            pat.leftClick()
            return False
        elif self._type == "k":
            pyperclip.copy(self._data[0])
            pat.hotkey("ctrl", "v")
            return False
        elif self._type == "h":
            if len(self._data) == 1:
                pat.hotkey(self._data[0])
            if len(self._data) == 2:
                pat.hotkey(self._data[0], self._data[1])
            if len(self._data) == 3:
                pat.hotkey(self._data[0], self._data[1], self._data[2])
            return False
        elif self._type == "pause":
            return True
        elif self._type == "reset":
            commands = CommandSet()



class MacroServer(QWidget):
    commands = CommandSet()
    activated_socket = None
    acc_time = 0
    isTimerRunning = False

    class Worker(QObject):
        finished = pyqtSignal()

        def run(self):
            MacroServer.startSocketListen(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.isConnected = False
        
        self.acc_time = 0
        self.routine_time = 30 # default time 30 seconds
        self.delay_time = 0

        # 녹화 리스너
        self.setStyleSheet("background-color: #292929;")
        self.setWindowTitle("MacroServer")
        self.resize(640, 320)

        # self.state_ = QLabel("상태")
        # self.state_.setAlignment(QtCore.Qt.AlignCenter)
        # self.state_.setFont(QFont('Arial', 10))
        # self.state_.setStyleSheet('QLabel { color : white;}')

        self.state_msg = QLabel("연결 안됨")
        self.state_msg.setFont(QFont('Arial', 10))
        self.state_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.state_msg.setStyleSheet('QLabel { color : white;}')

        self.time_interval_text = QLineEdit("30")
        self.time_interval_text.setStyleSheet('QLineEdit { color : white;}')
        self.time_interval_text.setAlignment(QtCore.Qt.AlignCenter)
        #label
        self.loading_label = QLabel(alignment = QtCore.Qt.AlignCenter)

        self.loading_label.setGeometry(QtCore.QRect(50, 50, 50, 50))
        self.loading_label.setMinimumSize(QtCore.QSize(50, 50))
        self.loading_label.setMaximumSize(QtCore.QSize(150, 150))

        self.timer_label = QLabel("0")
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStyleSheet('QLabel { color : white;}')

        # Loading the GIF
        self.movie = QMovie("loading4.gif", QByteArray(), self)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.loading_label.setMovie(self.movie)
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_conn = QPushButton("Try Connect")
        self.btn_conn.resize(300,300)
        self.btn_conn.setIcon(QIcon('try_conn_btn.png'))
        self.btn_conn.setStyleSheet('QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#FF9800; color: white;}')

        self.btn_startMacro = QPushButton("Start Macro")
        self.btn_startMacro.setStyleSheet('QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#FF9800; color: white;}')

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timer_update)

        layout = QGridLayout()
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 1)
        layout.setRowStretch(6, 1)
        layout.setRowStretch(7, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)
        

        layout.addWidget(self.loading_label, 0, 2)
        # layout.addWidget(self.state_, 1, 2)
        layout.addWidget(self.state_msg, 2, 2)
        layout.addWidget(self.btn_conn, 3, 2)
        layout.addWidget(self.btn_startMacro, 4, 2)
        layout.addWidget(self.timer_label, 5, 2)
        layout.addWidget(self.time_interval_text,6,2)

        self.setLayout(layout)

        self.btn_conn.clicked.connect(self.btn_conn_Clicked)
        self.btn_startMacro.clicked.connect(self.btn_Macro_On_Off_Clicked)
        
        hotkeyManager = GlobalHotkeyManager(self)
        hotkeyManager.StopSignal.connect(self.btn_Macro_On_Off_Clicked)
        hotkeyManager.start()

    def timer_update(self):
        self.acc_time += 1
        self.timer_label.setText(str(self.routine_time - self.acc_time))
        if self.routine_time <= self.acc_time:
            #일할 시간이다 Client야.
            send_to_client_execute_command()
            self.acc_time = 0

        # Server - Client Binding 연결.. (hand shaking)
    def btn_conn_Clicked(self):
        self.routine_time = int(self.time_interval_text.text())
        if self.btn_conn.text() == "Stop Connecting":
            #연결 중단하기
            self.stopLoadingAnimation(False)
        else:
            self.startLoadingAnimation()
            self.startListen()

    def btn_Macro_On_Off_Clicked(self):
        if self.isTimerRunning == False:
            # 매크로 실행
            self.isTimerRunning = True
            self.timer.start()
            send_to_client_execute_command()
            self.btn_startMacro.setText("Stop Macro")
            self.btn_startMacro.setStyleSheet('QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#64b5f6; color: white;}')            
            self.showMinimized()
        else:
            # 매크로 중지
            self.isTimerRunning = False
            self.timer.stop()
            self.btn_startMacro.setText("Start Macro")
            self.time_interval_text.setText("0")
            self.btn_startMacro.setStyleSheet('QPushButton::hover' '{' 'background-color : #64b5f6' '}' 'QPushButton {background-color:#FF9800; color: white;}')
            self.showNormal()

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
        self.server_socket.bind(('127.0.0.1', 9999))
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



def send_to_client_execute_command():
    MacroServer.activated_socket.send('client on'.encode())

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
    is_client_running = False
    # 커넥션이 되면 접속 주소가 나온다.

    print('Connected by', addr)
    win.stopLoadingAnimation(True)


    client_socket.settimeout(None)
    MacroServer.activated_socket = client_socket


    #client_socket.send('pong'.encode())

    #client에게 명령 하면서 시작
#    client_socket.send('client on'.encode())

    while True:
        try:
            # receive 시작
            rdata = client_socket.recv(256)
            #print("receive : ", rdata.decode('utf8'), '\n')

            if rdata.decode('utf8') == "server on":
                print("server 시작")
                while True:
                    time.sleep(1)
                    
                    if win.isTimerRunning == False :
                        print("매크로 작업 스탑! ( S )")
                        MacroServer.commands = CommandSet()
                        win.showNormal()
                        client_socket.send('client off'.encode())
                        is_client_running = False
                        break
                    
                    if len(MacroServer.commands._list) <= 0:
                        print("Server 루틴 종료")
                        MacroServer.commands = CommandSet()
                        break
                    c = MacroServer.commands._list.pop()

                    # Command Set에 따라 일하기
                    isBreak = c.work()

                    # command set에 pause 명령어 들어온 경우
                    if isBreak:
                        print("명령 권한 변경 Server -> client")
                        client_socket.send('client on'.encode())
                        is_client_running = True
                        if len(MacroServer.commands._list) <= 0:
                            MacroServer.commands = CommandSet()
                        break

            if rdata.decode('utf8') == "server off":
                MacroServer.commands = CommandSet()

            if is_socket_closed(client_socket):
                print("Client 응답 없음")
                win.stopLoadingAnimation(False)
                break
            else:
                pass  # print("연결 정상")

            if win.isConnected is False:
                break

        except BlockingIOError as block_error:
            pass
        except OSError as os_error:
            win.stopLoadingAnimation(False)
            break
        
        if win.isTimerRunning == False and is_client_running == True:
            print("매크로 작업 스탑! ( S )")
            MacroServer.commands = CommandSet()
            win.showNormal()
            client_socket.send('client off'.encode())
            is_client_running = False
            
                    
        time.sleep(2)
        

if __name__ == '__main__':
#    commands = CommandSet()
    app = QApplication(sys.argv)
    win = MacroServer()
    win.show()
    sys.exit(app.exec_())