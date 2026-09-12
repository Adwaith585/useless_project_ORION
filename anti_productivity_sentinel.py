import sys
import os
import time
import json
import threading
import copy
import cv2
import mss
import numpy as np
import pygetwindow as gw
import keyboard
import win32gui
import win32con
import win32api
import win32process
import ollama
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QUrl, QTimer

WORK_TITLES = ['vscode', 'visual studio code', 'pycharm', 'terminal', 'cmd', 'powershell', 'jupyter', 'vim', 'kali']

OLLAMA_PROMPT = """Look at the provided webcam image and screen image. 
Is the person physically studying, reading a textbook, writing with a pen on paper, holding a pen, OR looking at an IDE/code editor/coding terminal on the screen? 
If yes, you must reply with exactly one word: TRIGGER 

Otherwise, if they are just lounging or doing nothing, reply with: IDLE"""

class SentinelThread(QThread):
    trigger_signal = pyqtSignal()
    hide_signal = pyqtSignal()

    def __init__(self, window_ref=None):
        super().__init__()
        self.window_ref = window_ref
        self.running = True
        self.model_name = "llava"
        
        self.request_lock = threading.Lock()
        
    def diff_frames(self, diff_name, f1, f2, threshold=1000):
        if f1 is None or f2 is None: return True
        f1_gray = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
        f2_gray = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(f1_gray, f2_gray)
        non_zero = np.count_nonzero(diff > 30)
        print(f"Diff [{diff_name}]: {non_zero}")
        return non_zero > threshold

    def get_resized_frame(self, frame, width=640):
        if frame is None: return None
        h, w = frame.shape[:2]
        r = width / float(w)
        dim = (width, int(h * r))
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    def is_work_window_active(self):
        win = gw.getActiveWindow()
        if win and win.title:
            title = win.title.lower()
            return any(w in title for w in WORK_TITLES)
        return False

    def run(self):
        sct = mss.MSS()
        # CAP_DSHOW on Windows often enables webcam significantly faster
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        prev_screen = None
        prev_webcam = None
        
        while self.running:
            time.sleep(5)
            # Try to grab the lock without blocking. If we can't, it means a request is still in flight.
            if not self.request_lock.acquire(blocking=False):
                print("Skipping cycle; previous request still in flight.")
                continue
                
            if self.window_ref and self.window_ref.is_showing:
                print("Annoyance window active; holding, skipping detection cycle.")
                self.request_lock.release()
                continue
                
            try:
                # Capture screen
                monitor = sct.monitors[1] # primary monitor
                screen_img_raw = np.array(sct.grab(monitor))
                screen_frame = cv2.cvtColor(screen_img_raw, cv2.COLOR_BGRA2BGR)
                screen_small = self.get_resized_frame(screen_frame)
                
                # Capture webcam
                ret, webcam_frame = cap.read()
                webcam_small = self.get_resized_frame(webcam_frame) if ret else None
                
                work_title = self.is_work_window_active()
                s_changed = self.diff_frames("screen", prev_screen, screen_small, 5000)
                w_changed = self.diff_frames("webcam", prev_webcam, webcam_small, 3000)
                
                # Save the debug feed locally so we can view what the Sentinel sees safely
                debug_view = np.vstack((screen_small, webcam_small)) if webcam_small is not None else screen_small
                cv2.imwrite("debug_feed.png", debug_view)
                
                # 1. Local pre-filter check
                if work_title:
                    print("HARD TRIGGER: Work application is actively focused! Bypassing local model...")
                    self.trigger_signal.emit()
                    self.request_lock.release()
                    continue

                if not s_changed and not w_changed:
                    print("Pre-filter block: No visual changes. Skipping Ollama trigger.")
                    self.request_lock.release()
                    continue
                    
                prev_screen = screen_small
                prev_webcam = webcam_small
                
                print("Motion verified. Sending payload to Ollama for study detection...")
                
                # Sending both the screen AND webcam back into the payload, as Llava handles multi-image context brilliantly natively.
                _, screen_buf = cv2.imencode('.png', screen_small)
                images = [screen_buf.tobytes()]
                if webcam_small is not None:
                    _, webcam_buf = cv2.imencode('.png', webcam_small)
                    images.append(webcam_buf.tobytes())
                    

                    
                # 2. Call Ollama
                try:
                    res = ollama.chat(
                        model=self.model_name,
                        messages=[{
                            'role': 'user',
                            'content': OLLAMA_PROMPT,
                            'images': images
                        }]
                    )
                    raw_text = res['message']['content'].strip('` \n')
                    text_lower = raw_text.lower()
                    
                    if 'trigger' in text_lower:
                        print(f"TRIGGERED (fuzzy match): {raw_text}")
                        self.trigger_signal.emit()
                    elif 'idle' in text_lower:
                        print(f"IDLE (fuzzy match): {raw_text}")
                        self.hide_signal.emit()
                    else:
                        print(f"AMBIGUOUS output: {raw_text}")
                        
                except Exception as e:
                    print(f"Ollama output parsing/API error: {e}")
                    if 'res' in locals():
                        print(f"Raw response was: {res}")
                    # Do not emit hide_signal here so annoyance window stays up on failure
                    
            except Exception as e:
                print(f"Loop Capture error: {e}")
                # Do not emit hide_signal here for robustness
            finally:
                if self.request_lock.locked():
                    self.request_lock.release()

class AnnoyanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEnginePage
        import os

        profile_path = os.path.join(os.path.expanduser("~"), ".sentinel_browser_profile")
        self.profile = QWebEngineProfile("SentinelProfile", self)
        self.profile.setPersistentStoragePath(profile_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = QWebEnginePage(self.profile, self)
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.setCentralWidget(self.browser)
        self.setWindowTitle("Brain Rot")
        # Ensure it acts as a focused foreground window with full interaction capabilities
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window)
        
        self.url_toggle = True
        self.is_showing = False
    
    def steal_focus(self):
        hwnd = win32gui.FindWindow(None, "Brain Rot")
        if hwnd:
            try:
                fg_hwnd = win32gui.GetForegroundWindow()
                if fg_hwnd and hwnd != fg_hwnd:
                    # Windows restricts who can steal focus. The workaround is attaching thread inputs.
                    current_thread_id = win32api.GetCurrentThreadId()
                    fg_thread_id = win32process.GetWindowThreadProcessId(fg_hwnd)[0]
                    
                    win32process.AttachThreadInput(current_thread_id, fg_thread_id, True)
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    win32gui.SetForegroundWindow(hwnd)
                    win32process.AttachThreadInput(current_thread_id, fg_thread_id, False)
            except Exception as e:
                print(f"Focus steal partial fallback: {e}")

    def show_annoyance(self):
        # Trigger action
        if not self.is_showing:
            import random
            # Bypassing regional blocks and utilizing cache-busting parameters so the Shorts algorithm doesn't re-serve the same starting video.
            rand_bust = random.randint(1000, 99999)
            url = f"https://www.youtube.com/shorts?t={rand_bust}" if self.url_toggle else f"https://www.youtube.com/feed/trending?t={rand_bust}"
            self.url_toggle = not self.url_toggle
            self.browser.setUrl(QUrl(url))
            self.showFullScreen()
            self.is_showing = True
        
        # Always aggressively attempt to yank focus back if work persists
        self.steal_focus()

    def hide_annoyance(self):
        if self.is_showing:
            self.hide()
            self.browser.setUrl(QUrl("about:blank")) # stop playing audio!
            self.is_showing = False

def main():
    from PyQt5.QtCore import QCoreApplication
    print(f"Anti-Productivity Sentinel initialized. PID: {os.getpid()}")
    print("-> Press Ctrl+Alt+Shift+Q at any time to execute the Kill Switch.")
    print("-> NOTE: For the hotkey to work reliably against elevated windows, run this terminal as Administrator!")
    print(f"-> Backup kill command: taskkill /PID {os.getpid()} /F")
    # 4. Global Kill switch (Operator hatch)
    keyboard.add_hotkey('ctrl+alt+shift+q', lambda: os._exit(0))
    
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    
    window = AnnoyanceWindow()
    # Don't show initially unless triggered
    
    thread = SentinelThread(window)
    thread.trigger_signal.connect(window.show_annoyance)
    thread.hide_signal.connect(window.hide_annoyance)
    # Give the thread a slight delay to allow GUI to set up
    QTimer.singleShot(1000, thread.start)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
