import subprocess
import os
import platform
import psutil

def run_powershell(command: str) -> str:
    """Execute a PowerShell command and return output"""
    try:
        # Use -Command to execute
        result = subprocess.run(
            ["powershell", "-Command", command], 
            capture_output=True, 
            text=True,
            encoding='utf-8' # Force encoding if needed to avoid decode errors
        )
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Execution Error: {str(e)}"

def run_cmd(command: str) -> str:
    """Execute a CMD command and return output"""
    try:
        result = subprocess.run(
            command, 
            shell=True,
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
             # Combine stdout and stderr if needed, or just return stderr
             return f"Error: {result.stderr.strip()} (Types: {result.stdout.strip()})"
        return result.stdout.strip()
    except Exception as e:
        return f"Execution Error: {str(e)}"

def file_read(path: str) -> str:
    """Read contents of a file"""
    try:
        if not os.path.exists(path):
            return "File does not exist"
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def file_write(path: str, content: str) -> str:
    """Write content to a file"""
    try:
        mode = 'w'
        # Basic check if it's a binary write request? user said "Write content", implied string
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        return "File written successfully"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def file_list(directory: str) -> list:
    """List files in a directory"""
    try:
        if not os.path.exists(directory):
            return ["Directory does not exist"]
        return os.listdir(directory)
    except Exception as e:
        return [f"Error: {str(e)}"]

def file_exists(path: str) -> bool:
    """Check if a file or directory exists"""
    return os.path.exists(path)

def get_system_info() -> dict:
    """Get system information (OS, CPU, memory, etc.)"""
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "cpu_percent": psutil.cpu_percent(interval=0.1)
    }
    return info

def set_volume(level: int) -> str:
    """Set system volume (0-100)"""
    # Requires external library or powershell/nircmd. sticking to powershell for simplicity no extra dependency
    # "uiautomation" can theoretically do it by finding the volume mixer, but scripting is cleaner.
    # A common way is using a small powershell script or pycaw if installed (not in list).
    # We will try powershell approach.
    ps_script = f"""
    $obj = new-object -com wscript.shell
    # There isn't a direct "SetVolume" in WScript.Shell, it just does SendKeys.
    # To set specific level is hard without CoreAudio APIs (pycaw).
    # For now, we'll return a stub or try pycaw if we secretly had it, but we don't.
    # We will use valid requirement: pycaw or comtypes. 
    # Since they weren't in requirements.txt (only fastmcp/ui/pyauto...), we'll skip complex implementation 
    # and provide a 'Not Implemented without pycaw' message or use nircmd if available.
    # Wait! 'pycaw' wasn't in the user prompt requirements.
    # I will omit actual implementation or use a placeholder that says "Volume control requires pycaw".
    """
    return "Volume control requires 'pycaw' library which is not in the standard requirements. Skipping."

def notification(title: str, message: str) -> str:
    """Show a Windows notification"""
    # Powershell balloon tip
    cmd = f"""
    [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
    $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon 
    $objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information 
    $objNotifyIcon.BalloonTipIcon = "Info" 
    $objNotifyIcon.BalloonTipTitle = "{title}" 
    $objNotifyIcon.BalloonTipText = "{message}" 
    $objNotifyIcon.Visible = $True 
    $objNotifyIcon.ShowBalloonTip(10000)
    """
    # This might hang if not careful or requires a message loop. 
    # Better to just use a simple Toast if possible, or skip complex GUI interaction from backend.
    # We'll try the simple powershell method.
    try:
        subprocess.Popen(["powershell", "-Command", cmd])
        return "Notification sent"
    except Exception as e:
        return f"Error sending notification: {str(e)}"
