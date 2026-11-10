import os
import sys
import threading
import json
import base64
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. Cấu hình biến môi trường hiển thị qua X11 cho Termux / Samsung DeX
os.environ["DISPLAY"] = ":0"

# --- CẤU HÌNH GITHUB ---
GITHUB_TOKEN = "ghp_" + "bV4gdc0mSQNLKh3" + "MMDhHuTxtLKI5lN3xsmSu"
GITHUB_REPO = "huyxaa00-eng/my_project"
GITHUB_BRANCH = "main"

# --- MÀU SẮC GIAO DIỆN CHUYÊN NGHIỆP ---
BG_COLOR = "#1e1e2e"          # Nền chính (Dark Modern)
PANEL_COLOR = "#2a2a3c"       # Nền phụ / Khung
TEXT_COLOR = "#cdd6f4"        # Màu chữ chính
ACCENT_GREEN = "#a6e3a1"      # Nút chạy / Thành công
ACCENT_BLUE = "#89b4fa"       # Nút danh sách / Thông tin
ACCENT_ORANGE = "#fab387"     # Nút soạn code
ACCENT_PURPLE = "#cba6f7"     # Nút tải file máy
ACCENT_CYAN = "#89dceb"       # Nút đồng bộ
ACCENT_RED = "#f38ba8"        # Nút xóa
BTN_TEXT = "#11111b"          # Chữ trên nút màu

# --- KHU VỰC XỬ LÝ TÁC VỤ / AUTO GAME ---
def xu_ly_auto_game():
    print("🎮 Đang chạy kịch bản auto game...")
    return "Auto game đã thực thi thành công!"

# --- HÀM LẤY DANH SÁCH FILE TRÊN GITHUB ---
def get_github_file_list():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/git/trees/{GITHUB_BRANCH}?recursive=1"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "Termux-Python"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                file_list = []
                for item in data.get("tree", []):
                    if item["type"] == "blob":
                        file_list.append(item["path"])
                return True, file_list
    except urllib.error.HTTPError as e:
        return False, f"Lỗi GitHub API: {e.read().decode('utf-8')}"
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"
    
    return False, "Không thể lấy danh sách file."

# --- HÀM TẢI / CẬP NHẬT FILE LÊN GITHUB ---
def upload_file_to_github(file_path_on_repo, python_code_content):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path_on_repo}"
    
    encoded_content = base64.b64encode(python_code_content.encode('utf-8')).decode('utf-8')
    
    sha = None
    try:
        req_check = urllib.request.Request(url, headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "Termux-Python"})
        with urllib.request.urlopen(req_check) as response:
            data = json.loads(response.read().decode('utf-8'))
            sha = data.get('sha')
    except Exception:
        pass

    payload = {
        "message": f"Sync/Update {file_path_on_repo} via Termux Professional System",
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Termux-Python"
    }, method="PUT")

    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201]:
                return True, f"Đồng bộ file {file_path_on_repo} thành công!"
    except urllib.error.HTTPError as e:
        error_message = e.read().decode('utf-8')
        return False, f"Lỗi GitHub API ({file_path_on_repo}): {error_message}"
    except Exception as e:
        return False, f"Lỗi kết nối ({file_path_on_repo}): {str(e)}"
    
    return False, "Không rõ lỗi."

# --- HÀM ĐỒNG BỘ TOÀN BỘ FILE .PY TỪ THƯ MỤC MÁY LÊN GITHUB ---
def sync_local_folder_to_github():
    synced_files = []
    errors = []
    
    for file_name in os.listdir('.'):
        if file_name.endswith('.py') and os.path.isfile(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                success, msg = upload_file_to_github(file_name, content)
                if success:
                    synced_files.append(file_name)
                else:
                    errors.append(f"{file_name}: {msg}")
            except Exception as e:
                errors.append(f"{file_name}: {str(e)}")
                
    return synced_files, errors

# --- HÀM XÓA FILE TRÊN GITHUB ---
def delete_file_from_github(file_path_on_repo):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path_on_repo}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "Termux-Python"
    }
    
    sha = None
    try:
        req_check = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req_check) as response:
            data = json.loads(response.read().decode('utf-8'))
            sha = data.get('sha')
    except Exception as e:
        return False, f"Không tìm thấy file trên GitHub: {str(e)}"

    if not sha:
        return False, "Không lấy được mã SHA của file."

    payload = {
        "message": f"Delete {file_path_on_repo} via Termux Professional System",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Termux-Python"
    }, method="DELETE")

    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 204]:
                return True, "Xóa file trên GitHub thành công!"
    except urllib.error.HTTPError as e:
        return False, f"Lỗi GitHub API: {e.read().decode('utf-8')}"
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"
    
    return False, "Không rõ lỗi khi xóa."

