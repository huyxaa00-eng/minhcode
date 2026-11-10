import os
import json
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

# --- QUẢN LÝ CẤU HÌNH TOKEN ---
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
APP_PORT = 5000

RISH_PATH = "/data/data/com.termux/files/home/.config/rish/rish"

def upload_file_to_github(file_name, content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    data = {"message": f"Auto sync {file_name}", "content": content_encoded}
    if sha: data["sha"] = sha
    return requests.put(url, headers=headers, json=data).status_code in [200, 201]

class AutoManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Vision Macro Pro - Token Config")
        self.root.geometry("480x760")
        self.root.configure(bg="#121212")
        
        style = ttk.Style()
        style.theme_use("clam")

        container = tk.Frame(root, bg="#121212")
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # --- HEADER ---
        header_frame = tk.Frame(container, bg="#1e1e1e", pady=4)
        header_frame.pack(fill=tk.X, pady=(0, 4))
        tk.Label(header_frame, text="🤖 VISION MACRO & TOKEN MANAGER", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#00ffcc").pack()

        # --- 1. CHỌN ỨNG DỤNG & CÀI ĐẶT TOKEN / GITHUB ---
        top_ctrl_frame = tk.Frame(container, bg="#121212")
        top_ctrl_frame.pack(fill=tk.X, pady=2)

        app_frame = tk.LabelFrame(top_ctrl_frame, text=" 📱 Chọn App ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#00E676", bd=1, relief="solid")
        app_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2), ipadx=2, ipady=2)

        app_sub = tk.Frame(app_frame, bg="#121212")
        app_sub.pack(fill=tk.X, padx=2, pady=2)
        self.combo_apps = ttk.Combobox(app_sub, state="readonly", width=12, font=("Segoe UI", 8))
        self.combo_apps.pack(side=tk.LEFT, padx=2)
        self.combo_apps['values'] = ["Toàn bộ màn hình"]
        self.combo_apps.current(0)
        tk.Button(app_sub, text="🔄", bg="#00838F", fg="white", font=("Segoe UI", 7, "bold"), command=self.scan_running_apps).pack(side=tk.LEFT, padx=2)

        # CÁC NÚT ĐỔI TOKEN & QUẢN LÝ GITHUB
        gh_btn_frame = tk.Frame(top_ctrl_frame, bg="#121212")
        gh_btn_frame.pack(side=tk.LEFT, fill=tk.X, padx=(2, 0))
        
        tk.Button(gh_btn_frame, text="🔑 Đổi Token", bg="#607D8B", fg="white", font=("Segoe UI", 7, "bold"), command=self.open_token_config_window).pack(fill=tk.X, padx=1, pady=1)
        tk.Button(gh_btn_frame, text="📂 Quản lý GitHub", bg="#3949AB", fg="white", font=("Segoe UI", 7, "bold"), command=self.open_github_manager).pack(fill=tk.X, padx=1, pady=1)

        # --- 2. BẢNG QUẢN LÝ ẢNH & LỆNH ---
        table_frame = tk.LabelFrame(container, text=" 📋 Danh Sách Ảnh & Gán Lệnh ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#FFD700", bd=1, relief="solid")
        table_frame.pack(fill=tk.X, pady=4, ipadx=3, ipady=2)

        columns = ("filename", "action")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=3)
        self.tree.heading("filename", text="Tên Ảnh")
        self.tree.heading("action", text="Lệnh Gán")
        self.tree.column("filename", width=150, anchor="w")
        self.tree.column("action", width=170, anchor="w")
        self.tree.pack(side=tk.TOP, fill=tk.X, padx=4, pady=2)

        btn_box = tk.Frame(table_frame, bg="#121212")
        btn_box.pack(fill=tk.X, padx=4, pady=2)
        tk.Button(btn_box, text="➕ Thêm Ảnh Trong Máy", bg="#00838F", fg="white", font=("Segoe UI", 7, "bold"), command=self.add_image_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_box, text="❌ Xóa Ảnh Chọn", bg="#D32F2F", fg="white", font=("Segoe UI", 7, "bold"), command=self.remove_selected_image).pack(side=tk.LEFT, padx=2)
        self.tree.insert("", tk.END, values=("template.png", "Click Trái (Tap)"))

        # --- 3. ĐIỀU KHIỂN CHÍNH (CHẠY / DỪNG) ---
        ctrl_frame = tk.LabelFrame(container, text=" ⚡ Điều Khiển Macro ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#2979FF", bd=1, relief="solid")
        ctrl_frame.pack(fill=tk.X, pady=4, ipadx=3, ipady=2)

        cfg_box = tk.Frame(ctrl_frame, bg="#121212")
        cfg_box.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(cfg_box, text="Độ khớp(%):", font=("Segoe UI", 7), bg="#121212", fg="#CCC").grid(row=0, column=0, sticky="w")
        self.spin_thresh = tk.Spinbox(cfg_box, from_=50, to=99, width=5, font=("Consolas", 8))
        self.spin_thresh.delete(0, tk.END); self.spin_thresh.insert(0, "80")
        self.spin_thresh.grid(row=0, column=1, padx=4)

        tk.Label(cfg_box, text="Vòng lặp:", font=("Segoe UI", 7), bg="#121212", fg="#CCC").grid(row=0, column=2, sticky="w", padx=4)
        self.spin_loop = tk.Spinbox(cfg_box, from_=1, to=1000, width=5, font=("Consolas", 8))
        self.spin_loop.delete(0, tk.END); self.spin_loop.insert(0, "1")
        self.spin_loop.grid(row=0, column=3, padx=4)

        run_stop_box = tk.Frame(ctrl_frame, bg="#121212")
        run_stop_box.pack(fill=tk.X, padx=4, pady=2)
        
        self.btn_run_macro = tk.Button(run_stop_box, text="▶ BẮT ĐẦU AUTO", bg="#00ACC1", fg="white", font=("Segoe UI", 8, "bold"), command=self.on_run_assigned_macro)
        self.btn_run_macro.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=3)

        self.btn_stop_macro = tk.Button(run_stop_box, text="⏹ DỪNG AUTO", bg="#D32F2F", fg="white", font=("Segoe UI", 8, "bold"), command=self.on_stop_macro)
        self.btn_stop_macro.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=3)

        # --- HỆ THỐNG & NHẬT KÝ ---
        sys_box = tk.Frame(container, bg="#121212")
        sys_box.pack(fill=tk.X, pady=2)
        tk.Button(sys_box, text="♻️ Reset", bg="#7B1FA2", fg="white", font=("Segoe UI", 7, "bold"), command=self.on_full_reset).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(sys_box, text="🧹 Xóa Log", bg="#EF6C00", fg="white", font=("Segoe UI", 7, "bold"), command=self.on_reset_log).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(sys_box, text="Thoát", bg="#333", fg="#CCC", font=("Segoe UI", 7), command=root.quit).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        log_frame = tk.LabelFrame(container, text=" 📋 Nhật ký ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#AAA", bd=1, relief="solid")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.log_text = tk.Text(log_frame, height=4, bg="#1e1e1e", fg="#00FF00", font=("Consolas", 7), relief="flat")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        self.log_text.insert(tk.END, "[INFO] Đã chuyển sang chế độ cấu hình bằng mã Token!\n")

        self.is_running = True
        self.is_macro_running = False
        threading.Thread(target=self.background_auto_sync_loop, daemon=True).start()
        self.scan_running_apps()

    def open_token_config_window(self):
        """Cửa sổ giao diện gọn gàng chỉ để điền và cập nhật mã Token"""
        cfg_win = tk.Toplevel(self.root)
        cfg_win.title("Cài đặt Mã Token")
        cfg_win.geometry("350x210")
        cfg_win.configure(bg="#121212")

        tk.Label(cfg_win, text="🔑 Cập Nhật Mã Token GitHub", font=("Segoe UI", 9, "bold"), bg="#121212", fg="#00ffcc").pack(pady=10)

        form_frame = tk.Frame(cfg_win, bg="#121212")
        form_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(form_frame, text="Nhập Mã Token Mới:", font=("Segoe UI", 8), bg="#121212", fg="#CCC").pack(anchor="w")
        token_entry = tk.Entry(form_frame, bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 8), width=38, show="*")
        token_entry.pack(fill=tk.X, pady=(2, 6))
        token_entry.insert(0, GITHUB_TOKEN)

        def save_and_restart():
            global GITHUB_TOKEN
            new_token = token_entry.get().strip()

            if not new_token:
                messagebox.showerror("Lỗi", "Mã Token không được để trống!")
                return

            config_data = load_config()
            config_data["GITHUB_TOKEN"] = new_token
            save_config(config_data)

            messagebox.showinfo("Thành công", "Đã lưu mã Token mới! Ứng dụng sẽ khởi động lại.")
            cfg_win.destroy()
            
            # Khởi động lại ứng dụng
            self.is_running = False
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

        btn_box = tk.Frame(cfg_win, bg="#121212")
        btn_box.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(btn_box, text="💾 Lưu & Khởi Động Lại", bg="#00838F", fg="white", font=("Segoe UI", 8, "bold"), command=save_and_restart).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)
        tk.Button(btn_box, text="⬅ Quay Về", bg="#444444", fg="white", font=("Segoe UI", 8, "bold"), command=cfg_win.destroy).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)

    def scan_running_apps(self):
        def _scan():
            try:
                cmd = f"{RISH_PATH} -c 'dumpsys activity activities | grep mResumedActivity'"
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                app_list = ["Toàn bộ màn hình"]
                for line in res.stdout.strip().split("\n"):
                    if "/" in line:
                        for p in line.split():
                            if "/" in p:
                                pkg = p.split("/")[0]
                                if pkg not in app_list: app_list.append(pkg)
                self.root.after(0, lambda: self.combo_apps.config(values=app_list))
                if len(app_list) > 1: self.root.after(0, lambda: self.combo_apps.current(1))
            except Exception: pass
        threading.Thread(target=_scan, daemon=True).start()

    def add_image_dialog(self):
        f_path = filedialog.askopenfilename(title="Chọn ảnh", initialdir="/sdcard/Download", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if f_path:
            f_name = os.path.basename(f_path)
            if not os.path.exists(f_name): shutil.copy(f_path, f_name)
            self.assign_action_for_image(f_name)

    def assign_action_for_image(self, f_name):
        dlg = tk.Toplevel(self.root)
        dlg.title("Gán lệnh")
        dlg.geometry("260x140")
        dlg.configure(bg="#121212")
        tk.Label(dlg, text=f"Ảnh: {f_name}", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#00ffcc").pack(pady=6)
        
        act_var = tk.StringVar(value="Click Trái (Tap)")
        cb = ttk.Combobox(dlg, textvariable=act_var, values=["Click Trái (Tap)", "Double Click", "Nhấn Giữ (Long Press)", "Vuốt Màn Hình (Swipe)"], state="readonly", width=20)
        cb.pack(pady=4)

        def save():
            self.tree.insert("", tk.END, values=(f_name, act_var.get()))
            dlg.destroy()
        tk.Button(dlg, text="Lưu", bg="#00ACC1", fg="white", font=("Segoe UI", 8, "bold"), command=save).pack(pady=6)

    def remove_selected_image(self):
        for item in self.tree.selection(): self.tree.delete(item)

    def open_github_manager(self):
        manager_win = tk.Toplevel(self.root)
        manager_win.title("Quản lý file trên GitHub")
        manager_win.geometry("380x450")
        manager_win.configure(bg="#121212")

        tk.Label(manager_win, text="Danh sách file trên kho GitHub:", font=("Segoe UI", 9, "bold"), bg="#121212", fg="#FFD700").pack(pady=8)

        frame_list = tk.Frame(manager_win, bg="#121212")
        frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(frame_list, bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 9), yscrollcommand=scrollbar.set, selectbackground="#D32F2F")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        file_info_map = {}

        def load_github_files():
            listbox.delete(0, tk.END)
            file_info_map.clear()
            try:
                url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
                headers = {
                    "Authorization": f"token {GITHUB_TOKEN}", 
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Termux-App"
                }
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    data_json = res.json()
                    if isinstance(data_json, list):
                        for item in data_json:
                            name = item.get("name")
                            sha = item.get("sha")
                            file_info_map[name] = sha
                            listbox.insert(tk.END, name)
                    else:
                        listbox.insert(tk.END, "[Trống] Không có file nào.")
                else:
                    listbox.insert(tk.END, f"[Lỗi API] Mã: {res.status_code}")
            except Exception as e:
                listbox.insert(tk.END, f"[Lỗi kết nối] {e}")

        load_github_files()

        def delete_selected_github_file():
            selected = listbox.curselection()
            if not selected:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một file cần xóa!")
                return
            
            filename = listbox.get(selected[0])
            if filename.startswith("["): return
            
            if messagebox.askyesno("Xác nhận xóa", f"Xóa vĩnh viễn file '{filename}' trên GitHub?"):
                sha = file_info_map.get(filename)
                if sha:
                    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
                    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    data = {"message": f"Xóa file {filename}", "sha": sha}
                    del_res = requests.delete(url, headers=headers, json=data)
                    if del_res.status_code in [200, 204]:
                        messagebox.showinfo("Thành công", f"Đã xóa file '{filename}'!")
                        self.log(f"[GITHUB] Đã xóa file '{filename}'")
                        load_github_files()
                    else:
                        messagebox.showerror("Lỗi", f"Xóa thất bại! Mã lỗi: {del_res.status_code}")

        btn_box_gh = tk.Frame(manager_win, bg="#121212")
        btn_box_gh.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_box_gh, text="🗑 Xóa File Đã Chọn", bg="#D32F2F", fg="white", font=("Segoe UI", 8, "bold"), command=delete_selected_github_file).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)
        tk.Button(btn_box_gh, text="⬅ Quay Về Menu", bg="#444444", fg="white", font=("Segoe UI", 8, "bold"), command=manager_win.destroy).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, ipady=4)

    def log(self, msg):
        self.root.after(0, lambda: (self.log_text.insert(tk.END, f"> {msg}\n"), self.log_text.see(tk.END)))

    def background_auto_sync_loop(self):
        last_c = ""
        while self.is_running:
            time.sleep(10)
            if os.path.exists("main.py"):
                with open("main.py", "r", encoding="utf-8") as f: c = f.read()
                if c != last_c:
                    if upload_file_to_github("main.py", c): last_c = c

    def on_stop_macro(self):
        if self.is_macro_running:
            self.is_macro_running = False
            self.log("[MACRO] ⏹ Đã dừng khẩn cấp!")
            messagebox.showinfo("Thông báo", "Đã dừng Auto!")

    def on_run_assigned_macro(self):
        if self.is_macro_running: return
        rows = self.tree.get_children()
        if not rows:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh trong bảng lệnh!")
            return

        selected_app = self.combo_apps.get()
        tasks = [(self.tree.item(r)['values'][0], self.tree.item(r)['values'][1]) for r in rows]
        
        try:
            thresh = float(self.spin_thresh.get()) / 100.0
            loops = int(self.spin_loop.get())
        except ValueError: return

        self.is_macro_running = True
        self.log(f"[MACRO] Bắt đầu chạy trên: [{selected_app}]")

        def task_thread():
            try:
                if selected_app and "Toàn bộ" not in selected_app:
                    subprocess.run(f"{RISH_PATH} -c 'am start -n {selected_app}/.MainActivity' 2>/dev/null", shell=True)
                    time.sleep(1.5)

                for l in range(1, loops + 1):
                    if not self.is_running or not self.is_macro_running: break
                    screen_path = "/sdcard/screen.png"
                    subprocess.run(f"{RISH_PATH} -c '/system/bin/screencap -p {screen_path}'", shell=True)
                    
                    if not os.path.exists(screen_path) or not self.is_macro_running: break
                    screen_raw = cv2.imread(screen_path)
                    if screen_raw is None: continue
                    screen = cv2.cvtColor(screen_raw, cv2.COLOR_BGR2GRAY)

                    found = False
                    for t_file, action in tasks:
                        if not self.is_macro_running or not os.path.exists(t_file): break
                        template_raw = cv2.imread(t_file)
                        if template_raw is None: continue
                        
                        template = cv2.cvtColor(template_raw, cv2.COLOR_BGR2GRAY)
                        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                        _, max_v, _, max_l = cv2.minMaxLoc(res)

                        if max_v >= thresh and self.is_macro_running:
                            cx = max_l[0] + template.shape[1] // 2
                            cy = max_l[1] + template.shape[0] // 2
                            self.log(f"[FOUND] '{t_file}' ({max_v*100:.1f}%) -> {action} tại ({cx}, {cy})")
                            
                            if action == "Click Trái (Tap)": cmd = f"input tap {cx} {cy}"
                            elif action == "Double Click": cmd = f"input tap {cx} {cy} && input tap {cx} {cy}"
                            elif action == "Nhấn Giữ (Long Press)": cmd = f"input swipe {cx} {cy} {cx} {cy} 1000"
                            elif action == "Vuốt Màn Hình (Swipe)": cmd = f"input swipe 500 1500 500 500 300"
                            else: cmd = f"input tap {cx} {cy}"

                            subprocess.run(f"{RISH_PATH} -c '{cmd}'", shell=True)
                            found = True
                            break
                    time.sleep(1.0)

                if self.is_macro_running:
                    self.root.after(0, lambda: messagebox.showinfo("Hoàn tất", "Đã chạy xong kịch bản!"))
                self.is_macro_running = False
            except Exception as e:
                self.is_macro_running = False
                self.log(f"[ERROR] {e}")

        threading.Thread(target=task_thread, daemon=True).start()

    def on_full_reset(self):
        if messagebox.askyesno("Reset", "Tải lại bản mới từ GitHub?"):
            os.system(f"curl -fsSL https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py -o main.py")
            self.is_running = False
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def on_reset_log(self): self.log_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoManagerApp(root)
    root.mainloop()
