import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import urllib.request
import json
import urllib.parse
from datetime import datetime, timedelta
import base64

# --- TỰ ĐỘNG KIỂM TRA & TẢI THƯ VIỆN ---
def auto_install(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"⚠️ Đang tải thư viện '{package_name}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package_name])

REQUIRED_PACKAGES = [
    ("requests", "requests"),
    ("Pillow", "PIL"),
]

for pkg, imp in REQUIRED_PACKAGES:
    try:
        auto_install(pkg, imp)
    except Exception as e:
        print(f"Lỗi cài {pkg}: {e}")

SUPABASE_URL = "https://dvbhaxymloazsqvnwefd.supabase.co"
SUPABASE_KEY = "sb_publishable_hWWTO_k0YxAsq3jjw9LCtg_V2S03ORC"
ADMIN_EMAIL = "admin@gmail.com"
DEFAULT_TRIAL_HOURS = 0
DEFAULT_TRIAL_DAYS = 3
GITHUB_REPO = "huyxaa00-eng/my_project"
GITHUB_TOKEN = "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"

def supabase_request(endpoint, method="GET", data=None, query_params=""):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}{query_params}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body) if res_body else []
    except urllib.error.HTTPError as e:
        raise Exception(e.read().decode("utf-8"))
    except Exception as e:
        raise Exception(str(e))

