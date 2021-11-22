import time

import pyautogui as pat
import pyperclip
import numpy as np

class Command:
    def __init__(self, command_type = "m", command_data = ["0,0"]):
        #m : mouse command, h : keyboard commnad, k : keyboard typing, lc : click
        self._type = command_type
        self._data = command_data

    def work(self):
        if self._type == "move":
            _pos = np.array([self._data[0],self._data[1]])
            print("- mouse input -")
            print(_pos)
            pat.moveTo(_pos[0],_pos[1])
            return True
        elif self._type == "lc":
            pat.leftClick()
            return True
        elif self._type == "k":
            pyperclip.copy(self._data[0])
            pat.hotkey("ctrl", "v")
            return True
        elif self._type == "h":
            if len(self._data) == 1:
                pat.hotkey(self._data[0])
            if len(self._data) == 2:
                pat.hotkey(self._data[0],self._data[1])
            if len(self._data) == 3:
                pat.hotkey(self._data[0],self._data[1],self._data[2])
            return True
        elif self._type == "turn":
            return False




class CommandSet:
    def __init__(self):
        # 명령어 입력 부분 (계산기 sample
        self._list = list()
        self._list.insert(0,Command("move",[30,2140]))
        self._list.insert(0,Command("lc"))
        self._list.insert(0,Command("k",["계산기"]))
        self._list.insert(0,Command("h",["enter"]))
        self._list.insert(0,Command("h",["win","up"]))
        self._list.insert(0, Command("move", [1976, 1753]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [396, 1244]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [408, 1526]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [2779, 1264]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [618, 1749]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [1181, 1735]))
        self._list.insert(0, Command("lc"))
        self._list.insert(0, Command("move", [2816, 1984]))
        self._list.insert(0, Command("lc"))
#        self._list.insert(0,Command("k","win"))

if __name__ == '__main__':
    commands = CommandSet()

    while True:
        time.sleep(1)
        if len(commands._list) <= 0:
            break

        c = commands._list.pop()
        isContinue = c.work()


#1. connection
