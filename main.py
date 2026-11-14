import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request
import json
import urllib.parse
from datetime import datetime, timedelta
import os
import sys
import subprocess

SUPABASE_URL = "https://dvbhaxymloazsqvnwefd.supabase.co"
SUPABASE_KEY = "sb_publishable_hWWTO_k0YxAsq3jjw9LCtg_V2S03ORC"

ADMIN_EMAIL = "admin@gmail.com"

DEFAULT_TRIAL_HOURS = 0
DEFAULT_TRIAL_DAYS = 3

GITHUB_RAW_URL = "https://raw.githubusercontent.com/huyxaa00-eng/my_project/main/main.py"
LOCAL_SCRIPT_NAME = "main.py"

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
        err_message = e.read().decode("utf-8")
        raise Exception(err_message)
    except Exception as e:
        raise Exception(str(e))

root = tk.Tk()
root.title("Hệ Thống Quản Trị Supabase Cloud")
root.geometry("440x820")
root.configure(bg="#667EEA")

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# --- HÀM TỰ ĐỘNG CẬP NHẬT KÈM HIỂN THỊ % TẢI VỀ KHI KHỞI ĐỘNG ---
def check_and_auto_update():
    clear_window()
    
    tk.Label(root, text="🔄 Đang kiểm tra cập nhật...", font=("Arial", 16, "bold"), fg="white", bg="#667EEA").pack(pady=(150, 10))
    
    status_lbl = tk.Label(root, text="Đang kết nối tới GitHub...", font=("Arial", 11), fg="#E0E0E0", bg="#667EEA")
    status_lbl.pack(pady=(0, 20))

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)

    percent_lbl = tk.Label(root, text="0%", font=("Arial", 12, "bold"), fg="white", bg="#667EEA")
    percent_lbl.pack(pady=10)

    def run_download():
        try:
            req = urllib.request.urlopen(GITHUB_RAW_URL, timeout=5)
            total_size = int(req.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            buffer = bytearray()

            while True:
                chunk = req.read(chunk_size)
                if not chunk:
                    break
                buffer.extend(chunk)
                downloaded += len(chunk)
                
                if total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    progress['value'] = percent
                    percent_lbl.config(text=f"{percent}%")
                    status_lbl.config(text=f"Đã tải: {downloaded // 1024} KB / {total_size // 1024} KB")
                    root.update_idletasks()

            with open(LOCAL_SCRIPT_NAME, "wb") as f:
                f.write(buffer)
            
            status_lbl.config(text="✅ Cập nhật thành công! Đang khởi động lại...")
            root.update()
            root.after(1000, lambda: restart_app())

        except Exception as e:
            status_lbl.config(text="⚠️ Lỗi kết nối mạng, đang dùng bản cục bộ...")
            root.update()
            root.after(1500, lambda: show_login())

    root.after(500, run_download)

def restart_app():
    root.destroy()
    os.execv(sys.executable, [sys.executable, LOCAL_SCRIPT_NAME])

# --- GIAO DIỆN QUẢN TRỊ VIÊN ---
def show_admin_dashboard(admin_email):
    clear_window()
    
    top_bar = tk.Frame(root, bg="#667EEA")
    top_bar.pack(padx=15, fill="x", pady=(10, 0))
    
    tk.Button(top_bar, text="🚪 Đăng Xuất", command=show_login, font=("Arial", 9, "bold"), fg="white", bg="#DC3545", bd=0, cursor="hand2").pack(side="right", ipadx=8, ipady=4)

    tk.Label(root, text="🛡️ QUẢN TRỊ VIÊN HỆ THỐNG", font=("Arial", 15, "bold"), fg="white", bg="#667EEA").pack(pady=(5, 5))

    config_frame = tk.LabelFrame(root, text="⚙️ Cài đặt dùng thử cho tài khoản mới", font=("Arial", 9, "bold"), fg="white", bg="#667EEA", bd=1, relief="solid")
    config_frame.pack(padx=15, fill="x", pady=(0, 5), ipadx=5, ipady=5)

    cfg_sub = tk.Frame(config_frame, bg="#667EEA")
    cfg_sub.pack(fill="x", padx=5)

    tk.Label(cfg_sub, text="Giờ:", fg="white", bg="#667EEA", font=("Arial", 9)).pack(side="left")
    hours_entry = tk.Entry(cfg_sub, font=("Arial", 10), width=5, bg="#FFFFFF", bd=0, relief="solid")
    hours_entry.insert(0, str(DEFAULT_TRIAL_HOURS))
    hours_entry.pack(side="left", padx=(2, 8))

    tk.Label(cfg_sub, text="Ngày:", fg="white", bg="#667EEA", font=("Arial", 9)).pack(side="left")
    days_entry = tk.Entry(cfg_sub, font=("Arial", 10), width=5, bg="#FFFFFF", bd=0, relief="solid")
    days_entry.insert(0, str(DEFAULT_TRIAL_DAYS))
    days_entry.pack(side="left", padx=(2, 8))

    def save_trial_config():
        global DEFAULT_TRIAL_HOURS, DEFAULT_TRIAL_DAYS
        try:
            DEFAULT_TRIAL_HOURS = int(hours_entry.get().strip() or 0)
            DEFAULT_TRIAL_DAYS = int(days_entry.get().strip() or 0)
            messagebox.showinfo("Thành công", f"Đã lưu cấu hình:\n- Số giờ: {DEFAULT_TRIAL_HOURS}\n- Số ngày: {DEFAULT_TRIAL_DAYS}")
        except ValueError:
            messagebox.showerror("Lỗi", "Số giờ và số ngày phải là số nguyên!")

    tk.Button(cfg_sub, text="Lưu Cấu Hình", command=save_trial_config, font=("Arial", 9, "bold"), fg="white", bg="#E67E22", bd=0, cursor="hand2").pack(side="right", ipadx=6, ipady=2)

    frame_list = tk.Frame(root, bg="white", bd=1, relief="solid")
    frame_list.pack(padx=15, fill="both", expand=True, pady=(0, 5))

    tk.Label(frame_list, text="📋 Danh Sách Thành Viên (Email | Số Tiền | Ngày Hạn)", font=("Arial", 10, "bold"), bg="white", fg="#333").pack(pady=4)

    listbox_frame = tk.Frame(frame_list, bg="white")
    listbox_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side="right", fill="y")

    user_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Courier", 10), bg="#F8F9FA", bd=1, relief="solid")
    user_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=user_listbox.yview)

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
                            days_left = f"{int(delta)} ngày" if delta >= 1 else f"{int(delta*24)} giờ"
                        else:
                            days_left = "Hết hạn"
                    except:
                        pass

                display_text = f"{email:<22} | {balance:>6}đ | {days_left}"
                user_listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách: {str(e)}")

    load_users()

    action_frame = tk.Frame(root, bg="#667EEA")
    action_frame.pack(padx=15, fill="x", pady=(0, 5))

    input_sub_frame = tk.Frame(action_frame, bg="#667EEA")
    input_sub_frame.pack(fill="x", pady=(0, 3))

    tk.Label(input_sub_frame, text="Email được chọn:", fg="white", bg="#667EEA", font=("Arial", 9, "bold")).pack(anchor="w")
    email_action_entry = tk.Entry(input_sub_frame, font=("Arial", 11), bg="#FFFFFF", bd=0, relief="solid")
    email_action_entry.pack(fill="x", ipady=3, pady=(0, 4))

    val_frame = tk.Frame(action_frame, bg="#667EEA")
    val_frame.pack(fill="x", pady=(0, 5))

    f1 = tk.Frame(val_frame, bg="#667EEA")
    f1.pack(side="left", expand=True, fill="x", padx=(0, 5))
    tk.Label(f1, text="Cộng/Trừ Tiền (VNĐ):", fg="white", bg="#667EEA", font=("Arial", 9)).pack(anchor="w")
    money_entry = tk.Entry(f1, font=("Arial", 11), bg="#FFFFFF", bd=0, relief="solid")
    money_entry.pack(fill="x", ipady=3)

    f2 = tk.Frame(val_frame, bg="#667EEA")
    f2.pack(side="left", expand=True, fill="x")
    tk.Label(f2, text="Cộng Thêm Số Ngày:", fg="white", bg="#667EEA", font=("Arial", 9)).pack(anchor="w")
    days_entry_act = tk.Entry(f2, font=("Arial", 11), bg="#FFFFFF", bd=0, relief="solid")
    days_entry_act.pack(fill="x", ipady=3)

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
            messagebox.showerror("Lỗi", "Vui lòng chọn tài khoản từ danh sách!")
            return
        
        money_str = money_entry.get().strip()
        days_str = days_entry_act.get().strip()

        try:
            current_user = supabase_request("users", method="GET", query_params=f"?email=eq.{urllib.parse.quote(email)}&select=balance,expiry_date")
            if not current_user:
                messagebox.showerror("Lỗi", "Không tìm thấy tài khoản trên Cloud!")
                return
            
            old_balance = current_user[0].get('balance') or 0
            old_expiry = current_user[0].get('expiry_date')

            update_data = {}

            if money_str:
                add_money = int(money_str)
                update_data["balance"] = old_balance + add_money

            if days_str:
                add_days = int(days_str)
                base_date = datetime.now()
                if old_expiry:
                    try:
                        parsed_old = datetime.strptime(old_expiry, "%Y-%m-%d %H:%M:%S" if len(old_expiry) > 10 else "%Y-%m-%d")
                        if parsed_old > base_date:
                            base_date = parsed_old
                    except:
                        pass
                new_expiry_date = base_date + timedelta(days=add_days)
                update_data["expiry_date"] = new_expiry_date.strftime("%Y-%m-%d %H:%M:%S")

            if not update_data:
                messagebox.showerror("Lỗi", "Vui lòng nhập số tiền hoặc số ngày cần cộng!")
                return

            query = f"?email=eq.{urllib.parse.quote(email)}"
            supabase_request("users", method="PATCH", data=update_data, query_params=query)
            
            messagebox.showinfo("Thành công", f"Đã cập nhật cho tài khoản: {email}")
            money_entry.delete(0, tk.END)
            days_entry_act.delete(0, tk.END)
            load_users()

        except ValueError:
            messagebox.showerror("Lỗi định dạng", "Số tiền và số ngày phải là số nguyên hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def handle_reset_password():
        email = email_action_entry.get().strip()
        new_pass = money_entry.get().strip()
        if not email or not new_pass:
            messagebox.showerror("Lỗi", "Vui lòng chọn email và nhập mật khẩu mới vào ô 'Cộng/Trừ Tiền'!")
            return
        try:
            query = f"?email=eq.{urllib.parse.quote(email)}"
            supabase_request("users", method="PATCH", data={"password": new_pass}, query_params=query)
            messagebox.showinfo("Thành công", f"Đã đổi mật khẩu cho: {email}")
            load_users()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    btn_grid = tk.Frame(action_frame, bg="#667EEA")
    btn_grid.pack(fill="x", pady=5)

    tk.Button(btn_grid, text="💰 Cộng Tiền / Ngày", command=handle_add_money_and_days, font=("Arial", 9, "bold"), fg="white", bg="#28A745", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=6, padx=2)
    tk.Button(btn_grid, text="🔑 Đổi Pass", command=handle_reset_password, font=("Arial", 9, "bold"), fg="white", bg="#FFC107", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=6, padx=2)

    bottom_btn_frame = tk.Frame(root, bg="#667EEA")
    bottom_btn_frame.pack(padx=15, fill="x", pady=(5, 10))

    tk.Button(bottom_btn_frame, text="🔄 Làm Mới", command=load_users, font=("Arial", 10, "bold"), fg="white", bg="#17A2B8", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=6, padx=2)
    tk.Button(bottom_btn_frame, text="🚪 Đăng Xuất", command=show_login, font=("Arial", 10, "bold"), fg="white", bg="#343A40", bd=0, cursor="hand2").pack(side="left", expand=True, fill="x", ipady=6, padx=2)

# --- GIAO DIỆN ĐĂNG NHẬP ---
def show_login():
    clear_window()
    
    tk.Label(root, text="Welcome Back!", font=("Arial", 26, "bold"), fg="white", bg="#667EEA").pack(pady=(40, 10))
    tk.Label(root, text="Đăng nhập hệ thống đám mây", font=("Arial", 11), fg="#E0E0E0", bg="#667EEA").pack(pady=(0, 20))

    form_frame = tk.Frame(root, bg="#667EEA")
    form_frame.pack(padx=24, fill="x")

    tk.Label(form_frame, text="Email hoặc số điện thoại", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    email_entry = tk.Entry(form_frame, font=("Arial", 13), bg="#FFFFFF", bd=0, relief="solid")
    email_entry.pack(fill="x", ipady=8, pady=(0, 12))

    tk.Label(form_frame, text="Mật khẩu", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    pass_entry = tk.Entry(form_frame, show="*", font=("Arial", 13), bg="#FFFFFF", bd=0, relief="solid")
    pass_entry.pack(fill="x", ipady=8, pady=(0, 15))

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
                    messagebox.showinfo("Thành công", f"Đăng nhập thành công!\nXin chào: {email}")
                    
                    # Đóng giao diện đăng nhập hiện tại và tự động đồng bộ/chạy file mới nhất từ GitHub
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

    tk.Button(form_frame, text="Đăng nhập", command=handle_login, font=("Arial", 13, "bold"), fg="white", bg="#FF416C", bd=0, cursor="hand2").pack(fill="x", ipady=10, pady=(0, 15))

    reg_frame = tk.Frame(root, bg="#667EEA")
    reg_frame.pack(pady=5)
    tk.Label(reg_frame, text="Chưa có tài khoản? ", fg="#E0E0E0", bg="#667EEA", font=("Arial", 10)).pack(side="left")
    tk.Button(reg_frame, text="Tạo tài khoản", command=show_register, fg="white", bg="#667EEA", font=("Arial", 10, "bold"), bd=0, cursor="hand2").pack(side="left")

# --- GIAO DIỆN ĐĂNG KÝ ---
def show_register():
    clear_window()

    tk.Label(root, text="Tạo tài khoản", font=("Arial", 26, "bold"), fg="white", bg="#667EEA").pack(pady=(40, 10))
    tk.Label(root, text="Đăng ký lưu trữ trực tuyến", font=("Arial", 11), fg="#E0E0E0", bg="#667EEA").pack(pady=(0, 15))

    form_frame = tk.Frame(root, bg="#667EEA")
    form_frame.pack(padx=24, fill="x")

    tk.Label(form_frame, text="Email hoặc số điện thoại", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    reg_email = tk.Entry(form_frame, font=("Arial", 13), bg="#FFFFFF", bd=0, relief="solid")
    reg_email.pack(fill="x", ipady=8, pady=(0, 10))

    tk.Label(form_frame, text="Mật khẩu", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    reg_pass = tk.Entry(form_frame, show="*", font=("Arial", 13), bg="#FFFFFF", bd=0, relief="solid")
    reg_pass.pack(fill="x", ipady=8, pady=(0, 10))

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

    tk.Button(form_frame, text="Đăng ký ngay", command=handle_register, font=("Arial", 13, "bold"), fg="white", bg="#FF416C", bd=0, cursor="hand2").pack(fill="x", ipady=10, pady=(0, 10))

    back_frame = tk.Frame(root, bg="#667EEA")
    back_frame.pack(pady=5)
    tk.Label(back_frame, text="Đã có tài khoản? ", fg="#E0E0E0", bg="#667EEA", font=("Arial", 10)).pack(side="left")
    tk.Button(back_frame, text="Đăng nhập", command=show_login, fg="white", bg="#667EEA", font=("Arial", 10, "bold"), bd=0, cursor="hand2").pack(side="left")

# Khởi động ứng dụng, tự động kiểm tra % update trước tiên
check_and_auto_update()
root.mainloop()
EOF
