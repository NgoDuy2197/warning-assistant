import sys
import os
import subprocess

class AutostartService:
    APP_NAME = "Assistant"

    @staticmethod
    def set_autostart(enable=True):
        """Set autostart for the application based on OS"""
        if sys.platform == "win32":
            return AutostartService._set_autostart_windows(enable)
        elif sys.platform == "darwin":
            return AutostartService._set_autostart_macos(enable)
        else:
            # Linux support can be added here if needed
            print("Autostart not supported on this platform")
            return False

    @staticmethod
    def _set_autostart_windows(enable=True):
        """Set autostart on Windows using Registry"""
        try:
            import winreg
            REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
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
                    pass  # Already gone
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error setting autostart on Windows: {e}")
            return False

    @staticmethod
    def _set_autostart_macos(enable=True):
        """Set autostart on macOS using LaunchAgents"""
        try:
            # Get path to LaunchAgents directory
            launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
            os.makedirs(launch_agents_dir, exist_ok=True)
            
            plist_filename = f"com.assistant.{AutostartService.APP_NAME}.plist"
            plist_path = os.path.join(launch_agents_dir, plist_filename)
            
            if enable:
                # Get path to the executable
                if getattr(sys, 'frozen', False):
                    # Running as compiled app
                    script_path = sys.executable
                else:
                    # Running as Python script
                    script_path = os.path.abspath(sys.argv[0])
                    python_path = sys.executable
                
                # Create plist content
                if getattr(sys, 'frozen', False):
                    # For compiled app
                    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.assistant.{AutostartService.APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
                else:
                    # For Python script
                    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.assistant.{AutostartService.APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
                
                # Write plist file
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                
                # Load the launch agent
                subprocess.run(['launchctl', 'load', plist_path], check=False)
            else:
                # Disable autostart
                if os.path.exists(plist_path):
                    # Unload the launch agent
                    subprocess.run(['launchctl', 'unload', plist_path], check=False)
                    # Remove the plist file
                    os.remove(plist_path)
            
            return True
        except Exception as e:
            print(f"Error setting autostart on macOS: {e}")
            return False

    @staticmethod
    def is_autostart_enabled():
        """Check if autostart is enabled based on OS"""
        if sys.platform == "win32":
            return AutostartService._is_autostart_enabled_windows()
        elif sys.platform == "darwin":
            return AutostartService._is_autostart_enabled_macos()
        else:
            return False

    @staticmethod
    def _is_autostart_enabled_windows():
        """Check if autostart is enabled on Windows"""
        try:
            import winreg
            REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, AutostartService.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    @staticmethod
    def _is_autostart_enabled_macos():
        """Check if autostart is enabled on macOS"""
        try:
            launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
            plist_filename = f"com.assistant.{AutostartService.APP_NAME}.plist"
            plist_path = os.path.join(launch_agents_dir, plist_filename)
            return os.path.exists(plist_path)
        except Exception:
            return False
