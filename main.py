import os
import json
import requests
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import subprocess
import threading
import time
import base64
import cv2
import numpy as np
import shutil

app = Flask(__name__)

# --- CẤU HÌNH & QUẢN LÝ TOKEN ---
CONFIG_FILE = "config.json"

def load_config():
    default_config = {
        "GITHUB_TOKEN": "Ghp_54vJqzvILzQzK9A4rC2DzRzBjNPS4p3DMbWQ",
        "REPO_OWNER": "huyxaa00-eng",
        "REPO_NAME": "my_project"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass

config = load_config()
GITHUB_TOKEN = config.get("GITHUB_TOKEN")
REPO_OWNER = config.get("REPO_OWNER")
REPO_NAME = config.get("REPO_NAME")
RISH_PATH = "/data/data/com.termux/files/home/.config/rish/rish"

# Biến trạng thái toàn cục cho Auto Macro
is_macro_running = False
macro_logs = ["[INFO] Web App Vision Macro đã khởi động sẵn sàng!"]

def log_msg(msg):
    global macro_logs
    print(msg)
    macro_logs.append(f"> {msg}")
    if len(macro_logs) > 50:
        macro_logs.pop(0)

# --- GIAO DIỆN WEB HTML (Giao diện Mobile-First, Đen huyền ảo Cyberpunk) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vision Macro Web Pro</title>
    <style>
        body { background-color: #121212; color: #00ffcc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 10px; }
        h1 { font-size: 18px; text-align: center; color: #00ffcc; margin-bottom: 10px; }
        .card { background: #1e1e1e; border-radius: 8px; padding: 10px; margin-bottom: 10px; border: 1px solid #333; }
        label { font-size: 12px; color: #ccc; display: block; margin-top: 5px; }
        select, input, button { width: 100%; padding: 8px; margin-top: 4px; background: #2b2b2b; color: #fff; border: 1px solid #444; border-radius: 4px; font-size: 13px; box-sizing: border-box; }
        button { font-weight: bold; cursor: pointer; border: none; margin-top: 8px; }
        .btn-run { background: #00ACC1; color: white; }
        .btn-stop { background: #D32F2F; color: white; }
        .btn-gh { background: #3949AB; color: white; }
        .btn-token { background: #607D8B; color: white; }
        table { width: 100%; font-size: 12px; margin-top: 5px; border-collapse: collapse; }
        th, td { border: 1px solid #444; padding: 6px; text-align: left; }
        th { background: #252525; color: #FFD700; }
        #logs { background: #0a0a0a; color: #00FF00; font-family: monospace; font-size: 11px; padding: 8px; height: 120px; overflow-y: scroll; border-radius: 4px; border: 1px solid #333; }
        .row { display: flex; gap: 5px; }
        .col { flex: 1; }
    </style>
</head>
<body>
    <h1>🤖 VISION MACRO WEB PRO</h1>

    <!-- 1. CHỌN APP & TOKEN -->
    <div class="card">
        <label>📱 Chọn App Mục Tiêu:</label>
        <div class="row">
            <select id="target_app" class="col">
                <option value="Toàn bộ màn hình">Toàn bộ màn hình</option>
            </select>
            <button class="btn-token col" onclick="openTokenModal()" style="max-width: 100px;">🔑 Token</button>
        </div>
        <button class="btn-gh" onclick="openGithubManager()" style="margin-top: 8px;">📂 Quản lý & Xóa File GitHub</button>
    </div>

    <!-- 2. ĐIỀU KHIỂN CHÍNH -->
    <div class="card">
        <label>⚡ Cấu Hình & Điều Khiển Macro:</label>
        <div class="row">
            <div class="col">
                <label>Độ khớp (%):</label>
                <input type="number" id="thresh" value="80" min="50" max="99">
            </div>
            <div class="col">
                <label>Vòng lặp:</label>
                <input type="number" id="loops" value="1" min="1" max="1000">
            </div>
        </div>
        <div class="row">
            <button class="btn-run col" onclick="startMacro()">▶ BẮT ĐẦU AUTO</button>
            <button class="btn-stop col" onclick="stopMacro()">⏹ DỪNG AUTO</button>
        </div>
    </div>

    <!-- 3. NHẬT KÝ (LOGS) -->
    <div class="card">
        <label>📋 Nhật Ký Hoạt Động:</label>
        <div id="logs">Đang tải nhật ký...</div>
    </div>

    <script>
        function fetchLogs() {
            fetch('/get_logs')
            .then(res => res.json())
            .then(data => {
                const logBox = document.getElementById('logs');
                logBox.innerHTML = data.logs.join('<br>');
                logBox.scrollTop = logBox.scrollHeight;
            });
        }
        setInterval(fetchLogs, 1500);

        function startMacro() {
            const app = document.getElementById('target_app').value;
            const thresh = document.getElementById('thresh').value;
            const loops = document.getElementById('loops').value;

            fetch('/start_macro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({app: app, thresh: thresh, loops: loops})
            }).then(res => res.json()).then(data => alert(data.message));
        }

        function stopMacro() {
            fetch('/stop_macro', {method: 'POST'})
            .then(res => res.json()).then(data => alert(data.message));
        }

        function openTokenModal() {
            let token = prompt("Nhập mã Token GitHub mới:");
            if (token) {
                fetch('/update_token', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: token})
                }).then(res => res.json()).then(data => {
                    alert(data.message);
                    location.reload();
                });
            }
        }

        function openGithubManager() {
            window.open('/github_manager', '_blank');
        }

        // Tải danh sách app đang chạy
        fetch('/get_apps')
        .then(res => res.json())
        .then(data => {
            const sel = document.getElementById('target_app');
            sel.innerHTML = '<option value="Toàn bộ màn hình">Toàn bộ màn hình</option>';
            data.apps.forEach(app => {
                let opt = document.createElement('option');
                opt.value = app;
                opt.textContent = app;
                sel.appendChild(opt);
            });
        });
    </script>
</body>
</html>
"""

# --- CÁC API BACKEND CỦA FLASK ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": macro_logs})

@app.route('/get_apps')
def get_apps():
    try:
        cmd = f"{RISH_PATH} -c 'dumpsys activity activities | grep mResumedActivity'"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        app_list = []
        for line in res.stdout.strip().split("\n"):
            if "/" in line:
                for p in line.split():
                    if "/" in p:
                        pkg = p.split("/")[0]
                        if pkg not in app_list: app_list.append(pkg)
        return jsonify({"apps": app_list})
    except Exception:
        return jsonify({"apps": []})

@app.route('/update_token', methods=['POST'])
def update_token():
    global GITHUB_TOKEN
    data = request.json
    new_token = data.get("token")
    if new_token:
        cfg = load_config()
        cfg["GITHUB_TOKEN"] = new_token
        save_config(cfg)
        GITHUB_TOKEN = new_token
        return jsonify({"message": "Đã cập nhật Token thành công!"})
    return jsonify({"message": "Token không hợp lệ!"}), 400

@app.route('/stop_macro', methods=['POST'])
def api_stop_macro():
    global is_macro_running
    is_macro_running = False
    log_msg("⏹ Đã gửi tín hiệu dừng khẩn cấp từ Web!")
    return jsonify({"message": "Đã dừng Auto!"})

@app.route('/start_macro', methods=['POST'])
def api_start_macro():
    global is_macro_running
    if is_macro_running:
        return jsonify({"message": "Macro đang chạy rồi!"})
    
    data = request.json
    selected_app = data.get("app")
    try:
        thresh = float(data.get("thresh")) / 100.0
        loops = int(data.get("loops"))
    except ValueError:
        return jsonify({"message": "Tham số không hợp lệ!"}), 400

    is_macro_running = True
    log_msg(f"▶ Bắt đầu chạy Auto trên: [{selected_app}]")

    def run_background_task():
        global is_macro_running
        try:
            if selected_app and "Toàn bộ" not in selected_app:
                subprocess.run(f"{RISH_PATH} -c 'am start -n {selected_app}/.MainActivity' 2>/dev/null", shell=True)
                time.sleep(1.5)

            # Ví dụ kịch bản quét ảnh mẫu template.png có sẵn
            for l in range(1, loops + 1):
                if not is_macro_running: break
                screen_path = "/sdcard/screen.png"
                subprocess.run(f"{RISH_PATH} -c '/system/bin/screencap -p {screen_path}'", shell=True)
                
                if not os.path.exists(screen_path) or not is_macro_running: break
                screen_raw = cv2.imread(screen_path)
                if screen_raw is None: continue
                screen = cv2.cvtColor(screen_raw, cv2.COLOR_BGR2GRAY)

                if os.path.exists("template.png"):
                    template_raw = cv2.imread("template.png")
                    if template_raw is not None:
                        template = cv2.cvtColor(template_raw, cv2.COLOR_BGR2GRAY)
                        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                        _, max_v, _, max_l = cv2.minMaxLoc(res)

                        if max_v >= thresh and is_macro_running:
                            cx = max_l[0] + template.shape[1] // 2
                            cy = max_l[1] + template.shape[0] // 2
                            log_msg(f"✨ Tìm thấy 'template.png' ({max_v*100:.1f}%) tại ({cx}, {cy}) -> Tap!")
                            subprocess.run(f"{RISH_PATH} -c 'input tap {cx} {cy}'", shell=True)
                time.sleep(1.0)

            log_msg("✅ Đã hoàn thành kịch bản Auto!")
        except Exception as e:
            log_msg(f"[LỖI THỰC THI] {e}")
        finally:
            is_macro_running = False

    threading.Thread(target=run_background_task, daemon=True).start()
    return jsonify({"message": "Đã kích hoạt tiến trình Auto chạy ngầm!"})

@app.route('/github_manager')
def github_manager():
    # Giao diện quản lý file GitHub trực tiếp trên web
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>GitHub Manager</title>
        <style>
            body { background: #121212; color: #00ffcc; font-family: monospace; padding: 15px; }
            h2 { color: #FFD700; font-size: 16px; }
            ul { list-style: none; padding: 0; }
            li { background: #1e1e1e; margin: 5px 0; padding: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; }
            button { background: #D32F2F; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 3px; }
            .back { background: #444; margin-top: 15px; width: 100%; padding: 10px; font-weight: bold; color: white; border: none; }
        </style>
    </head>
    <body>
        <h2>📂 Quản lý & Xóa File trên GitHub</h2>
        <ul id="file_list">Đang tải danh sách file...</ul>
        <button class="back" onclick="window.close()">⬅ Đóng Cửa Sổ</button>

        <script>
            function loadFiles() {
                fetch('/api/gh_list')
                .then(res => res.json())
                .then(data => {
                    const ul = document.getElementById('file_list');
                    ul.innerHTML = '';
                    if(data.files && data.files.length > 0) {
                        data.files.forEach(f => {
                            let li = document.createElement('li');
                            li.innerHTML = `<span>${f.name}</span> <button onclick="deleteFile('${f.name}', '${f.sha}')">Xóa</button>`;
                            ul.appendChild(li);
                        });
                    } else {
                        ul.innerHTML = '<li>Không có file nào hoặc lỗi kết nối.</li>';
                    }
                });
            }
            loadFiles();

            function deleteFile(name, sha) {
                if(confirm(`Bạn có chắc muốn xóa file '${name}' không?`)) {
                    fetch('/api/gh_delete', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({name: name, sha: sha})
                    }).then(res => res.json()).then(data => {
                        alert(data.message);
                        loadFiles();
                    });
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/gh_list')
def api_gh_list():
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "Termux-Web"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            items = res.json()
            files = [{"name": item.get("name"), "sha": item.get("sha")} for item in items if isinstance(item, dict)]
            return jsonify({"files": files})
    except Exception:
        pass
    return jsonify({"files": []})

@app.route('/api/gh_delete', methods=['POST'])
def api_gh_delete():
    data = request.json
    filename = data.get("name")
    sha = data.get("sha")
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        payload = {"message": f"Xóa file {filename} qua Web", "sha": sha}
        res = requests.delete(url, headers=headers, json=payload)
        if res.status_code in [200, 204]:
            return jsonify({"message": f"Đã xóa file '{filename}' thành công!"})
    except Exception as e:
        pass
    return jsonify({"message": "Xóa thất bại!"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
