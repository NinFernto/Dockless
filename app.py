from flask import Flask, flash, redirect, request, render_template
from git import Repo
import subprocess
import platform
import psutil
import json
import sys
import os

app = Flask(__name__)
app.secret_key = "dockless-secret-key"

os.makedirs('config', exist_ok=True)

@app.route("/")
def index():
    check_status_all_running()
    projects = getallprojects()
    return render_template('index.html', projects=projects)

@app.route("/api/download")
def download():
    try:
        url = request.args.get('q')
        if not url:
            flash("URL не указан", "warning")
            return redirect("/")
        namefile = url.split('/')[4].split('.git')[0]
        namefolder = 'projects/' + namefile
        os.makedirs(namefolder, exist_ok=True)
        Repo.clone_from(url, namefolder)

        #Сделаем конфиг для проекта
        conf = {
            'name':namefile,
            'running':False,
            'start_file':'app.py',
            'url_local':namefolder
        }
        os.makedirs('config', exist_ok=True)
        with open('config/' + namefile + '.json', "w", encoding="utf-8") as f:
            json.dump(conf, f, indent=4, ensure_ascii=False)
        flash("Репозиторий успешно загружен", "success")
    except Exception as e:
        flash(f"Ошибка загрузки репозитория", "danger")
        print(e)  # для логов

    return redirect("/")

@app.route("/api/start/<name>", methods = ['GET'])
def start(name):
    name_file_config = name + '.json'
    start_file = getStartFile(name_file_config)
    url_start = 'projects/' + name + '/' + start_file
    run_detached(url_start)
    setRunningStatus(name, True)
    return redirect('/')

@app.route("/api/stop/<name>", methods = ['GET'])
def stop(name):
    kill_process_by_name(getStartFile(name + '.json'))
    setRunningStatus(name, False)
    return redirect('/')

def run_detached(script):
    urlsplit = script.split('/')
    name_script = urlsplit[0] + "/" + urlsplit[1] + '/logs/' + urlsplit[1]
    os.makedirs(urlsplit[0] + "/" + urlsplit[1] + '/logs', exist_ok=True)
    
    system = platform.system()
    
    with open(f"{name_script}.log", "a", encoding="utf-8") as log_file, \
         open(f"{name_script}_err.log", "a", encoding="utf-8") as err_file:
        
        subprocess.Popen(
            [sys.executable, urlsplit[2]],
            creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0,
            cwd=os.path.abspath(urlsplit[0] + "/" + urlsplit[1]),
            stdout=log_file,
            stderr=err_file,
            bufsize=1,
            text=True,
            close_fds=True
        )

def getallprojects():
    projects = []
    for filename in os.listdir('config'):
        file_path = os.path.join('config', filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                projects.append(content)
    return projects

def kill_process_by_name(script_name):
    script_path = os.path.abspath(script_name)
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmd = proc.info['cmdline']
            if not cmd:
                continue

            if any(os.path.abspath(arg) == script_path for arg in cmd):
                print(f"Убиваем процесс {proc.pid} ({cmd})")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def killall():
    for project in getallprojects():
        kill_process_by_name(getStartFile(project['name'] + '.json'))
        setRunningStatus(project['name'])

def setRunningStatus(name, status=False):
    name = name + '.json'
    for root, _, files in os.walk("config"):
        if name in files:
            path = os.path.join(root, name)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["running"] = status
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

def getStartFile(name):
    for root, _, files in os.walk("config"):
        if name in files:
            path = os.path.join(root, name)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data['start_file']
    return None

def is_script_running(script_path):
    script_path = os.path.abspath(script_path)
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmd = proc.info['cmdline']
            if not cmd:
                continue
            if any(os.path.abspath(arg) == script_path for arg in cmd):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def check_status_all_running():
    for project in getallprojects():
        setRunningStatus(project['name'], is_script_running(project['start_file']))

if __name__ == "__main__":
    killall()
    app.run()
