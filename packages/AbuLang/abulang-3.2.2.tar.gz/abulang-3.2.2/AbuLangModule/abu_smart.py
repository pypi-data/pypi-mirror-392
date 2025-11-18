"""
AbuSmart - System Utilities Package
"""

import datetime
import webbrowser
import os
import platform

def time():
    """Get current time"""
    return datetime.datetime.now().strftime("%H:%M:%S")

def date():
    """Get current date"""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def datetime_now():
    """Get current datetime"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def timestamp():
    """Get Unix timestamp"""
    return int(datetime.datetime.now().timestamp())

def system_info():
    """Display system information"""
    print("=== System Information ===")
    print(f"OS: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {platform.python_version()}")

def open_url(url):
    """Open URL in browser"""
    webbrowser.open(url)

def shutdown(minutes=0):
    """Shutdown system (Windows)"""
    if platform.system() == "Windows":
        os.system(f"shutdown /s /t {minutes*60}")
    else:
        print("Shutdown only supported on Windows")

def cancel_shutdown():
    """Cancel shutdown (Windows)"""
    if platform.system() == "Windows":
        os.system("shutdown /a")
    else:
        print("Cancel shutdown only supported on Windows")

def restart(minutes=0):
    """Restart system (Windows)"""
    if platform.system() == "Windows":
        os.system(f"shutdown /r /t {minutes*60}")
    else:
        print("Restart only supported on Windows")

def battery():
    """Get battery status (requires psutil)"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            return battery.percent
        return None
    except ImportError:
        print("Install psutil: pip install psutil")
        return None

def clipboard_copy(text):
    """Copy to clipboard (requires pyperclip)"""
    try:
        import pyperclip
        pyperclip.copy(text)
    except ImportError:
        print("Install pyperclip: pip install pyperclip")

def clipboard_paste():
    """Paste from clipboard (requires pyperclip)"""
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        print("Install pyperclip: pip install pyperclip")
        return ""

def notify(title, message):
    """Show system notification"""
    try:
        if platform.system() == "Windows":
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
        else:
            print(f"[{title}] {message}")
    except ImportError:
        print(f"[{title}] {message}")

def webcam():
    """Open webcam (requires opencv)"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    except ImportError:
        print("Install opencv: pip install opencv-python")
