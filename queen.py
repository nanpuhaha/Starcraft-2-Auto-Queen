import win32com.client
import win32api
import win32con
import time
import win32ui
from ctypes import *
import pythoncom, pyHook
from threading import Thread

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def boxSelect(x1,y1,x2,y2):
    win32api.SetCursorPos((x1,y1))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x1,y1,0,0)
    time.sleep(0.01)
    win32api.SetCursorPos((x2,y2))
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x2,y2,0,0)

def tap(char, count):
    for i in range(count):
        shell.SendKeys(char)
        time.sleep(0.01)

def beepWait(count):
    for i in range(count):
        print "\a"
    time.sleep(1)

def queen(pos):
    #Change 'v' to 'x' if you don't use grid layout
    tap('v', 1)
    click(pos[0], pos[1])
    time.sleep(0.01)

def allQueen(hatchPositions):
    beepWait(1)
    tap("^9", 1)
    tap(6, 1)
    for i in range(len(hatchPositions)):
        queen(hatchPositions[i])
    tap(9, 1)
    win32api.SetCursorPos((820,260))

class Admin(Thread):
    commandFlag = False
    queenFlag = False
    queenTime = 0
    cancelFlag = False
    hatchClick = False
    hatchPositions = []

    def handleKeyPressEvent(self, event):
        if (not self.commandFlag):
            if (event.Ascii == 92):
                self.commandFlag = True
        else:
            self.commandFlag = False
            #'q', start/stop queening
            if (event.Ascii == 113):
                self.queenFlag = not self.queenFlag
                self.queenTime = 0
            #'p', quit
            elif (event.Ascii == 112):
                self.cancelFlag = True
                self.hooker.join
            #'r', reset
            elif (event.Ascii == 114):
                self.reset()
            #'o', locate hatchery
            elif (event.Ascii == 111):
                self.hatchClick = True
                self.hooker.catchMouse(True)
        return True

    def handleMouseDownEvent(self, event):
        if (self.hatchClick):
            self.hatchClick = False
            self.hooker.catchMouse(False)
            self.hatchPositions.extend([0])
            self.hatchPositions[-1] = event.Position

    def reset(self):
        self.commandFlag = False
        self.queenFlag = False
        self.cancelFlag = False
        self.queenTime = 0
        self.hatchClick = False
        self.hatchPositions = []

    def run(self):
        while(not self.cancelFlag):
            time.sleep(0.5)
            #print self.stepTimer - time.clock()
            if (self.queenFlag and self.queenTime < time.clock()):
                allQueen(self.hatchPositions)
                self.queenTime = time.clock() + 30

    def registerHooker(self, hooker):
        self.hooker = hooker

class Hooker(Thread): 
    hm = pyHook.HookManager()
    def __init__ (self, admin):
        Thread.__init__(self)
        self.admin = admin

    def catchMouse(self, on):
        if (on):
            self.hm.MouseLeftDown = self.admin.handleMouseDownEvent
            self.hm.HookMouse()
        else:
            self.hm.UnhookMouse()

    def run(self):
        # watch for all keyboard events
        self.hm.KeyUp = self.admin.handleKeyPressEvent
        # set the hook
        self.hm.HookKeyboard()
        pythoncom.PumpMessages()


shell = win32com.client.Dispatch("WScript.Shell")
y = Admin()
x = Hooker(y)
y.registerHooker(x)
x.start()
y.start()
