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

# Cấu hình GitHub và Port ứng dụng
GITHUB_TOKEN = "Ghp_54vJqzvILzQzK9A4rC2DzRzBjNPS4p3DMbWQ"
REPO_OWNER = "huyxaa00-eng"
REPO_NAME = "my_project"
APP_PORT = 5000

# Đường dẫn rish chuẩn cho Android 14+
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
        self.root.title("🤖 Trạm Quản Lý Vision Macro - Quản Lý Ảnh & Lệnh Riêng")
        self.root.geometry("500x820")
        self.root.configure(bg="#121212")
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # --- HEADER ---
        header_frame = tk.Frame(root, bg="#1e1e1e", pady=8)
        header_frame.pack(fill=tk.X, padx=15, pady=(8, 4))
        
        title_label = tk.Label(header_frame, text="QUẢN LÝ DANH SÁCH ẢNH & GÁN LỆNH", font=("Segoe UI", 10, "bold"), bg="#1e1e1e", fg="#00ffcc")
        title_label.pack()
        
        sub_label = tk.Label(header_frame, text="Trạng thái: Tùy chỉnh hành động riêng cho từng ảnh mẫu", font=("Segoe UI", 7), bg="#1e1e1e", fg="#888888")
        sub_label.pack(pady=(2, 0))

        # --- NHÓM 1: BẢNG QUẢN LÝ ẢNH & GÁN LỆNH ---
        table_frame = tk.LabelFrame(root, text=" 📋 Danh Sách Ảnh Mẫu & Lệnh Gán Riêng ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#FFD700", bd=1, relief="solid")
        table_frame.pack(fill=tk.X, padx=15, pady=4, ipadx=5, ipady=3)

        # Tạo bảng Treeview hiển thị (Tên ảnh | Hành động)
        columns = ("filename", "action")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
        self.tree.heading("filename", text="Tên File Ảnh")
        self.tree.heading("action", text="Lệnh Gán (Hành động)")
        self.tree.column("filename", width=160, anchor="w")
        self.tree.column("action", width=180, anchor="w")
        self.tree.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Các nút thao tác với bảng
        btn_action_frame = tk.Frame(table_frame, bg="#121212")
        btn_action_frame.pack(fill=tk.X, padx=5, pady=2)

        btn_add_img = tk.Button(btn_action_frame, text="➕ Thêm Ảnh & Lệnh", bg="#00838F", fg="white", font=("Segoe UI", 7, "bold"), relief="flat", command=self.add_image_dialog)
        btn_add_img.pack(side=tk.LEFT, padx=2, ipadx=4)

        btn_del_img = tk.Button(btn_action_frame, text="❌ Xóa Ảnh Chọn", bg="#D32F2F", fg="white", font=("Segoe UI", 7, "bold"), relief="flat", command=self.remove_selected_image)
        btn_del_img.pack(side=tk.LEFT, padx=2, ipadx=4)

        # Thêm sẵn 1-2 mẫu mặc định để demo
        self.tree.insert("", tk.END, values=("template.png", "Click Trái (Tap)"))

        # --- NHÓM 2: CẤU HÌNH CHUNG ---
        config_frame = tk.Frame(root, bg="#121212")
        config_frame.pack(fill=tk.X, padx=15, pady=4)

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

        # --- NHÓM 3: CANVAS SÓNG NHẠC ---
        visual_frame = tk.LabelFrame(root, text=" 🎵 Sóng nhạc trực quan ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#FF007F", bd=1, relief="solid")
        visual_frame.pack(fill=tk.X, padx=15, pady=4)
        
        self.canvas = tk.Canvas(visual_frame, width=460, height=35, bg="#181818", highlightthickness=0)
        self.canvas.pack(padx=5, pady=3)
        self.bars = [random.randint(5, 25) for _ in range(24)]

        # --- NHÓM 4: ĐIỀU KHIỂN CHÍNH ---
        group_github = tk.LabelFrame(root, text=" 🌐 Điều khiển GitHub & Macro ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#2979FF", bd=1, relief="solid")
        group_github.pack(fill=tk.X, padx=15, pady=4, ipadx=5, ipady=3)
        
        self.create_styled_button(group_github, "▶ Chạy trực tiếp từ GitHub", "#2979FF", self.on_run_github)
        self.create_styled_button(group_github, "🔍 Chạy Auto Theo Bảng Lệnh Đã Gán", "#00ACC1", self.on_run_assigned_macro)
        self.create_styled_button(group_github, "🗑 Xóa file main.py trên GitHub", "#D32F2F", self.on_delete)

        # --- NHÓM 5: HỆ THỐNG ---
        group_system = tk.LabelFrame(root, text=" ⚙️ Hệ thống ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#00E676", bd=1, relief="solid")
        group_system.pack(fill=tk.X, padx=15, pady=4, ipadx=5, ipady=3)
        
        self.create_styled_button(group_system, "♻️ Reset toàn bộ & Khởi động lại", "#7B1FA2", self.on_full_reset)
        self.create_styled_button(group_system, "🧹 Làm mới bảng nhật ký", "#EF6C00", self.on_reset_log)

        # --- NHÓM 6: NHẬT KÝ (LOG) ---
        group_log = tk.LabelFrame(root, text=" 📋 Nhật ký hoạt động ", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#AAAAAA", bd=1, relief="solid")
        group_log.pack(fill=tk.BOTH, expand=True, padx=15, pady=4, ipadx=5, ipady=2)
        
        self.log_text = tk.Text(group_log, height=4, bg="#1e1e1e", fg="#00FF00", font=("Consolas", 8), relief="flat", highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=4)
        self.log_text.insert(tk.END, "[INFO] Hệ thống quản lý lệnh theo ảnh đã sẵn sàng...\n")

        # --- FOOTER ---
        footer_frame = tk.Frame(root, bg="#121212")
        footer_frame.pack(fill=tk.X, padx=15, pady=(2, 6))
        
        exit_btn = tk.Button(footer_frame, text="Thoát ứng dụng", bg="#333333", fg="#CCCCCC", font=("Segoe UI", 8), relief="flat", bd=0, cursor="hand2", command=root.quit)
        exit_btn.pack(fill=tk.X, ipady=2)

        self.is_running = True
        self.sync_thread = threading.Thread(target=self.background_auto_sync_loop, daemon=True)
        self.sync_thread.start()

        self.update_visualizer()

    def create_styled_button(self, parent, text, bg_color, command):
        btn = tk.Button(parent, text=text, bg=bg_color, fg="white", font=("Segoe UI", 8, "bold"), 
                        relief="flat", bd=0, cursor="hand2", command=command)
        btn.pack(fill=tk.X, padx=6, pady=2, ipady=2)
        return btn

    def add_image_dialog(self):
        """Mở cửa sổ phụ để chọn ảnh và chọn lệnh gán tương ứng"""
        file_path = filedialog.askopenfilename(title="Chọn file ảnh mẫu", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return
        
        file_name = os.path.basename(file_path)
        if not os.path.exists(file_name):
            import shutil
            shutil.copy(file_path, file_name)

        # Tạo cửa sổ nhỏ để chọn lệnh gán cho ảnh này
        dialog = tk.Toplevel(self.root)
        dialog.title("Gán Lệnh Cho Ảnh")
        dialog.geometry("300x180")
        dialog.configure(bg="#121212")

        tk.Label(dialog, text=f"Ảnh: {file_name}", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#00ffcc").pack(pady=10)
        tk.Label(dialog, text="Chọn hành động (Lệnh):", font=("Segoe UI", 8), bg="#121212", fg="#CCCCCC").pack()

        action_var = tk.StringVar(value="Click Trái (Tap)")
        actions = ["Click Trái (Tap)", "Double Click", "Nhấn Giữ (Long Press)", "Vuốt Màn Hình (Swipe)"]
        
        dropdown = ttk.Combobox(dialog, textvariable=action_var, values=actions, state="readonly", width=22)
        dropdown.pack(pady=5)

        def save_assignment():
            chosen_action = action_var.get()
            self.tree.insert("", tk.END, values=(file_name, chosen_action))
            self.log(f"[CONFIG] Đã gán lệnh '{chosen_action}' cho ảnh '{file_name}'")
            dialog.destroy()

        tk.Button(dialog, text="Lưu Cấu Hình", bg="#00ACC1", fg="white", font=("Segoe UI", 8, "bold"), command=save_assignment).pack(pady=10, ipadx=10)

    def remove_selected_image(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            self.tree.delete(item)
        self.log("[CONFIG] Đã xóa ảnh được chọn khỏi danh sách.")

    def update_visualizer(self):
        if not self.is_running:
            return
        self.canvas.delete("all")
        width = 460
        num_bars = len(self.bars)
        bar_w = width / num_bars
        colors = ["#00ffcc", "#0099ff", "#9370DB", "#FF007F"]

        for i in range(num_bars):
            target = random.randint(4, 25)
            self.bars[i] += (target - self.bars[i]) * 0.4
            h = self.bars[i]
            x1 = i * bar_w + 2
            y1 = 35 - h
            x2 = (i + 1) * bar_w - 2
            y2 = 35
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
                            self.log("[SYNC] Đã cập nhật lên GitHub")
            except Exception:
                pass

    def on_run_github(self):
        try:
            self.log("Đang khởi chạy từ GitHub...")
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py"
            cmd = f"curl -fsSL {url} | python"
            subprocess.Popen(cmd, shell=True)
            messagebox.showinfo("Thành công", "Đã khởi chạy từ GitHub!")
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")

    def on_run_assigned_macro(self):
        """Thực thi quét danh sách ảnh và thực hiện đúng lệnh đã gán cho từng ảnh"""
        rows = self.tree.get_children()
        if not rows:
            messagebox.showwarning("Cảnh báo", "Danh sách ảnh đang trống! Vui lòng thêm ảnh và gán lệnh.")
            return

        tasks = []
        for row in rows:
            item = self.tree.item(row)
            t_file, action = item['values']
            tasks.append((t_file, action))

        try:
            threshold_val = float(self.spin_thresh.get()) / 100.0
            total_loops = int(self.spin_loop.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số cho độ khớp và số vòng lặp!")
            return

        self.log(f"[MACRO] Bắt đầu chạy chuỗi {len(tasks)} nhiệm vụ | Ngưỡng: {int(threshold_val*100)}%")

        def vision_task():
            try:
                for current_loop in range(1, total_loops + 1):
                    if not self.is_running:
                        break
                    
                    self.log(f"[AUTO] --- Vòng lặp {current_loop}/{total_loops} ---")
                    screenshot_path = "/sdcard/screen.png"
                    
                    cmd_capture = f"{RISH_PATH} -c '/system/bin/screencap -p {screenshot_path}'"
                    subprocess.run(cmd_capture, shell=True)
                    
                    if not os.path.exists(screenshot_path):
                        self.log("[VISION ERROR] Không thể chụp màn hình qua Shizuku!")
                        break

                    screen = cv2.imread(screenshot_path)
                    found_any = False

                    for t_file, action in tasks:
                        if not os.path.exists(t_file):
                            self.log(f"[WARNING] Không tìm thấy file ảnh mẫu '{t_file}'")
                            continue

                        template = cv2.imread(t_file)
                        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                        if max_val >= threshold_val:
                            h, w, _ = template.shape
                            center_x = max_loc[0] + w // 2
                            center_y = max_loc[1] + h // 2
                            
                            self.log(f"[FOUND] '{t_file}' khớp {max_val*100:.1f}% -> Thực thi lệnh: [{action}] tại ({center_x}, {center_y})")
                            
                            # Thực thi lệnh tương ứng dựa vào cấu hình đã gán
                            if action == "Click Trái (Tap)":
                                cmd = f"{RISH_PATH} -c 'input tap {center_x} {center_y}'"
                            elif action == "Double Click":
                                cmd = f"{RISH_PATH} -c 'input tap {center_x} {center_y} && input tap {center_x} {center_y}'"
                            elif action == "Nhấn Giữ (Long Press)":
                                cmd = f"{RISH_PATH} -c 'input swipe {center_x} {center_y} {center_x} {center_y} 1000'"
                            elif action == "Vuốt Màn Hình (Swipe)":
                                cmd = f"{RISH_PATH} -c 'input swipe 500 1500 500 500 300'"
                            else:
                                cmd = f"{RISH_PATH} -c 'input tap {center_x} {center_y}'"

                            subprocess.run(cmd, shell=True)
                            found_any = True
                            break # Khớp và thực thi xong 1 tác vụ ưu tiên thì chuyển vòng

                    if not found_any:
                        self.log("[VISION] Không tìm thấy ảnh nào khớp trong bảng lệnh.")

                    time.sleep(1.0)

                self.log("[MACRO] Hoàn thành chuỗi kịch bản tự động!")
                self.root.after(0, lambda: messagebox.showinfo("Hoàn tất", "Đã chạy xong kịch bản tự động theo bảng lệnh!"))
                
            except Exception as e:
                self.log(f"[ERROR] {str(e)}")

        threading.Thread(target=vision_task, daemon=True).start()

    def on_delete(self):
        if messagebox.askyesno("Xác nhận", "Xóa file main.py trên GitHub?"):
            url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
            headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                sha = res.json().get("sha")
                requests.delete(url, headers=headers, json={"message": "Xóa qua GUI", "sha": sha})
                messagebox.showinfo("Thành công", "Đã xóa file trên GitHub!")

    def on_full_reset(self):
        if messagebox.askyesno("Xác nhận Reset", "Tải lại bản mới nhất từ GitHub và khởi động lại?"):
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py"
            os.system(f"curl -fsSL {url} -o main.py")
            self.is_running = False
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def on_reset_log(self):
        self.log_text.delete("1.0", tk.END)
        self.log("Đã làm mới bảng điều khiển.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoManagerApp(root)
    root.mainloop()