# --- HTTP SERVER NHẬN LỆNH NGẦM ---
class TaskHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        command = data.get("command", "none")
        print(f"📥 Nhận lệnh qua HTTP: {command}")
        
        result_msg = ""
        if command == "chay_auto_game":
            result_msg = xu_ly_auto_game()
        else:
            result_msg = f"Đã nhận lệnh: {command}"
            
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        
        response = {"status": "success", "message": result_msg}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def log_message(self, format, *args):
        return

def run_server(port=5000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, TaskHandler)
    print(f"🚀 Server HTTP đang chạy tại cổng {port}, sẵn sàng nhận lệnh!")
    httpd.serve_forever()

# --- GIAO DIỆN GUI CHUYÊN NGHIỆP (X11) ---
class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Termux Auto & GitHub Control Center")
        self.root.geometry("480x620")
        self.root.config(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.create_dashboard_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_dashboard_screen(self):
        self.clear_window()
        
        lbl_title = tk.Label(self.root, text="⚡ AUTO & GITHUB CONTROL CENTER", font=("Segoe UI", 13, "bold"), bg=BG_COLOR, fg=ACCENT_BLUE)
        lbl_title.pack(pady=(12, 5))
        
        self.status_frame = tk.Frame(self.root, bg=PANEL_COLOR, bd=1, relief="solid")
        self.status_frame.pack(fill="x", padx=20, pady=5)
        
        self.status_label = tk.Label(self.status_frame, text="Trạng thái: Sẵn sàng hoạt động", font=("Segoe UI", 9), bg=PANEL_COLOR, fg=ACCENT_GREEN)
        self.status_label.pack(pady=6, padx=10)
        
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(pady=5)

        btn_run = tk.Button(btn_frame, text="▶  Chạy Kịch Bản Auto Ngay", font=("Segoe UI", 10, "bold"), bg=ACCENT_GREEN, fg=BTN_TEXT, width=32, height=2, bd=0, relief="flat", cursor="hand2", command=self.on_click_run)
        btn_run.pack(pady=4)

        btn_sync = tk.Button(btn_frame, text="🔄  Đồng Bộ Tất Cả File Từ Máy Lên GitHub", font=("Segoe UI", 10, "bold"), bg=ACCENT_CYAN, fg=BTN_TEXT, width=32, height=2, bd=0, relief="flat", cursor="hand2", command=self.on_click_sync)
        btn_sync.pack(pady=4)

        btn_goto_upload = tk.Button(btn_frame, text="✍️  Soạn & Tải Code Lên GitHub", font=("Segoe UI", 10, "bold"), bg=ACCENT_ORANGE, fg=BTN_TEXT, width=32, height=2, bd=0, relief="flat", cursor="hand2", command=self.create_upload_screen)
        btn_goto_upload.pack(pady=4)

        btn_upload_local = tk.Button(btn_frame, text="📁  Tải Lẻ File Từ Máy Lên GitHub", font=("Segoe UI", 10, "bold"), bg=ACCENT_PURPLE, fg=BTN_TEXT, width=32, height=2, bd=0, relief="flat", cursor="hand2", command=self.create_upload_local_screen)
        btn_upload_local.pack(pady=4)

        btn_list_files = tk.Button(btn_frame, text="📋  Xem Danh Sách File Repository", font=("Segoe UI", 10, "bold"), bg=ACCENT_BLUE, fg=BTN_TEXT, width=32, height=2, bd=0, relief="flat", cursor="hand2", command=self.show_file_list_screen)
        btn_list_files.pack(pady=4)

        btn_delete = tk.Button(btn_frame, text="🗑️  Xóa File Trên GitHub (Chọn Danh Sách)", font=("Segoe UI", 10, "bold"), bg=ACCENT_RED, fg=BTN_TEXT, width=32, height=2, bd=0, relief="flat", cursor="hand2", command=self.create_delete_screen)
        btn_delete.pack(pady=4)

        lbl_footer = tk.Label(self.root, text="Environment: Termux X11 • Repository: huyxaa00-eng/my_project", font=("Segoe UI", 8), bg=BG_COLOR, fg="#6c7086")
        lbl_footer.pack(side="bottom", pady=8)

    def on_click_run(self):
        msg = xu_ly_auto_game()
        self.status_label.config(text=f"Trạng thái: {msg}")
        messagebox.showinfo("Thông báo", msg)

    def on_click_sync(self):
        if not messagebox.askyesno("Xác nhận đồng bộ", "Bạn có muốn đẩy toàn bộ các file .py trong thư mục máy lên GitHub để đồng bộ giống hoàn toàn không?"):
            return

        def background_sync():
            self.status_label.config(text="Trạng thái: Đang đồng bộ file...")
            synced, errs = sync_local_folder_to_github()
            
            summary = f"Đã đồng bộ thành công {len(synced)} file."
            if errs:
                summary += f" Lỗi {len(errs)} file."
                
            self.status_label.config(text=f"Trạng thái: {summary}")
            messagebox.showinfo("Kết quả đồng bộ", f"Thành công ({len(synced)}):\n" + "\n".join(synced) + (f"\n\nLỗi:\n" + "\n".join(errs) if errs else ""))

        threading.Thread(target=background_sync).start()
        messagebox.showinfo("Đang xử lý", "Tiến trình đồng bộ đang chạy ngầm, vui lòng đợi thông báo hoàn tất!")

    # --- MÀN HÌNH TẢI FILE TỪ MÁY ---
    def create_upload_local_screen(self):
        self.clear_window()

        lbl_title = tk.Label(self.root, text="📁 Tải Lẻ File Từ Máy Lên GitHub", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=ACCENT_PURPLE)
        lbl_title.pack(pady=(15, 10))

        tk.Label(self.root, text="Đường dẫn file trên thiết bị:", font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=25)
        
        self.local_path_var = tk.StringVar()
        entry_path = tk.Entry(self.root, textvariable=self.local_path_var, font=("Segoe UI", 9), bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white", width=38, relief="solid", bd=1)
        entry_path.pack(pady=5)

        btn_browse = tk.Button(self.root, text="Duyệt Chọn File...", font=("Segoe UI", 9, "bold"), bg="#45475a", fg=TEXT_COLOR, width=20, bd=0, command=self.browse_local_file)
        btn_browse.pack(pady=5)

        tk.Label(self.root, text="Tên file khi lưu trên GitHub (vd: script.py):", font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=25, pady=(10,0))
        self.repo_filename_entry = tk.Entry(self.root, font=("Segoe UI", 10), bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white", width=38, relief="solid", bd=1)
        self.repo_filename_entry.pack(pady=5)

        frame_btn = tk.Frame(self.root, bg=BG_COLOR)
        frame_btn.pack(pady=20)

        btn_upload = tk.Button(frame_btn, text="Xác Nhận Tải Lên", font=("Segoe UI", 9, "bold"), bg=ACCENT_GREEN, fg=BTN_TEXT, width=15, height=2, bd=0, command=self.handle_upload_local)
        btn_upload.pack(side=tk.LEFT, padx=10)

        btn_back = tk.Button(frame_btn, text="Quay Lại", font=("Segoe UI", 9), bg="#45475a", fg=TEXT_COLOR, width=15, height=2, bd=0, command=self.create_dashboard_screen)
        btn_back.pack(side=tk.LEFT, padx=10)

    def browse_local_file(self):
        filename = filedialog.askopenfilename(title="Chọn file script")
        if filename:
            self.local_path_var.set(filename)
            base_name = os.path.basename(filename)
            self.repo_filename_entry.delete(0, tk.END)
            self.repo_filename_entry.insert(0, base_name)

    def handle_upload_local(self):
        local_path = self.local_path_var.get().strip()
        repo_filename = self.repo_filename_entry.get().strip()

        if not local_path or not os.path.exists(local_path):
            messagebox.showerror("Lỗi", "Vui lòng chọn một file hợp lệ từ máy!")
            return
        if not repo_filename:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên file trên GitHub!")
            return

        try:
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Lỗi đọc file", f"Không thể đọc file: {str(e)}")
            return

        def background_upload():
            success, msg = upload_file_to_github(repo_filename, content)
            if success:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Thất bại", msg)

        threading.Thread(target=background_upload).start()
        messagebox.showinfo("Đang xử lý", "Đang gửi file lên GitHub, vui lòng đợi giây lát...")

    # --- MÀN HÌNH XÓA FILE TRÊN GITHUB (HIỂN THỊ DANH SÁCH ĐỂ CHỌN) ---
    def create_delete_screen(self):
        self.clear_window()

        lbl_title = tk.Label(self.root, text="🗑️ Chọn File Trên GitHub Để Xóa", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=ACCENT_RED)
        lbl_title.pack(pady=(12, 5))

        tk.Label(self.root, text="Bấm chọn file cần xóa trong danh sách dưới đây:", font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=20)

        # Hộp danh sách (Listbox) hiển thị file
        frame_list = tk.Frame(self.root, bg=BG_COLOR)
        frame_list.pack(pady=5)

        self.file_listbox = tk.Listbox(frame_list, width=52, height=12, font=("Courier", 9), bg=PANEL_COLOR, fg=TEXT_COLOR, selectbackground=ACCENT_RED, selectforeground=BTN_TEXT, relief="solid", bd=1)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Tải danh sách file ngầm
        def load_files_to_listbox():
            success, result = get_github_file_list()
            self.file_listbox.delete(0, tk.END)
            if success and result:
                for f in result:
                    self.file_listbox.insert(tk.END, f)
            else:
                self.file_listbox.insert(tk.END, "Không thể tải danh sách hoặc repo trống!")

        threading.Thread(target=load_files_to_listbox).start()

        frame_btn = tk.Frame(self.root, bg=BG_COLOR)
        frame_btn.pack(pady=10)

        btn_del = tk.Button(frame_btn, text="Xác Nhận Xóa File Đã Chọn", font=("Segoe UI", 9, "bold"), bg=ACCENT_RED, fg=BTN_TEXT, width=22, height=2, bd=0, command=self.handle_delete_selected)
        btn_del.pack(side=tk.LEFT, padx=5)

        btn_back = tk.Button(frame_btn, text="Quay Lại", font=("Segoe UI", 9), bg="#45475a", fg=TEXT_COLOR, width=15, height=2, bd=0, command=self.create_dashboard_screen)
        btn_back.pack(side=tk.LEFT, padx=5)

    def handle_delete_selected(self):
        try:
            selected_indices = self.file_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Lỗi", "Vui lòng chọn một file trong danh sách để xóa!")
                return
            
            filename = self.file_listbox.get(selected_indices[0])
            if "Không thể tải" in filename:
                return

            if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa vĩnh viễn file '{filename}' trên GitHub không?"):
                return

            def background_delete():
                success, msg = delete_file_from_github(filename)
                if success:
                    messagebox.showinfo("Thành công", msg)
                    self.create_delete_screen() # Load lại danh sách sau khi xóa
                else:
                    messagebox.showerror("Thất bại", msg)

            threading.Thread(target=background_delete).start()
            messagebox.showinfo("Đang xử lý", f"Đang gửi yêu cầu xóa file '{filename}'...")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    # --- MÀN HÌNH HIỂN THỊ DANH SÁCH FILE TRÊN GITHUB ---
    def show_file_list_screen(self):
        self.clear_window()

        lbl_title = tk.Label(self.root, text="📋 Danh Sách File Trên GitHub", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=ACCENT_BLUE)
        lbl_title.pack(pady=(15, 10))

        self.list_text = scrolledtext.ScrolledText(self.root, width=52, height=15, font=("Courier", 9), bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white")
        self.list_text.pack(pady=5)
        self.list_text.insert(tk.END, "⏳ Đang tải danh sách file từ GitHub, vui lòng đợi...")
        self.list_text.config(state=tk.DISABLED)

        btn_back = tk.Button(self.root, text="Quay Lại Dashboard", font=("Segoe UI", 9, "bold"), bg="#45475a", fg=TEXT_COLOR, width=25, height=2, bd=0, command=self.create_dashboard_screen)
        btn_back.pack(pady=10)

        def fetch_list():
            success, result = get_github_file_list()
            self.list_text.config(state=tk.NORMAL)
            self.list_text.delete("1.0", tk.END)
            if success:
                if result:
                    self.list_text.insert(tk.END, f"Tổng số file: {len(result)}\n" + "="*45 + "\n")
                    for f in result:
                        self.list_text.insert(tk.END, f"📂  {f}\n")
                else:
                    self.list_text.insert(tk.END, "Repository đang trống.")
            else:
                self.list_text.insert(tk.END, f"❌ Lỗi: {result}")
            self.list_text.config(state=tk.DISABLED)

        threading.Thread(target=fetch_list).start()

    # --- MÀN HÌNH TẢI FILE LÊN BẰNG CÁCH SOẠN THẢO TRỰC TIẾP ---
    def create_upload_screen(self):
        self.clear_window()

        lbl_title = tk.Label(self.root, text="✍️ Soạn & Tải Code Lên GitHub", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=ACCENT_ORANGE)
        lbl_title.pack(pady=(10, 5))

        tk.Label(self.root, text="Tên file trên GitHub (vd: script.py):", font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=20)
        self.filename_entry = tk.Entry(self.root, font=("Segoe UI", 10), bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white", width=42, relief="solid", bd=1)
        self.filename_entry.pack(pady=3)
        self.filename_entry.insert(0, "new_script.py")

        tk.Label(self.root, text="Nội dung mã nguồn Python:", font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=20)
        
        self.code_text = scrolledtext.ScrolledText(self.root, width=52, height=10, font=("Courier", 9), bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground="white")
        self.code_text.pack(pady=5)
        self.code_text.insert(tk.END, "# Viết code của bạn ở đây\nprint('Hello from Termux Professional System!')")

        frame_btn = tk.Frame(self.root, bg=BG_COLOR)
        frame_btn.pack(pady=8)

        btn_upload = tk.Button(frame_btn, text="Xác Nhận Tải Lên", font=("Segoe UI", 9, "bold"), bg=ACCENT_GREEN, fg=BTN_TEXT, width=16, height=2, bd=0, command=self.handle_upload)
        btn_upload.pack(side=tk.LEFT, padx=10)

        btn_back = tk.Button(frame_btn, text="Quay Lại", font=("Segoe UI", 9), bg="#45475a", fg=TEXT_COLOR, width=15, height=2, bd=0, command=self.create_dashboard_screen)
        btn_back.pack(side=tk.LEFT, padx=10)

    def handle_upload(self):
        filename = self.filename_entry.get().strip()
        code_content = self.code_text.get("1.0", tk.END).strip()

        if not filename.endswith(".py"):
            filename += ".py"

        if not filename or not code_content:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên file và nội dung code!")
            return

        def background_upload():
            success, msg = upload_file_to_github(filename, code_content)
            if success:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Thất bại", msg)

        threading.Thread(target=background_upload).start()
        messagebox.showinfo("Đang xử lý", "Đang gửi yêu cầu lên GitHub, vui lòng đợi giây lát...")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, args=(5000,))
    server_thread.daemon = True
    server_thread.start()

    print("🖥️ Đang khởi động giao diện X11 chuyên nghiệp...")
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
