import os
import sys
import threading
import requests
import subprocess
from tkinter import messagebox

# Software Version & GitHub Repository
CURRENT_VERSION = "v1.0.0"
GITHUB_REPO = "hex3132/invoice-managment"

class AutoUpdater:
    """Safely checks GitHub Releases in a non-blocking background thread."""
    def __init__(self, current_version=CURRENT_VERSION, repo=GITHUB_REPO):
        self.current_version = current_version
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{self.repo}/releases/latest"

    def check_for_updates(self, silent=True):
        """Spawns a daemon thread to check updates without freezing Tkinter UI."""
        thread = threading.Thread(target=self._check_logic, args=(silent,), daemon=True)
        thread.start()

    def _check_logic(self, silent):
        try:
            res = requests.get(self.api_url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                latest = data.get("tag_name", "")
                if latest and latest != self.current_version:
                    ans = messagebox.askyesno(
                        "Update Available!",
                        f"New version ({latest}) available!\nCurrent: {self.current_version}.\n\nDownload and install now?"
                    )
                    if ans:
                        self._download_and_install(data)
                elif not silent:
                    messagebox.showinfo("Up to Date", "You are using the latest version.")
            elif not silent:
                messagebox.showwarning("Update Error", f"Server status: {res.status_code}")
        except Exception:
            if not silent:
                messagebox.showerror("Update Error", "Unable to connect to GitHub.")

    def _download_and_install(self, release_data):
        assets = release_data.get("assets", [])
        exe_asset = next((a for a in assets if a.get("name", "").endswith(".exe")), None)
        if not exe_asset:
            messagebox.showerror("Error", "No installer (.exe) asset found in the latest release.")
            return

        try:
            messagebox.showinfo("Downloading", "Downloading update in background... Please wait.")
            r = requests.get(exe_asset["browser_download_url"], stream=True)
            path = os.path.join(os.getcwd(), exe_asset["name"])
            
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Execute Inno Setup installer in silent mode and exit app
            subprocess.Popen([path, "/SILENT"])
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Download Error", str(e))