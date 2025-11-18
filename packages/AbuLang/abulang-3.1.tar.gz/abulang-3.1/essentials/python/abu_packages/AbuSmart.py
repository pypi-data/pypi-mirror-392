"""
AbuSmart - System utilities for AbuLang
Provides system operations like time, shutdown, webcam, etc.
"""

import os
import sys
import platform
import datetime
import subprocess
import webbrowser

class AbuSmart:
    """System utilities and smart operations"""
    
    @staticmethod
    def time():
        """Get current time as string"""
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def date():
        """Get current date as string"""
        return datetime.datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def datetime():
        """Get current date and time as string"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def timestamp():
        """Get current Unix timestamp"""
        return int(datetime.datetime.now().timestamp())
    
    @staticmethod
    def shutdown(minutes=0):
        """
        Shutdown computer after specified minutes
        
        Args:
            minutes: Minutes to wait before shutdown (0 = immediate)
        """
        seconds = minutes * 60
        system = platform.system()
        
        try:
            if system == "Windows":
                os.system(f"shutdown /s /t {seconds}")
                print(f"[AbuSmart] Shutdown scheduled in {minutes} minute(s)")
            elif system in ["Linux", "Darwin"]:  # Darwin = macOS
                os.system(f"sudo shutdown -h +{minutes}")
                print(f"[AbuSmart] Shutdown scheduled in {minutes} minute(s)")
            else:
                print(f"[AbuSmart Error] Shutdown not supported on {system}")
        except Exception as e:
            print(f"[AbuSmart Error] Could not schedule shutdown: {e}")
    
    @staticmethod
    def cancel_shutdown():
        """Cancel scheduled shutdown"""
        system = platform.system()
        
        try:
            if system == "Windows":
                os.system("shutdown /a")
                print("[AbuSmart] Shutdown cancelled")
            elif system in ["Linux", "Darwin"]:
                os.system("sudo shutdown -c")
                print("[AbuSmart] Shutdown cancelled")
        except Exception as e:
            print(f"[AbuSmart Error] Could not cancel shutdown: {e}")
    
    @staticmethod
    def restart(minutes=0):
        """
        Restart computer after specified minutes
        
        Args:
            minutes: Minutes to wait before restart (0 = immediate)
        """
        seconds = minutes * 60
        system = platform.system()
        
        try:
            if system == "Windows":
                os.system(f"shutdown /r /t {seconds}")
                print(f"[AbuSmart] Restart scheduled in {minutes} minute(s)")
            elif system in ["Linux", "Darwin"]:
                os.system(f"sudo shutdown -r +{minutes}")
                print(f"[AbuSmart] Restart scheduled in {minutes} minute(s)")
        except Exception as e:
            print(f"[AbuSmart Error] Could not schedule restart: {e}")
    
    @staticmethod
    def webcam():
        """Open webcam using default camera application"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Try to open Windows Camera app
                os.system("start microsoft.windows.camera:")
                print("[AbuSmart] Opening webcam...")
            elif system == "Darwin":  # macOS
                # Open Photo Booth or FaceTime
                os.system("open -a 'Photo Booth'")
                print("[AbuSmart] Opening webcam...")
            elif system == "Linux":
                # Try cheese or guvcview
                try:
                    subprocess.Popen(["cheese"])
                    print("[AbuSmart] Opening webcam...")
                except:
                    try:
                        subprocess.Popen(["guvcview"])
                        print("[AbuSmart] Opening webcam...")
                    except:
                        print("[AbuSmart Error] No webcam app found. Install 'cheese' or 'guvcview'")
        except Exception as e:
            print(f"[AbuSmart Error] Could not open webcam: {e}")
    
    @staticmethod
    def open_url(url):
        """Open URL in default browser"""
        try:
            webbrowser.open(url)
            print(f"[AbuSmart] Opening {url}")
        except Exception as e:
            print(f"[AbuSmart Error] Could not open URL: {e}")
    
    @staticmethod
    def system_info():
        """Get system information"""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version.split()[0]
        }
        
        for key, value in info.items():
            print(f"{key}: {value}")
        
        return info
    
    @staticmethod
    def battery():
        """Get battery status (requires psutil)"""
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                print(f"Battery: {battery.percent}%")
                print(f"Plugged in: {battery.power_plugged}")
                print(f"Time left: {battery.secsleft // 60} minutes")
                return {
                    "percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "time_left": battery.secsleft
                }
            else:
                print("[AbuSmart] No battery detected")
                return None
        except ImportError:
            print("[AbuSmart Error] Install 'psutil' for battery info: pip install psutil")
            return None
        except Exception as e:
            print(f"[AbuSmart Error] Could not get battery info: {e}")
            return None
    
    @staticmethod
    def volume(level=None):
        """
        Get or set system volume (0-100)
        
        Args:
            level: Volume level to set (None = just get current)
        """
        try:
            import psutil
            # This is platform-specific and complex
            # For now, just provide a message
            if level is not None:
                print(f"[AbuSmart] Volume control requires platform-specific implementation")
                print(f"[AbuSmart] Requested volume: {level}%")
            else:
                print("[AbuSmart] Volume query requires platform-specific implementation")
        except ImportError:
            print("[AbuSmart Error] Install 'psutil' for volume control: pip install psutil")
    
    @staticmethod
    def notify(title, message):
        """
        Show system notification
        
        Args:
            title: Notification title
            message: Notification message
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                # Use Windows toast notification
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=5)
                except ImportError:
                    print("[AbuSmart] Install 'win10toast' for notifications: pip install win10toast")
            elif system == "Darwin":  # macOS
                os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
            elif system == "Linux":
                os.system(f'notify-send "{title}" "{message}"')
        except Exception as e:
            print(f"[AbuSmart Error] Could not show notification: {e}")
    
    @staticmethod
    def clipboard_copy(text):
        """Copy text to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(text)
            print(f"[AbuSmart] Copied to clipboard: {text[:50]}...")
        except ImportError:
            print("[AbuSmart Error] Install 'pyperclip' for clipboard: pip install pyperclip")
        except Exception as e:
            print(f"[AbuSmart Error] Could not copy to clipboard: {e}")
    
    @staticmethod
    def clipboard_paste():
        """Get text from clipboard"""
        try:
            import pyperclip
            text = pyperclip.paste()
            print(f"[AbuSmart] Clipboard: {text[:50]}...")
            return text
        except ImportError:
            print("[AbuSmart Error] Install 'pyperclip' for clipboard: pip install pyperclip")
            return None
        except Exception as e:
            print(f"[AbuSmart Error] Could not paste from clipboard: {e}")
            return None


# Create singleton instance
smart = AbuSmart()
