import os
import subprocess
import sys
import shutil

def install_pyinstaller():
    print("Checking for PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller. Please install it manually.")
        sys.exit(1)

def build_exe():
    print("Building Claude Bridge Agent...")
    
    # Clean previous build
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        
    # PyInstaller command
    # --noconsole: Don't show terminal window (run in background)
    # --onefile: Bundle everything into one .exe
    # --name: Name of the output file
    # --add-data: Include assets if needed
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "ClaudeBridgeAgent",
        "--hidden-import", "PIL",
        "--hidden-import", "pyautogui",
        "--hidden-import", "pyperclip",
        "--hidden-import", "aiohttp",
        "local_agent.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\nSUCCESS! Build complete.")
        print(f"Executable is located at: {os.path.abspath('dist/ClaudeBridgeAgent.exe')}")
    except subprocess.CalledProcessError:
        print("Build failed.")

if __name__ == "__main__":
    install_pyinstaller()
    build_exe()