root = tk.Tk()
root.title("Hệ Thống Quản Trị Supabase Cloud")
root.geometry("440x860")
root.configure(bg="#667EEA")

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def show_admin_dashboard(admin_email):
    clear_window()
    
    top_bar = tk.Frame(root, bg="#667EEA")
    top_bar.pack(padx=15, fill="x", pady=(8, 0))
    tk.Button(top_bar, text="🚪 Đăng Xuất", command=show_login, font=("Arial", 8, "bold"), fg="white", bg="#DC3545", bd=0, cursor="hand2").pack(side="right", ipadx=6, ipady=2)
    tk.Label(top_bar, text="🛡️ QUẢN TRỊ VIÊN HỆ THỐNG", font=("Arial", 12, "bold"), fg="white", bg="#667EEA").pack(side="left")

    # Tạo vùng chứa có thanh cuộn (Scrollable Canvas) cho Admin Dashboard
    container = tk.Frame(root, bg="#667EEA")
    container.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(container, bg="#667EEA", highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#667EEA")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 1. Cài đặt dùng thử
    config_frame = tk.LabelFrame(scrollable_frame, text="⚙️ Cài đặt dùng thử cho tài khoản mới", font=("Arial", 9, "bold"), fg="white", bg="#667EEA", bd=1, relief="solid")
    config_frame.pack(fill="x", pady=(0, 5), ipadx=5, ipady=5)

    cfg_sub = tk.Frame(config_frame, bg="#667EEA")
    cfg_sub.pack(fill="x", padx=5)

    tk.Label(cfg_sub, text="Giờ:", fg="white", bg="#667EEA", font=("Arial", 9)).pack(side="left")
    hours_entry = tk.Entry(cfg_sub, font=("Arial", 10), width=4, bg="#FFFFFF", bd=0, relief="solid")
    hours_entry.insert(0, str(DEFAULT_TRIAL_HOURS))
    hours_entry.pack(side="left", padx=(2, 8))

    tk.Label(cfg_sub, text="Ngày:", fg="white", bg="#667EEA", font=("Arial", 9)).pack(side="left")
    days_entry = tk.Entry(cfg_sub, font=("Arial", 10), width=4, bg="#FFFFFF", bd=0, relief="solid")
    days_entry.insert(0, str(DEFAULT_TRIAL_DAYS))
    days_entry.pack(side="left", padx=(2, 8))

    def save_trial_config():
        global DEFAULT_TRIAL_HOURS, DEFAULT_TRIAL_DAYS
        try:
            DEFAULT_TRIAL_HOURS = int(hours_entry.get().strip() or 0)
            DEFAULT_TRIAL_DAYS = int(days_entry.get().strip() or 0)
            messagebox.showinfo("Thành công", f"Đã lưu:\n- Giờ: {DEFAULT_TRIAL_HOURS}\n- Ngày: {DEFAULT_TRIAL_DAYS}")
        except ValueError:
            messagebox.showerror("Lỗi", "Phải là số nguyên!")

    tk.Button(cfg_sub, text="Lưu", command=save_trial_config, font=("Arial", 9, "bold"), fg="white", bg="#E67E22", bd=0, cursor="hand2").pack(side="right", ipadx=6, ipady=2)

    # 2. Danh sách thành viên
    frame_list = tk.Frame(scrollable_frame, bg="white", bd=1, relief="solid")
    frame_list.pack(fill="x", pady=(0, 5))

    tk.Label(frame_list, text="📋 Danh Sách Thành Viên", font=("Arial", 9, "bold"), bg="white", fg="#333").pack(pady=3)

    listbox_frame = tk.Frame(frame_list, bg="white")
    listbox_frame.pack(fill="x", padx=5, pady=(0, 5))

    user_scrollbar = tk.Scrollbar(listbox_frame)
    user_scrollbar.pack(side="right", fill="y")

    user_listbox = tk.Listbox(listbox_frame, yscrollcommand=user_scrollbar.set, font=("Courier", 9), bg="#F8F9FA", bd=1, relief="solid", height=5)
    user_listbox.pack(side="left", fill="both", expand=True)
    user_scrollbar.config(command=user_listbox.yview)

    users_cache = []

    def load_users():
        nonlocal users_cache
        user_listbox.delete(0, tk.END)
        try:
            users_cache = supabase_request("users", method="GET", query_params="?select=email,balance,expiry_date")
            for u in users_cache:
                email = u.get('email', '')
                balance = u.get('balance') or 0
                expiry = u.get('expiry_date') or 'Chưa có'
                
                days_left = "Vĩnh viễn"
                if expiry != 'Chưa có':
                    try:
                        exp_date = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S" if len(expiry) > 10 else "%Y-%m-%d")
                        delta = (exp_date - datetime.now()).total_seconds() / 86400
                        if delta >= 0:
                            days_left = f"{int(delta)}n" if delta >= 1 else f"{int(delta*24)}h"
                        else:
                            days_left = "Hết hạn"
                    except:
                        pass

                display_text = f"{email:<20} | {balance:>5}đ | {days_left}"
                user_listbox.insert(tk.END, display_text)
        except Exception as e:
            pass

    load_users()

    # 3. Thao tác tài khoản
    action_frame = tk.Frame(scrollable_frame, bg="#667EEA")
    action_frame.pack(fill="x", pady=(0, 5))

    tk.Label(action_frame, text="Email được chọn:", fg="white", bg="#667EEA", font=("Arial", 9, "bold")).pack(anchor="w")
    email_action_entry = tk.Entry(action_frame, font=("Arial", 10), bg="#FFFFFF", bd=0, relief="solid")
    email_action_entry.pack(fill="x", ipady=2, pady=(0, 3))

    val_frame = tk.Frame(action_frame, bg="#667EEA")
    val_frame.pack(fill="x", pady=(0, 3))

    f1 = tk.Frame(val_frame, bg="#667EEA")
    f1.pack(side="left", expand=True, fill="x", padx=(0, 4))
    tk.Label(f1, text="Cộng Tiền (VNĐ):", fg="white", bg="#667EEA", font=("Arial", 8)).pack(anchor="w")
    money_entry = tk.Entry(f1, font=("Arial", 10), bg="#FFFFFF", bd=0, relief="solid")
    money_entry.pack(fill="x", ipady=2)

    f2 = tk.Frame(val_frame, bg="#667EEA")
    f2.pack(side="left", expand=True, fill="x")
    tk.Label(f2, text="Cộng Số Ngày:", fg="white", bg="#667EEA", font=("Arial", 8)).pack(anchor="w")
    days_entry_act = tk.Entry(f2, font=("Arial", 10), bg="#FFFFFF", bd=0, relief="solid")
    days_entry_act.pack(fill="x", ipady=2)

    def on_select_user(event):
        selected_indices = user_listbox.curselection()
        if selected_indices:
            idx = selected_indices[0]
            if idx < len(users_cache):
                selected_email = users_cache[idx].get('email', '')
                email_action_entry.delete(0, tk.END)
                email_action_entry.insert(0, selected_email)

    user_listbox.bind('<<ListboxSelect>>', on_select_user)

    def handle_add_money_and_days():
        email = email_action_entry.get().strip()
        if not email:
            messagebox.showerror("Lỗi", "Chưa chọn tài khoản!")
            return
        money_str = money_entry.get().strip()
        days_str = days_entry_act.get().strip()
        try:
            current_user = supabase_request("users", method="GET", query_params=f"?email=eq.{urllib.parse.quote(email)}&select=balance,expiry_date")
            if not current_user:
                messagebox.showerror("Lỗi", "Không tìm thấy!")
                return
            old_balance = current_user[0].get('balance') or 0
            old_expiry = current_user[0].get('expiry_date')
            update_data = {}
            if money_str:
                update_data["balance"] = old_balance + int(money_str)
            if days_str:
                base_date = datetime.now()
                if old_expiry:
                    try:
                        parsed_old = datetime.strptime(old_expiry, "%Y-%m-%d %H:%M:%S" if len(old_expiry) > 10 else "%Y-%m-%d")
                        if parsed_old > base_date:
                            base_date = parsed_old
                    except:
                        pass
                new_expiry_date = base_date + timedelta(days=int(days_str))
                update_data["expiry_date"] = new_expiry_date.strftime("%Y-%m-%d %H:%M:%S")

            if not update_data:
                messagebox.showerror("Lỗi", "Nhập số tiền hoặc ngày!")
                return
            supabase_request("users", method="PATCH", data=update_data, query_params=f"?email=eq.{urllib.parse.quote(email)}")
            messagebox.showinfo("Thành công", f"Đã cập nhật cho {email}")
            money_entry.delete(0, tk.END)
            days_entry_act.delete(0, tk.END)
            load_users()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def handle_reset_password():
        email = email_action_entry.get().strip()
        new_pass = money_entry.get().strip()
        if not email or not new_pass:
            messagebox.showerror("Lỗi", "Nhập email và pass mới vào ô 'Cộng Tiền'!")
            return
        try:
            supabase_request("users", method="PATCH", data={"password": new_pass}, query_params=f"?email=eq.{urllib.parse.quote(email)}")
            messagebox.showinfo("Thành công", f"Đã đổi pass cho {email}")
            load_users()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    btn_grid = tk.Frame(action_frame, bg="#667EEA")
    btn_grid.pack(fill="x", pady=3)
    tk.Button(btn_grid, text="💰 Cộng Tiền / Ngày", command=handle_add_money_and_days, font=("Arial", 9, "bold"), fg="white", bg="#28A745", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=4, padx=1)
    tk.Button(btn_grid, text="🔑 Đổi Pass", command=handle_reset_password, font=("Arial", 9, "bold"), fg="white", bg="#FFC107", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=4, padx=1)

    # 4. Quản lý File Server (GitHub)
    file_mgmt_frame = tk.LabelFrame(scrollable_frame, text="📂 File Python Trên Server", font=("Arial", 9, "bold"), fg="white", bg="#667EEA", bd=1, relief="solid")
    file_mgmt_frame.pack(fill="x", pady=(0, 5), ipadx=5, ipady=5)

    file_listbox_frame = tk.Frame(file_mgmt_frame, bg="#667EEA")
    file_listbox_frame.pack(fill="x", padx=3, pady=3)

    file_scrollbar = tk.Scrollbar(file_listbox_frame)
    file_scrollbar.pack(side="right", fill="y")

    python_files_listbox = tk.Listbox(file_listbox_frame, yscrollcommand=file_scrollbar.set, font=("Courier", 9), bg="#F8F9FA", bd=1, relief="solid", height=4)
    python_files_listbox.pack(side="left", fill="both", expand=True)
    file_scrollbar.config(command=python_files_listbox.yview)

    def load_server_python_files():
        python_files_listbox.delete(0, tk.END)
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
            req = urllib.request.Request(url, headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "AdminApp"})
            with urllib.request.urlopen(req) as response:
                contents = json.loads(response.read().decode("utf-8"))
                for item in contents:
                    if item['type'] == 'file' and item['name'].endswith('.py'):
                        python_files_listbox.insert(tk.END, item['name'])
        except:
            pass

    load_server_python_files()

    def handle_upload_file():
        file_path = filedialog.askopenfilename(title="Chọn file Python", filetypes=[("Python Files", "*.py")])
        if not file_path:
            return
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
            
            check_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
            sha = None
            try:
                req_check = urllib.request.Request(check_url, headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "AdminApp"})
                with urllib.request.urlopen(req_check) as res:
                    sha = json.loads(res.read().decode("utf-8")).get("sha")
            except:
                pass

            data = {"message": f"Upload {file_name}", "content": encoded_content}
            if sha:
                data["sha"] = sha

            req_data = json.dumps(data).encode("utf-8")
            put_req = urllib.request.Request(check_url, data=req_data, headers={"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json", "User-Agent": "AdminApp"}, method="PUT")
            with urllib.request.urlopen(put_req):
                messagebox.showinfo("Thành công", f"Đã tải {file_name} lên GitHub!")
                load_server_python_files()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def handle_delete_file():
        selected_indices = python_files_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Lỗi", "Chọn file cần xóa!")
            return
        file_name = python_files_listbox.get(selected_indices[0])
        if messagebox.askyesno("Xác nhận", f"Xóa file {file_name}?"):
            try:
                check_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
                req_check = urllib.request.Request(check_url, headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "AdminApp"})
                with urllib.request.urlopen(req_check) as res:
                    sha = json.loads(res.read().decode("utf-8")).get("sha")

                data = {"message": f"Delete {file_name}", "sha": sha}
                req_data = json.dumps(data).encode("utf-8")
                del_req = urllib.request.Request(check_url, data=req_data, headers={"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json", "User-Agent": "AdminApp"}, method="DELETE")
                with urllib.request.urlopen(del_req):
                    messagebox.showinfo("Thành công", f"Đã xóa {file_name}!")
                    load_server_python_files()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    file_btn_frame = tk.Frame(file_mgmt_frame, bg="#667EEA")
    file_btn_frame.pack(fill="x", padx=3, pady=2)
    tk.Button(file_btn_frame, text="📤 Tải File Lên", command=handle_upload_file, font=("Arial", 8, "bold"), fg="white", bg="#28A745", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=3, padx=1)
    tk.Button(file_btn_frame, text="🗑️ Xóa File", command=handle_delete_file, font=("Arial", 8, "bold"), fg="white", bg="#DC3545", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=3, padx=1)

    # 5. Khung Dán Code Sửa File main.py Trên Máy
    code_edit_frame = tk.LabelFrame(scrollable_frame, text="📝 Dán Code Sửa main.py Trên Máy", font=("Arial", 9, "bold"), fg="white", bg="#667EEA", bd=1, relief="solid")
    code_edit_frame.pack(fill="x", pady=(0, 5), ipadx=5, ipady=5)

    code_text_box = tk.Text(code_edit_frame, font=("Courier", 8), bg="#1E1E1E", fg="#D4D4D4", insertbackground="white", height=5, bd=0)
    code_text_box.pack(fill="x", padx=3, pady=3)

    def handle_save_and_sync_code():
        new_code = code_text_box.get("1.0", tk.END).strip()
        if not new_code:
            messagebox.showerror("Lỗi", "Chưa nhập code!")
            return
        if not messagebox.askyesno("Xác nhận", "Lưu ghi đè main.py trên máy, đẩy lên GitHub và khởi động lại?"):
            return
        try:
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(new_code)
            encoded_content = base64.b64encode(new_code.encode("utf-8")).decode("utf-8")
            check_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/main.py"
            sha = None
            try:
                req_check = urllib.request.Request(check_url, headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "AdminApp"})
                with urllib.request.urlopen(req_check) as res:
                    sha = json.loads(res.read().decode("utf-8")).get("sha")
            except:
                pass
            data = {"message": "Update main.py via app", "content": encoded_content}
            if sha:
                data["sha"] = sha
            req_data = json.dumps(data).encode("utf-8")
            put_req = urllib.request.Request(check_url, data=req_data, headers={"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json", "User-Agent": "AdminApp"}, method="PUT")
            with urllib.request.urlopen(put_req):
                pass
            root.destroy()
            subprocess.run([sys.executable, "-c", "import os, sys; os.execv(sys.executable, [sys.executable, 'main.py'])"])
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    tk.Button(code_edit_frame, text="💾 Lưu main.py & Đồng Bộ & Khởi Động Lại", command=handle_save_and_sync_code, font=("Arial", 8, "bold"), fg="white", bg="#6f42c1", bd=0, cursor="hand2").pack(fill="x", padx=3, ipady=4)

    # 6. Khung Dán Code Sửa File Trangchu.py Trên Máy
    trangchu_edit_frame = tk.LabelFrame(scrollable_frame, text="📝 Dán Code Sửa Trangchu.py Trên Máy", font=("Arial", 9, "bold"), fg="white", bg="#667EEA", bd=1, relief="solid")
    trangchu_edit_frame.pack(fill="x", pady=(0, 5), ipadx=5, ipady=5)

    trangchu_text_box = tk.Text(trangchu_edit_frame, font=("Courier", 8), bg="#1E1E1E", fg="#D4D4D4", insertbackground="white", height=5, bd=0)
    trangchu_text_box.pack(fill="x", padx=3, pady=3)

    def handle_save_and_sync_trangchu():
        new_code = trangchu_text_box.get("1.0", tk.END).strip()
        if not new_code:
            messagebox.showerror("Lỗi", "Chưa nhập code!")
            return
        if not messagebox.askyesno("Xác nhận", "Lưu ghi đè Trangchu.py trên máy và đẩy lên GitHub?"):
            return
        try:
            with open("Trangchu.py", "w", encoding="utf-8") as f:
                f.write(new_code)
            encoded_content = base64.b64encode(new_code.encode("utf-8")).decode("utf-8")
            check_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/Trangchu.py"
            sha = None
            try:
                req_check = urllib.request.Request(check_url, headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "AdminApp"})
                with urllib.request.urlopen(req_check) as res:
                    sha = json.loads(res.read().decode("utf-8")).get("sha")
            except:
                pass
            data = {"message": "Update Trangchu.py via app", "content": encoded_content}
            if sha:
                data["sha"] = sha
            req_data = json.dumps(data).encode("utf-8")
            put_req = urllib.request.Request(check_url, data=req_data, headers={"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json", "User-Agent": "AdminApp"}, method="PUT")
            with urllib.request.urlopen(put_req):
                messagebox.showinfo("Thành công", "Đã lưu Trangchu.py và đồng bộ GitHub!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    tk.Button(trangchu_edit_frame, text="💾 Lưu Trangchu.py & Đồng Bộ GitHub", command=handle_save_and_sync_trangchu, font=("Arial", 8, "bold"), fg="white", bg="#20c997", bd=0, cursor="hand2").pack(fill="x", padx=3, ipady=4)

    # 7. Nút hệ thống chung (Làm mới & Reset Server)
    def handle_reset_server():
        if messagebox.askyesno("Xác nhận", "Reset Server (Tải lại toàn bộ code mới nhất từ GitHub)?"):
            try:
                root.destroy()
                subprocess.run([
                    sys.executable, "-c",
                    "import urllib.request, os, sys;"
                    "base = 'https://raw.githubusercontent.com/huyxaa00-eng/my_project/main/';"
                    "[open(f, 'w', encoding='utf-8').write(urllib.request.urlopen(base + f).read().decode('utf-8')) for f in ['main.py', 'Trangchu.py']];"
                    "os.execv(sys.executable, [sys.executable, 'main.py'])"
                ])
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    bottom_btn_frame = tk.Frame(scrollable_frame, bg="#667EEA")
    bottom_btn_frame.pack(fill="x", pady=(5, 10))
    tk.Button(bottom_btn_frame, text="🔄 Làm Mới", command=load_users, font=("Arial", 9, "bold"), fg="white", bg="#17A2B8", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=5, padx=1)
    tk.Button(bottom_btn_frame, text="🔁 Reset Server", command=handle_reset_server, font=("Arial", 9, "bold"), fg="white", bg="#E83E8C", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=5, padx=1)

def show_login():
    clear_window()
    tk.Label(root, text="Welcome Back!", font=("Arial", 24, "bold"), fg="white", bg="#667EEA").pack(pady=(30, 5))
    tk.Label(root, text="Đăng nhập hệ thống đám mây", font=("Arial", 10), fg="#E0E0E0", bg="#667EEA").pack(pady=(0, 15))

    form_frame = tk.Frame(root, bg="#667EEA")
    form_frame.pack(padx=24, fill="x")

    tk.Label(form_frame, text="Email hoặc số điện thoại", fg="white", bg="#667EEA", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 3))
    email_entry = tk.Entry(form_frame, font=("Arial", 12), bg="#FFFFFF", bd=0, relief="solid")
    email_entry.pack(fill="x", ipady=6, pady=(0, 10))

    tk.Label(form_frame, text="Mật khẩu", fg="white", bg="#667EEA", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 3))
    pass_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), bg="#FFFFFF", bd=0, relief="solid")
    pass_entry.pack(fill="x", ipady=6, pady=(0, 12))

    def handle_login():
        email = email_entry.get().strip()
        password = pass_entry.get().strip()
        if not email or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        try:
            query = f"?email=eq.{urllib.parse.quote(email)}&password=eq.{urllib.parse.quote(password)}"
            response = supabase_request("users", method="GET", query_params=query)
            if response and len(response) > 0:
                if email.lower() == ADMIN_EMAIL.lower():
                    show_admin_dashboard(email)
                else:
                    messagebox.showinfo("Thành công", f"Đăng nhập thành công!\nĐang đồng bộ code mới từ máy chủ...")
                    root.destroy()
                    subprocess.run([
                        sys.executable, "-c",
                        "import urllib.request, os, sys;"
                        "base = 'https://raw.githubusercontent.com/huyxaa00-eng/my_project/main/';"
                        "[open(f, 'w', encoding='utf-8').write(urllib.request.urlopen(base + f).read().decode('utf-8')) for f in ['main.py', 'Trangchu.py']];"
                        "os.execv(sys.executable, [sys.executable, 'main.py'])"
                    ])
            else:
                messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu")
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", str(e))

    tk.Button(form_frame, text="Đăng nhập", command=handle_login, font=("Arial", 12, "bold"), fg="white", bg="#FF416C", bd=0, cursor="hand2").pack(fill="x", ipady=8, pady=(0, 12))

    reg_frame = tk.Frame(root, bg="#667EEA")
    reg_frame.pack(pady=5)
    tk.Label(reg_frame, text="Chưa có tài khoản? ", fg="#E0E0E0", bg="#667EEA", font=("Arial", 9)).pack(side="left")
    tk.Button(reg_frame, text="Tạo tài khoản", command=show_register, fg="white", bg="#667EEA", font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side="left")

