from flask import Flask, abort, redirect, url_for, jsonify, request
from git import Repo, Git
import subprocess
import platform
import psutil
import time
import sys
import os

app = Flask(__name__)

#Для теста http://localhost:5000/api/download?q=https://github.com/NinFernto/MicroGitPyDocker.git
#http://localhost:5000/api/download?q=https://github.com/Flowseal/zapret-discord-youtube.git
@app.route("/api/download")
def test():
    url = request.args.get('q')
    if url != None:       
        namefolder = url.split('/')[4].split('.git')[0]
        namefolder = 'projects/' + namefolder
        os.makedirs(namefolder, exist_ok=True)
        Repo.clone_from(url, namefolder)
    return redirect('/')

@app.route("/api/hello")
def hello():
    name = request.args.get("name", "мир")
    return jsonify(message=f"Привет, {name}!")

def run_detached(script):
    os.makedirs('logs', exist_ok=True)
    name_script = "logs/" + script.split('.')[0]
    system = platform.system()
    log_file = open(f"{name_script}.log", "a", encoding="utf-8")
    err_file = open(f"{name_script}_err.log", "a", encoding="utf-8")
    subprocess.Popen(
        [sys.executable, script],
        creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0,
        stdout=log_file,
        stderr=err_file,
        bufsize=1,
        text=True   
    )

def kill_process_by_name(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = proc.info['cmdline']
            if cmd and script_name in cmd:
                print(f"Убиваем {script_name}, PID={proc.pid}")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == "__main__":
    app.run(debug=True)
