import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import win32gui, win32con, win32process, win32api

class WindowMgr(QObject):
    show_sig = pyqtSignal()
    
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.show_sig.connect(self.show_it)
        
    def show_it(self):
        self.win.showFullScreen()
        hwnd = win32gui.FindWindow(None, "TestPopup")
        if hwnd:
            try:
                fg_hwnd = win32gui.GetForegroundWindow()
                if fg_hwnd and hwnd != fg_hwnd:
                    current_thread_id = win32api.GetCurrentThreadId()
                    fg_thread_id = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
                    win32process.AttachThreadInput(current_thread_id, fg_thread_id, True)
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    win32gui.SetForegroundWindow(hwnd)
                    win32process.AttachThreadInput(current_thread_id, fg_thread_id, False)
                    print("Focus violently stolen on Windows.")
            except Exception as e:
                print(f"Failed to force foreground: {e}")
            
def background(mgr):
    time.sleep(3)
    print("Triggering popup NOW!")
    mgr.show_sig.emit()

from PyQt5.QtCore import QCoreApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
app = QApplication(sys.argv)
win = QMainWindow()
win.setWindowTitle("TestPopup")
win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
lbl = QLabel("<h1 style='color:red;text-align:center;'>TESTING FULLSCREEN POPUP FOCUS STEAL!</h1>")
win.setCentralWidget(lbl)

mgr = WindowMgr(win)
threading.Thread(target=background, args=(mgr,), daemon=True).start()
print("Please open and focus a completely different application (like an IDE or browser) within the next 3 seconds...")
sys.exit(app.exec_())
