import sys
import os
import winreg

class AutostartService:
    APP_NAME = "WarningAssistant"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def set_autostart(enable=True):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AutostartService.REG_PATH, 0, winreg.KEY_SET_VALUE)
            if enable:
                # Get path to the exe or python script
                if getattr(sys, 'frozen', False):
                    script_path = sys.executable
                else:
                    script_path = os.path.abspath(sys.argv[0])
                
                winreg.SetValueEx(key, AutostartService.APP_NAME, 0, winreg.REG_SZ, f'"{script_path}"')
            else:
                try:
                    winreg.DeleteValue(key, AutostartService.APP_NAME)
                except FileNotFoundError:
                    pass # Already gone
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error setting autostart: {e}")
            return False

    @staticmethod
    def is_autostart_enabled():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AutostartService.REG_PATH, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, AutostartService.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
