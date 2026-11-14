import tkinter as tk
from tkinter import messagebox
import urllib.request
import json

SUPABASE_URL = "https://dvbhaxymloazsqvnwefd.supabase.co"
SUPABASE_KEY = "sb_publishable_hWWTO_k0YxAsq3jjw9LCtg_V2S03ORC"

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
root.title("Ứng dụng Online Supabase")
root.geometry("400x650")
root.configure(bg="#667EEA")

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def show_login():
    clear_window()
    
    tk.Label(root, text="Welcome Back!", font=("Arial", 28, "bold"), fg="white", bg="#667EEA").pack(pady=(50, 10))
    tk.Label(root, text="Đăng nhập dữ liệu đám mây", font=("Arial", 12), fg="#E0E0E0", bg="#667EEA").pack(pady=(0, 30))

    form_frame = tk.Frame(root, bg="#667EEA")
    form_frame.pack(padx=24, fill="x")

    tk.Label(form_frame, text="Email hoặc số điện thoại", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    email_entry = tk.Entry(form_frame, font=("Arial", 14), bg="#FFFFFF", bd=0, relief="solid")
    email_entry.pack(fill="x", ipady=10, pady=(0, 15))

    tk.Label(form_frame, text="Mật khẩu", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    pass_entry = tk.Entry(form_frame, show="*", font=("Arial", 14), bg="#FFFFFF", bd=0, relief="solid")
    pass_entry.pack(fill="x", ipady=10, pady=(0, 20))

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
                messagebox.showinfo("Thành công", "Đăng nhập thành công từ Supabase!")
            else:
                messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu")
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", str(e))

    tk.Button(form_frame, text="Đăng nhập", command=handle_login, font=("Arial", 14, "bold"), fg="white", bg="#FF416C", bd=0, cursor="hand2").pack(fill="x", ipady=12, pady=(0, 20))

    reg_frame = tk.Frame(root, bg="#667EEA")
    reg_frame.pack(pady=10)
    tk.Label(reg_frame, text="Chưa có tài khoản? ", fg="#E0E0E0", bg="#667EEA", font=("Arial", 10)).pack(side="left")
    tk.Button(reg_frame, text="Tạo tài khoản", command=show_register, fg="white", bg="#667EEA", font=("Arial", 10, "bold"), bd=0, cursor="hand2").pack(side="left")

def show_register():
    clear_window()
    
    tk.Label(root, text="Tạo tài khoản", font=("Arial", 28, "bold"), fg="white", bg="#667EEA").pack(pady=(40, 10))
    tk.Label(root, text="Đăng ký lưu trữ trực tuyến", font=("Arial", 12), fg="#E0E0E0", bg="#667EEA").pack(pady=(0, 20))

    form_frame = tk.Frame(root, bg="#667EEA")
    form_frame.pack(padx=24, fill="x")

    tk.Label(form_frame, text="Email hoặc số điện thoại", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    reg_email = tk.Entry(form_frame, font=("Arial", 14), bg="#FFFFFF", bd=0, relief="solid")
    reg_email.pack(fill="x", ipady=10, pady=(0, 12))

    tk.Label(form_frame, text="Mật khẩu", fg="white", bg="#667EEA", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
    reg_pass = tk.Entry(form_frame, show="*", font=("Arial", 14), bg="#FFFFFF", bd=0, relief="solid")
    reg_pass.pack(fill="x", ipady=10, pady=(0, 12))

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
            supabase_request("users", method="POST", data={"email": email, "password": password})
            messagebox.showinfo("Thành công", "Đăng ký tài khoản lên Cloud thành công!")
            show_login()
        except Exception as e:
            messagebox.showerror("Lỗi đăng ký", str(e))

    tk.Button(form_frame, text="Đăng ký ngay", command=handle_register, font=("Arial", 14, "bold"), fg="white", bg="#FF416C", bd=0, cursor="hand2").pack(fill="x", ipady=12, pady=(0, 15))

    back_frame = tk.Frame(root, bg="#667EEA")
    back_frame.pack(pady=5)
    tk.Label(back_frame, text="Đã có tài khoản? ", fg="#E0E0E0", bg="#667EEA", font=("Arial", 10)).pack(side="left")
    tk.Button(back_frame, text="Đăng nhập", command=show_login, fg="white", bg="#667EEA", font=("Arial", 10, "bold"), bd=0, cursor="hand2").pack(side="left")

show_login()
root.mainloop()
