import subprocess
import sys
import os
import shutil

def run_git_cmd(args):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def update_from_git():
    """
    Check for git updates and pull if available.
    Returns:
        bool: True if updated (restart required), False otherwise.
    """
    # 1. Check if git is available and we are in a repo
    if not shutil.which("git"):
        print("[Updater] Git not found. Skipping auto-update.")
        return False
        
    if not os.path.exists(".git"):
        # Not a git repo (maybe downloaded zip or pip install)
        return False

    print("[Updater] Checking for updates...")
    
    # 2. Fetch remote
    ok, _ = run_git_cmd(["remote", "update"])
    if not ok:
        print("[Updater] Failed to check for updates (network issue?).")
        return False

    # 3. Check status
    # 'git status -uno' usually tells 'Your branch is behind...'
    ok, status = run_git_cmd(["status", "-uno"])
    
    if "Your branch is behind" in status:
        print("[Updater] New version available! Downloading...")
        
        # 4. Pull
        ok, res = run_git_cmd(["pull"])
        if ok:
            print("[Updater] ✅ Update successful.")
            return True
        else:
            print(f"[Updater] ❌ Update failed: {res}")
            return False
            
    elif "Your branch is up to date" in status:
        print("[Updater] Already up to date.")
        return False
    else:
        # Diverged or clean or something else
        # print(f"[Updater] Status: {status}") # Debug
        return False

def restart_process():
    """Restart the current python process."""
    print("[Updater] 🔄 Restarting application...")
    # Give time for I/O flush
    try:
        # Re-execute the current script with same arguments
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"[Updater] Error restarting: {e}")
        print("Please restart manually.")
        sys.exit(0)
