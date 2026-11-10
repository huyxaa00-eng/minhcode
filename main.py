import os
import requests
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess

# Cấu hình GitHub của bạn
GITHUB_TOKEN = "THAY_TOKEN_CUA_BAN_VÀO_ĐÂY"
REPO_OWNER = "huyxaa00-eng"
REPO_NAME = "my_project"

def upload_file_to_github(file_name, content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
        
    import base64
    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": f"Cập nhật {file_name} tự động qua GUI",
        "content": content_encoded
    }
    if sha:
        data["sha"] = sha
        
    put_response = requests.put(url, headers=headers, json=data)
    return (True, "Thành công") if put_response.status_code in [200, 201] else (False, put_response.json().get("message", "Lỗi"))

def sync_local_folder_to_github():
    file_name = "main.py"
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                content = f.read()
            success, msg = upload_file_to_github(file_name, content)
            return ([file_name], []) if success else ([], [f"{file_name}: {msg}"])
        except Exception as e:
            return ([], [f"{file_name}: {str(e)}"])
    return ([], ["main.py: Không tìm thấy file trên máy"])

def delete_github_file(file_name):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha")
        data = {"message": f"Xóa {file_name} qua giao diện", "sha": sha}
        del_response = requests.delete(url, headers=headers, json=data)
        if del_response.status_code == 200:
            return True, "Đã xóa thành công"
        return False, del_response.json().get("message", "Lỗi")
    return False, "Không tìm thấy file trên GitHub"

class AutoManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Bảng Điều Khiển Auto & GitHub - X11")
        self.root.geometry("450x450")
        self.root.configure(bg="#1e1e1e")
        
        style = ttk.Style()
        style.theme_use("clam")
        
        title_label = tk.Label(root, text="QUẢN LÝ AUTO & GITHUB", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="#00ffcc")
        title_label.pack(pady=15)
        
        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack(pady=5, fill=tk.X, padx=30)
        
        tk.Button(btn_frame, text="🔄 Đồng bộ main.py lên GitHub", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.on_sync).pack(pady=6, fill=tk.X)
        tk.Button(btn_frame, text="▶️ Chạy trực tiếp từ GitHub", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.on_run_github).pack(pady=6, fill=tk.X)
        tk.Button(btn_frame, text="🗑️ Xóa main.py trên GitHub", bg="#f44336", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.on_delete).pack(pady=6, fill=tk.X)
        tk.Button(btn_frame, text="⏹️ Dừng/Làm mới trạng thái", bg="#ff9800", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.on_reset).pack(pady=6, fill=tk.X)
        
        log_frame = tk.Frame(root, bg="#1e1e1e")
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=30)
        
        tk.Label(log_frame, text="Trạng thái hệ thống:", font=("Arial", 9), bg="#1e1e1e", fg="#aaaaaa", anchor="w").pack(fill=tk.X)
        
        self.log_text = tk.Text(log_frame, height=5, bg="#2d2d2d", fg="#00ff00", font=("Consolas", 9), relief="flat")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.insert(tk.END, "Sẵn sàng hoạt động...\n")
        
        tk.Button(root, text="Thoát ứng dụng", bg="#555555", fg="white", font=("Arial", 10), relief="flat", command=root.quit).pack(pady=10, fill=tk.X, padx=30)

    def log(self, message):
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)

    def on_sync(self):
        self.log("Đang đồng bộ main.py lên GitHub...")
        synced, errors = sync_local_folder_to_github()
        if synced:
            self.log("Đồng bộ thành công!")
            messagebox.showinfo("Thành công", f"Đã đồng bộ thành công: {', '.join(synced)}")
        else:
            self.log(f"Lỗi đồng bộ: {errors}")
            messagebox.showerror("Lỗi", f"Đồng bộ thất bại:\n{'\n'.join(errors)}")

    def on_run_github(self):
        try:
            self.log("Đang kích hoạt chạy từ GitHub...")
            # Sửa lại cú pháp an toàn không bị lỗi chuỗi
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/main.py"
            cmd = f"curl -fsSL {url} | python"
            subprocess.Popen(cmd, shell=True)
            self.log("Đã gửi lệnh chạy ngầm thành công!")
            messagebox.showinfo("Thành công", "Đã khởi chạy kịch bản từ GitHub!")
        except Exception as e:
            self.log(f"Lỗi chạy file: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể chạy file: {str(e)}")

    def on_delete(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa file main.py trên GitHub không?"):
            self.log("Đang gửi yêu cầu xóa file trên GitHub...")
            success, msg = delete_github_file("main.py")
            if success:
                self.log("Đã xóa file thành công trên GitHub.")
                messagebox.showinfo("Thành công", msg)
            else:
                self.log(f"Xóa thất bại: {msg}")
                messagebox.showerror("Lỗi", msg)

    def on_reset(self):
        self.log_text.delete("1.0", tk.END)
        self.log("Đã làm mới bảng điều khiển.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoManagerApp(root)
    root.mainloop()
