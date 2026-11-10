import os
import requests
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import sys
import threading
import time
import base64
import socket
import random

# Cấu hình GitHub và Port ứng dụng
GITHUB_TOKEN = "Ghp_54vJqzvILzQzK9A4rC2DzRzBjNPS4p3DMbWQ"
REPO_OWNER = "huyxaa00-eng"
REPO_NAME = "my_project"
APP_PORT = 5000

def check_and_free_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
    except Exception:
        pass

def upload_file_to_github(file_name, content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
        
    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": f"Auto sync {file_name} từ Termux",
        "content": content_encoded
    }
    if sha:
        data["sha"] = sha
        
    put_response = requests.put(url, headers=headers, json=data)
    return put_response.status_code in [200, 201]

class AutoManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Trạm Quản Lý Tự Động & Macro Pro")
        self.root.geometry("500x680")
        self.root.configure(bg="#121212")
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # --- HEADER ---
        header_frame = tk.Frame(root, bg="#1e1e1e", pady=10)
        header_frame.pack(fill=tk.X, padx=15, pady=(12, 5))
        
        title_label = tk.Label(header_frame, text="QUẢN LÝ HỆ THỐNG AUTO & MACRO", font=("Segoe UI", 12, "bold"), bg="#1e1e1e", fg="#00ffcc")
        title_label.pack()
        
        sub_label = tk.Label(header_frame, text="Trạng thái: Đồng bộ GitHub, Sóng nhạc & Auto Click Đa Điểm", font=("Segoe UI", 8), bg="#1e1e1e", fg="#888888")
        sub_label.pack(pady=(2, 0))

        # --- NHÓM 1: CANVAS HIỆU ỨNG SÓNG NHẠC ---
        visual_frame = tk.LabelFrame(root, text=" 🎵 Sóng nhạc trực quan (Visualizer) ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#FF007F", bd=1, relief="solid")
        visual_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.canvas = tk.Canvas(visual_frame, width=460, height=70, bg="#181818", highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)
        self.bars = [random.randint(10, 50) for _ in range(24)]

        # --- NHÓM 2: ĐIỀU KHIỂN GITHUB & MACRO CLICK ---
        group_github = tk.LabelFrame(root, text=" 🌐 Điều khiển GitHub & Macro Auto ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#2979FF", bd=1, relief="solid")
        group_github.pack(fill=tk.X, padx=15, pady=5, ipadx=5, ipady=4)
        
        self.create_styled_button(group_github, "▶ Chạy trực tiếp từ GitHub", "#2979FF", self.on_run_github)
        self.create_styled_button(group_github, "⚡ Chạy Macro Auto Click (Đa điểm)", "#00ACC1", self.on_macro_click)
        self.create_styled_button(group_github, "🗑 Xóa file main.py trên GitHub", "#D32F2F", self.on_delete)

        # --- NHÓM 3: HỆ THỐNG & TIẾN TRÌNH ---
        group_system = tk.LabelFrame(root, text=" ⚙️ Hệ thống & Port ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#00E676", bd=1, relief="solid")
        group_system.pack(fill=tk.X, padx=15, pady=5, ipadx=5, ipady=4)
        
        self.create_styled_button(group_system, "♻️ Reset toàn bộ & Khởi động lại", "#7B1FA2", self.on_full_reset)
        self.create_styled_button(group_system, "🧹 Làm mới bảng nhật ký", "#EF6C00", self.on_reset_log)

        # --- NHÓM 4: KHUNG NHẬT KÝ (LOG) ---
        group_log = tk.LabelFrame(root, text=" 📋 Nhật ký hoạt động ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#AAAAAA", bd=1, relief="solid")
        group_log.pack(fill=tk.BOTH, expand=True, padx=15, pady=5, ipadx=5, ipady=2)
        
        self.log_text = tk.Text(group_log, height=4, bg="#1e1e1e", fg="#00FF00", font=("Consolas", 8), relief="flat", highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.insert(tk.END, "[INFO] Hệ thống sẵn sàng với Macro Engine chuyên nghiệp...\n")

        # --- FOOTER: THOÁT ---
        footer_frame = tk.Frame(root, bg="#121212")
        footer_frame.pack(fill=tk.X, padx=15, pady=(2, 10))
        
        exit_btn = tk.Button(footer_frame, text="Thoát ứng dụng", bg="#333333", fg="#CCCCCC", font=("Segoe UI", 8), relief="flat", bd=0, cursor="hand2", command=root.quit)
        exit_btn.pack(fill=tk.X, ipady=4)

        # Kích hoạt luồng chạy ngầm đồng bộ & sóng nhạc
        self.is_running = True
        self.sync_thread = threading.Thread(target=self.background_auto_sync_loop, daemon=True)
        self.sync_thread.start()

        self.update_visualizer()

    def create_styled_button(self, parent, text, bg_color, command):
        btn = tk.Button(parent, text=text, bg=bg_color, fg="white", font=("Segoe UI", 8, "bold"), 
                        relief="flat", bd=0, cursor="hand2", command=command)
        btn.pack(fill=tk.X, padx=8, pady=2, ipady=3)
        return btn

    def update_visualizer(self):
        if not self.is_running:
            return
        self.canvas.delete("all")
        width = 460
        num_bars = len(self.bars)
        bar_w = width / num_bars

        colors = ["#00ffcc", "#0099ff", "#9370DB", "#FF007F"]

        for i in range(num_bars):
            target = random.randint(8, 50)
            self.bars[i] += (target - self.bars[i]) * 0.4
            h = self.bars[i]
            x1 = i * bar_w + 2
            y1 = 70 - h
            x2 = (i + 1) * bar_w - 2
            y2 = 70
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        self.root.after(100, self.update_visualizer)

    def log(self, message):
        def _log():
            self.log_text.insert(tk.END, f"> {message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, _log)

    def background_auto_sync_loop(self):
        last_content = ""
        while self.is_running:
            time.sleep(10)
            if not self.is_running:
                break
            try:
                file_name = "main.py"
                if os.path.exists(file_name):
                    with open(file_name, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    if content != last_content:
                        success = upload_file_to_github(file_name, content)
                        if success:
                            last_content = content
                            self.log("[SYNC] Da tu dong day ban cap nhat len GitHub")
            except Exception:
                pass

    def on_run_github(self):
        try:
            self.log("Dang kiem tra va giai phong port...")
            check_and_free_port(APP_PORT)
            
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py"
            cmd = f"curl -fsSL {url} | python"
            subprocess.Popen(cmd, shell=True)
            self.log("Da khoi chay kich ban thanh cong!")
            messagebox.showinfo("Thành công", "Đã giải phóng port và khởi chạy từ GitHub!")
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")

    def on_macro_click(self):
        """Hệ thống Macro Auto Click đa điểm chuyên nghiệp (Tap, Swipe, Delay, Loop)"""
        self.log("[MACRO] Bắt đầu thực thi chuỗi Auto Click đa điểm...")
        
        def macro_task():
            try:
                # Kịch bản mẫu (Bạn có thể tinh chỉnh tọa độ X, Y và thời gian trễ theo ý muốn)
                # Định dạng: ('tap', x, y, delay_seconds) hoặc ('swipe', x1, y1, x2, y2, duration_seconds)
                macro_actions = [
                    ('tap', 500, 1200, 1.0),                  # Click nút vào trận / bắt đầu
                    ('tap', 300, 800, 0.5),                   # Click chọn vị trí / mục tiêu 1
                    ('swipe', 200, 1000, 800, 1000, 0.5),     # Vuốt màn hình cuộn danh sách
                    ('tap', 700, 1200, 2.0)                   # Click xác nhận
                ]
                
                loops = 3  # Số vòng lặp kịch bản
                for current_loop in range(1, loops + 1):
                    self.log(f"[MACRO] --- Vòng lặp {current_loop}/{loops} ---")
                    
                    for action in macro_actions:
                        if action[0] == 'tap':
                            _, x, y, delay = action
                            self.log(f"[MACRO] Tap tại tọa độ: X={x}, Y={y}")
                            subprocess.run(f"input tap {x} {y}", shell=True)
                            time.sleep(delay)
                            
                        elif action[0] == 'swipe':
                            _, x1, y1, x2, y2, duration = action
                            self.log(f"[MACRO] Swipe từ ({x1},{y1}) đến ({x2},{y2})")
                            subprocess.run(f"input swipe {x1} {y1} {x2} {y2} {int(duration * 1000)}", shell=True)
                            time.sleep(1.0)
                            
                    time.sleep(1.5)
                
                self.log("[MACRO] Hoàn thành chuỗi kịch bản tự động!")
                self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã chạy xong chuỗi Macro Auto Click!"))
                
            except Exception as e:
                self.log(f"[MACRO ERROR] {str(e)}")

        threading.Thread(target=macro_task, daemon=True).start()

    def on_delete(self):
        if messagebox.askyesno("Xác nhận", "Xóa file main.py trên GitHub?"):
            self.log("Dang xoa file tren GitHub...")
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                sha = res.json().get("sha")
                del_res = requests.delete(url, headers=headers, json={"message": "Xóa qua GUI", "sha": sha})
                if del_res.status_code == 200:
                    self.log("Da xoa file thanh cong tren GitHub.")
                    messagebox.showinfo("Thành công", "Đã xóa file trên GitHub!")
                else:
                    self.log(f"Loi xoa: Status {del_res.status_code}")
                    messagebox.showerror("Lỗi", f"Không thể xóa! Mã lỗi: {del_res.status_code}")
            else:
                self.log(f"Khong tim thay file tren GitHub (Status: {res.status_code})")
                messagebox.showerror("Lỗi", "Không tìm thấy file main.py trên GitHub để xóa!")

    def on_full_reset(self):
        if messagebox.askyesno("Xác nhận Reset", "Hệ thống sẽ tải lại bản mới nhất từ GitHub và khởi động lại. Tiếp tục?"):
            self.log("Dang tien hanh reset he thong...")
            try:
                check_and_free_port(APP_PORT)
                url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py"
                os.system(f"curl -fsSL {url} -o main.py")
                self.is_running = False
                messagebox.showinfo("Thành công", "Đã reset và tải lại phiên bản mới thành công!")
                self.root.destroy()
                os.execl(sys.executable, sys.executable, *sys.argv)
            except Exception as e:
                self.log(f"[RESET ERROR] {str(e)}")

    def on_reset_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log("Da lam moi bang dieu khiển.")

if __name__ == "__main__":
    check_and_free_port(APP_PORT)
    root = tk.Tk()
    app = AutoManagerApp(root)
    root.mainloop()