def show_register():
    clear_window()
    tk.Label(root, text="Tạo tài khoản", font=("Arial", 24, "bold"), fg="white", bg="#667EEA").pack(pady=(30, 5))
    tk.Label(root, text="Đăng ký lưu trữ trực tuyến", font=("Arial", 10), fg="#E0E0E0", bg="#667EEA").pack(pady=(0, 15))

    form_frame = tk.Frame(root, bg="#667EEA")
    form_frame.pack(padx=24, fill="x")

    tk.Label(form_frame, text="Email hoặc số điện thoại", fg="white", bg="#667EEA", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 3))
    reg_email = tk.Entry(form_frame, font=("Arial", 12), bg="#FFFFFF", bd=0, relief="solid")
    reg_email.pack(fill="x", ipady=6, pady=(0, 10))

    tk.Label(form_frame, text="Mật khẩu", fg="white", bg="#667EEA", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 3))
    reg_pass = tk.Entry(form_frame, show="*", font=("Arial", 12), bg="#FFFFFF", bd=0, relief="solid")
    reg_pass.pack(fill="x", ipady=6, pady=(0, 10))

    def handle_register():
        email = reg_email.get().strip()
        password = reg_pass.get().strip()
        if not email or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        if len(password) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu phải từ 6 ký tự trở lên")
            return
        try:
            expiry_datetime = datetime.now() + timedelta(days=DEFAULT_TRIAL_DAYS, hours=DEFAULT_TRIAL_HOURS)
            new_user_data = {
                "email": email,
                "password": password,
                "balance": 0,
                "expiry_date": expiry_datetime.strftime("%Y-%m-%d")
            }
            supabase_request("users", method="POST", data=new_user_data)
            messagebox.showinfo("Thành công", f"Đăng ký thành công!\nĐược tặng {DEFAULT_TRIAL_DAYS} ngày và {DEFAULT_TRIAL_HOURS} giờ dùng thử.")
            show_login()
        except Exception as e:
            messagebox.showerror("Lỗi đăng ký", str(e))

    tk.Button(form_frame, text="Đăng ký ngay", command=handle_register, font=("Arial", 12, "bold"), fg="white", bg="#FF416C", bd=0, cursor="hand2").pack(fill="x", ipady=8, pady=(0, 10))

    back_frame = tk.Frame(root, bg="#667EEA")
    back_frame.pack(pady=5)
    tk.Label(back_frame, text="Đã có tài khoản? ", fg="#E0E0E0", bg="#667EEA", font=("Arial", 9)).pack(side="left")
    tk.Button(back_frame, text="Đăng nhập", command=show_login, fg="white", bg="#667EEA", font=("Arial", 9, "bold"), bd=0, cursor="hand2").pack(side="left")

show_login()
root.mainloop()
