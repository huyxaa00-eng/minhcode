import os
import requests
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import subprocess
import sys
import threading
import time
import base64
import socket
import random
import cv2
import numpy as np
import shutil

# Cấu hình GitHub và Port ứng dụng
GITHUB_TOKEN = "Ghp_54vJqzvILzQzK9A4rC2DzRzBjNPS4p3DMbWQ"
REPO_OWNER = "huyxaa00-eng"
REPO_NAME = "my_project"
APP_PORT = 5000

RISH_PATH = "/data/data/com.termux/files/home/.config/rish/rish"

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
        self.root.title("🤖 Vision Macro Pro - Chọn App & Gán Lệnh")
        self.root.geometry("500x850")
        self.root.configure(bg="#121212")
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # --- HEADER ---
        header_frame = tk.Frame(root, bg="#1e1e1e", pady=6)
        header_frame.pack(fill=tk.X, padx=10, pady=(6, 2))
        
        title_label = tk.Label(header_frame, text="🤖 VISION MACRO & CHỌN APP MỤC TIÊU", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#00ffcc")
        title_label.pack()

        # --- MENU 1: CHỌN APP ĐANG CHẠY (Làm nổi bật cực rõ ở đây) ---
        app_frame = tk.LabelFrame(root, text=" 📱 1. CHỌN ỨNG DỤNG CẦN TÌM ẢNH ", font=("Segoe UI", 9, "bold"), bg="#121212", fg="#00E676", bd=2, relief="groove")
        app_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=5, ipady=5)

        app_sub_frame = tk.Frame(app_frame, bg="#121212")
        app_sub_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(app_sub_frame, text="App:", font=("Segoe UI", 9, "bold"), bg="#121212", fg="#FFFFFF").pack(side=tk.LEFT, padx=2)
        
        self.combo_apps = ttk.Combobox(app_sub_frame, state="readonly", width=24, font=("Segoe UI", 9))
        self.combo_apps.pack(side=tk.LEFT, padx=5)
        self.combo_apps['values'] = ["Toàn bộ màn hình (Mặc định)", "Đang quét app..."]
        self.combo_apps.current(0)

        btn_refresh_apps = tk.Button(app_sub_frame, text="🔄 Quét App", bg="#00838F", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", command=self.scan_running_apps)
        btn_refresh_apps.pack(side=tk.LEFT, padx=2, ipadx=6, ipady=2)

        # --- MENU 2: BẢNG QUẢN LÝ ẢNH & GÁN LỆNH ---
        table_frame = tk.LabelFrame(root, text=" 📋 2. Danh Sách Ảnh Mẫu & Lệnh Gán ", font=("Segoe UI", 9, "bold"), bg="#121212", fg="#FFD700", bd=2, relief="groove")
        table_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=5, ipady=3)

        columns = ("filename", "action")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=3)
        self.tree.heading("filename", text="Tên File Ảnh")
        self.tree.heading("action", text="Lệnh Gán (Hành động)")
        self.tree.column("filename", width=160, anchor="w")
        self.tree.column("action", width=180, anchor="w")
        self.tree.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        btn_action_frame = tk.Frame(table_frame, bg="#121212")
        btn_action_frame.pack(fill=tk.X, padx=5, pady=2)

        btn_add_img = tk.Button(btn_action_frame, text="➕ Chọn Ảnh Trong Máy", bg="#00838F", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", command=self.add_image_dialog)
        btn_add_img.pack(side=tk.LEFT, padx=2, ipadx=5, ipady=2)

        btn_del_img = tk.Button(btn_action_frame, text="❌ Xóa Ảnh", bg="#D32F2F", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", command=self.remove_selected_image)
        btn_del_img.pack(side=tk.LEFT, padx=5, ipadx=5, ipady=2)

        self.tree.insert("", tk.END, values=("template.png", "Click Trái (Tap)"))

        # --- CẤU HÌNH CHUNG ---
        config_frame = tk.Frame(root, bg="#121212")
        config_frame.pack(fill=tk.X, padx=10, pady=4)

        lbl_thresh = tk.Label(config_frame, text="Độ khớp (%):", font=("Segoe UI", 8), bg="#121212", fg="#CCCCCC")
        lbl_thresh.grid(row=0, column=0, sticky="w", padx=2)
        self.spin_thresh = tk.Spinbox(config_frame, from_=50, to=99, bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 8), width=5)
        self.spin_thresh.delete(0, tk.END)
        self.spin_thresh.insert(0, "80")
        self.spin_thresh.grid(row=0, column=1, padx=5)

        lbl_loop = tk.Label(config_frame, text="Số Vòng Lặp:", font=("Segoe UI", 8), bg="#121212", fg="#CCCCCC")
        lbl_loop.grid(row=0, column=2, sticky="w", padx=2)
        self.spin_loop = tk.Spinbox(config_frame, from_=1, to=1000, bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 8), width=5)
        self.spin_loop.delete(0, tk.END)
        self.spin_loop.insert(0, "1")
        self.spin_loop.grid(row=0, column=3, padx=5)

        # --- CANVAS SÓNG NHẠC ---
        visual_frame = tk.LabelFrame(root, text=" 🎵 Sóng nhạc trực quan ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#FF007F", bd=1, relief="solid")
        visual_frame.pack(fill=tk.X, padx=10, pady=4)
        
        self.canvas = tk.Canvas(visual_frame, width=470, height=25, bg="#181818", highlightthickness=0)
        self.canvas.pack(padx=5, pady=2)
        self.bars = [random.randint(3, 18) for _ in range(24)]

        # --- ĐIỀU KHIỂN CHÍNH ---
        group_github = tk.LabelFrame(root, text=" 🌐 Điều khiển Macro ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#2979FF", bd=1, relief="solid")
        group_github.pack(fill=tk.X, padx=10, pady=4, ipadx=5, ipady=2)
        
        self.create_styled_button(group_github, "▶ Chạy trực tiếp từ GitHub", "#2979FF", self.on_run_github)
        self.create_styled_button(group_github, "🔍 Chạy Auto Theo App & Lệnh Đã Gán", "#00ACC1", self.on_run_assigned_macro)

        # --- HỆ THỐNG ---
        group_system = tk.Frame(root, bg="#121212")
        group_system.pack(fill=tk.X, padx=10, pady=2)
        
        tk.Button(group_system, text="♻️ Reset", bg="#7B1FA2", fg="white", font=("Segoe UI", 8, "bold"), command=self.on_full_reset).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=2)
        tk.Button(group_system, text="🧹 Xóa Log", bg="#EF6C00", fg="white", font=("Segoe UI", 8, "bold"), command=self.on_reset_log).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=2)
        tk.Button(group_system, text="Thoát", bg="#333333", fg="#CCCCCC", font=("Segoe UI", 8), command=root.quit).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=2)

        # --- NHẬT KÝ (LOG) ---
        group_log = tk.LabelFrame(root, text=" 📋 Nhật ký ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#AAAAAA", bd=1, relief="solid")
        group_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=4, ipadx=5, ipady=2)
        
        self.log_text = tk.Text(group_log, height=3, bg="#1e1e1e", fg="#00FF00", font=("Consolas", 8), relief="flat", highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.log_text.insert(tk.END, "[INFO] Giao diện đã được tối ưu hiển thị đầy đủ menu!\n")

        self.is_running = True
        self.sync_thread = threading.Thread(target=self.background_auto_sync_loop, daemon=True)
        self.sync_thread.start()

        self.update_visualizer()
        self.scan_running_apps()

    def create_styled_button(self, parent, text, bg_color, command):
        btn = tk.Button(parent, text=text, bg=bg_color, fg="white", font=("Segoe UI", 8, "bold"), 
                        relief="flat", bd=0, cursor="hand2", command=command)
        btn.pack(fill=tk.X, padx=4, pady=2, ipady=2)
        return btn

    def scan_running_apps(self):
        def _scan():
            try:
                cmd = f"{RISH_PATH} -c 'dumpsys activity activities | grep mResumedActivity'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = result.stdout.strip()
                
                app_list = ["Toàn bộ màn hình (Mặc định)"]
                for line in output.split("\n"):
                    if "/" in line:
                        for p in line.split():
                            if "/" in p:
                                pkg = p.split("/")[0]
                                if pkg not in app_list:
                                    app_list.append(pkg)
                
                common_apps = ["com.tencent.ig", "com.vng.pubgmobile", "com.garena.game.kgvn"]
                for ca in common_apps:
                    if ca not in app_list:
                        app_list.append(ca)

                self.root.after(0, lambda: self.combo_apps.config(values=app_list))
                if len(app_list) > 1:
                    self.root.after(0, lambda: self.combo_apps.current(1))
                self.log("[APP] Đã quét và cập nhật danh sách ứng dụng.")
            except Exception as e:
                self.log(f"[APP ERROR] {e}")

        threading.Thread(target=_scan, daemon=True).start()

    def add_image_dialog(self):
        initial_dir = "/sdcard/Download" if os.path.exists("/sdcard/Download") else "/sdcard/"
        file_path = filedialog.askopenfilename(title="Chọn ảnh mẫu", initialdir=initial_dir, filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            file_name = os.path.basename(file_path)
            if not os.path.exists(file_name):
                shutil.copy(file_path, file_name)
            self.assign_action_for_image(file_name)

    def assign_action_for_image(self, file_name):
        dialog = tk.Toplevel(self.root)
        dialog.title("Gán Lệnh Cho Ảnh")
        dialog.geometry("300x180")
        dialog.configure(bg="#121212")

        tk.Label(dialog, text=f"Ảnh: {file_name}", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#00ffcc").pack(pady=10)
        tk.Label(dialog, text="Chọn hành động:", font=("Segoe UI", 8), bg="#121212", fg="#CCCCCC").pack()

        action_var = tk.StringVar(value="Click Trái (Tap)")
        actions = ["Click Trái (Tap)", "Double Click", "Nhấn Giữ (Long Press)", "Vuốt Màn Hình (Swipe)"]
        dropdown = ttk.Combobox(dialog, textvariable=action_var, values=actions, state="readonly", width=22)
        dropdown.pack(pady=5)

        def save_assignment():
            self.tree.insert("", tk.END, values=(file_name, action_var.get()))
            self.log(f"[CONFIG] Đã gán lệnh cho '{file_name}'")
            dialog.destroy()

        tk.Button(dialog, text="Lưu Vào Bảng", bg="#00ACC1", fg="white", font=("Segoe UI", 8, "bold"), command=save_assignment).pack(pady=10, ipadx=10)

    def remove_selected_image(self):
        for item in self.tree.selection():
            self.tree.delete(item)

    def update_visualizer(self):
        if not self.is_running:
            return
        self.canvas.delete("all")
        for i in range(len(self.bars)):
            self.bars[i] += (random.randint(2, 15) - self.bars[i]) * 0.4
            h = self.bars[i]
            self.canvas.create_rectangle(i * 19 + 2, 25 - h, (i + 1) * 19 - 2, 25, fill=["#00ffcc", "#0099ff", "#FF007F"][i % 3], outline="")
        self.root.after(100, self.update_visualizer)

    def log(self, message):
        self.root.after(0, lambda: (self.log_text.insert(tk.END, f"> {message}\n"), self.log_text.see(tk.END)))

    def background_auto_sync_loop(self):
        last_content = ""
        while self.is_running:
            time.sleep(10)
            if os.path.exists("main.py"):
                with open("main.py", "r", encoding="utf-8") as f:
                    content = f.read()
                if content != last_content:
                    if upload_file_to_github("main.py", content):
                        last_content = content

    def on_run_github(self):
        subprocess.Popen(f"curl -fsSL https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py | python", shell=True)
        messagebox.showinfo("Thành công", "Đã khởi chạy từ GitHub!")

    def on_run_assigned_macro(self):
        rows = self.tree.get_children()
        if not rows:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh trong bảng lệnh!")
            return

        selected_app = self.combo_apps.get()
        tasks = [(self.tree.item(r)['values'][0], self.tree.item(r)['values'][1]) for r in rows]
        
        try:
            threshold_val = float(self.spin_thresh.get()) / 100.0
            total_loops = int(self.spin_loop.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Kiểm tra lại độ khớp hoặc vòng lặp!")
            return

        self.log(f"[MACRO] Chạy trên App: [{selected_app}]")

        def vision_task():
            try:
                if selected_app and "Toàn bộ" not in selected_app:
                    subprocess.run(f"{RISH_PATH} -c 'am start -n {selected_app}/.MainActivity' 2>/dev/null", shell=True)
                    time.sleep(1.5)

                for loop in range(1, total_loops + 1):
                    if not self.is_running: break
                    screenshot_path = "/sdcard/screen.png"
                    subprocess.run(f"{RISH_PATH} -c '/system/bin/screencap -p {screenshot_path}'", shell=True)
                    
                    if not os.path.exists(screenshot_path): break
                    screen = cv2.imread(screenshot_path)
                    found = False

                    for t_file, action in tasks:
                        if not os.path.exists(t_file): continue
                        template = cv2.imread(t_file)
                        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(res)

                        if max_val >= threshold_val:
                            cx = max_loc[0] + template.shape[1] // 2
                            cy = max_loc[1] + template.shape[0] // 2
                            self.log(f"[FOUND] '{t_file}' ({max_val*100:.1f}%) -> {action} tại ({cx}, {cy})")
                            
                            if action == "Click Trái (Tap)":
                                cmd = f"input tap {cx} {cy}"
                            elif action == "Double Click":
                                cmd = f"input tap {cx} {cy} && input tap {cx} {cy}"
                            elif action == "Nhấn Giữ (Long Press)":
                                cmd = f"input swipe {cx} {cy} {cx} {cy} 1000"
                            elif action == "Vuốt Màn Hình (Swipe)":
                                cmd = f"input swipe 500 1500 500 500 300"
                            else:
                                cmd = f"input tap {cx} {cy}"

                            subprocess.run(f"{RISH_PATH} -c '{cmd}'", shell=True)
                            found = True
                            break
                    time.sleep(1.0)
                self.root.after(0, lambda: messagebox.showinfo("Hoàn tất", "Đã chạy xong kịch bản!"))
            except Exception as e:
                self.log(f"[ERROR] {e}")

        threading.Thread(target=vision_task, daemon=True).start()

    def on_delete(self):
        if messagebox.askyesno("Xác nhận", "Xóa file trên GitHub?"):
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
            res = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"})
            if res.status_code == 200:
                requests.delete(url, headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"message": "Del", "sha": res.json().get("sha")})

    def on_full_reset(self):
        if messagebox.askyesno("Reset", "Tải lại bản mới từ GitHub?"):
            os.system(f"curl -fsSL https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py -o main.py")
            self.is_running = False
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def on_reset_log(self):
        self.log_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoManagerApp(root)
    root.mainloop()
