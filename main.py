import os
import sys

# Tự động trỏ đường dẫn vào thư mục libs trong cùng project
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs'))
)

# Sau đó bạn tiến hành import thư viện như bình thường
import ten_thu_vien
import os, subprocess, sys, json, threading, urllib.request, tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog

CONFIG_FILE = "saved_links.json"
AUTO_FILE = "auto.py"
DOWNLOAD_DIR = "downloaded_scripts"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def load_links():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_links(links):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=4)

class FloatingApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("140x45+50+50")
        self.root.configure(bg="#222")
        
        try:
            self.root.attributes("-topmost", True)
        except:
            pass

        self.current_process = None
        self.panel_window = None

        self.btn_float = tk.Button(
            root, text="💬 BONG BÓNG", 
            command=self.toggle_main_panel, 
            bg="#ff9800", fg="#000", 
            font=("Arial", 9, "bold"),
            relief="raised", bd=2
        )
        self.btn_float.pack(fill="both", expand=True)

        self.btn_float.bind("<B1-Motion>", self.move_window)
        self.btn_float.bind("<Button-1>", self.get_pos)
        
        self.keep_on_top()

    def keep_on_top(self):
        try:
            self.root.attributes("-topmost", True)
            if self.panel_window and tk.Toplevel.winfo_exists(self.panel_window):
                self.panel_window.attributes("-topmost", True)
        except:
            pass
        self.root.after(1000, self.keep_on_top)

    def get_pos(self, event):
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def get_panel_pos(self, event):
        self.px = event.x
        self.py = event.y

    def move_panel_window(self, event):
        if self.panel_window:
            deltax = event.x - self.px
            deltay = event.y - self.py
            x = self.panel_window.winfo_x() + deltax
            y = self.panel_window.winfo_y() + deltay
            self.panel_window.geometry(f"+{x}+{y}")

    def toggle_main_panel(self):
        if self.panel_window is not None and tk.Toplevel.winfo_exists(self.panel_window):
            self.panel_window.destroy()
            self.panel_window = None
            return

        self.panel_window = tk.Toplevel(self.root)
        self.panel_window.overrideredirect(True)
        self.panel_window.geometry("460x700+100+100")
        self.panel_window.configure(bg="#222")
        try:
            self.panel_window.attributes("-topmost", True)
        except:
            pass

        title_bar = tk.Frame(self.panel_window, bg="#007acc", relief="raised", bd=1)
        title_bar.pack(fill="x")
        
        lbl_title = tk.Label(title_bar, text="≡ QUẢN LÝ & CHẠY PYTHON (X11) [Kéo để dịch chuyển]", font=("Arial", 9, "bold"), bg="#007acc", fg="#fff")
        lbl_title.pack(side="left", padx=5, pady=4)
        
        btn_close_panel = tk.Button(title_bar, text="✕", command=self.toggle_main_panel, bg="#c9302c", fg="#fff", font=("Arial", 8, "bold"), relief="flat")
        btn_close_panel.pack(side="right", padx=2, pady=2)

        title_bar.bind("<B1-Motion>", self.move_panel_window)
        title_bar.bind("<Button-1>", self.get_panel_pos)
        lbl_title.bind("<B1-Motion>", self.move_panel_window)
        lbl_title.bind("<Button-1>", self.get_panel_pos)

        f_top1 = tk.Frame(self.panel_window, bg="#222")
        f_top1.pack(pady=4)

        tk.Button(f_top1, text="📁 Chọn", command=self.browse_all_python_files, bg="#444", fg="#fff", font=("Arial", 9)).grid(row=0, column=0, padx=2)
        tk.Button(f_top1, text="➕ Thêm File", command=self.add_shortcut, bg="#d9534f", fg="#fff", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=2)
        tk.Button(f_top1, text="🌐 Thêm Git", command=self.add_git_link, bg="#f0ad4e", fg="#fff", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=2)

        f_top2 = tk.Frame(self.panel_window, bg="#222")
        f_top2.pack(pady=3)

        tk.Button(f_top2, text="📋 Dán Auto Mới", command=self.paste_and_run_auto, bg="#28a745", fg="#fff", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=2)
        tk.Button(f_top2, text="⏹ Dừng / Thoát", command=self.stop_current_process, bg="#c9302c", fg="#fff", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=2)
        tk.Button(f_top2, text="🏠 Trang Chủ", command=self.go_home, bg="#0275d8", fg="#fff", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=2)

        tk.Label(self.panel_window, text="Danh sách file Auto & File đã lưu:", bg="#222", fg="#ff0", font=("Arial", 9)).pack(anchor="w", padx=15, pady=(5,0))
        
        self.canvas_frame = tk.Frame(self.panel_window, bg="#1a1a1a")
        self.canvas_frame.pack(padx=15, pady=5, fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_inner = tk.Frame(self.canvas, bg="#1a1a1a")

        self.scrollable_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        f_log_header = tk.Frame(self.panel_window, bg="#222")
        f_log_header.pack(fill="x", padx=15, pady=(5, 0))
        tk.Label(f_log_header, text="Kết quả thực thi:", bg="#222", fg="#fff", font=("Arial", 9)).pack(side="left")
        tk.Button(f_log_header, text="⏹ Thoát File Đang Chạy", command=self.stop_current_process, bg="#d9534f", fg="#fff", font=("Arial", 8, "bold")).pack(side="right")

        self.output_text = scrolledtext.ScrolledText(self.panel_window, font=("Consolas", 8), bg="#111", fg="#0f0", height=9)
        self.output_text.pack(padx=15, pady=2, fill="both", expand=False)

        self.refresh_shortcuts()

    def run_path(self, p):
        p = p.strip().strip('"').strip("'")
        if not p or not os.path.exists(p):
            messagebox.showerror("Lỗi", f"Không tìm thấy đường dẫn:\n{p}")
            return
        
        if self.current_process:
            self.stop_current_process()

        if self.panel_window and hasattr(self, 'output_text'):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Đang chạy: {p}\n" + "-"*35 + "\n")
        
        def target():
            try:
                self.current_process = subprocess.Popen(
                    [sys.executable, p],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
                stdout, stderr = self.current_process.communicate()
                
                if self.panel_window and hasattr(self, 'output_text'):
                    if stdout:
                        self.output_text.insert(tk.END, stdout)
                    if stderr:
                        self.output_text.insert(tk.END, f"\n[LỖI]:\n{stderr}")
                    self.output_text.insert(tk.END, "\n" + "-"*35 + "\n[Hoàn tất! Bấm '🏠 Trang Chủ' để quay lại]")
            except Exception as ex:
                if self.panel_window and hasattr(self, 'output_text'):
                    self.output_text.insert(tk.END, f"\nLỗi thực thi: {str(ex)}")
            finally:
                self.current_process = None

        threading.Thread(target=target, daemon=True).start()

    def stop_current_process(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process = None
                if self.panel_window and hasattr(self, 'output_text'):
                    self.output_text.insert(tk.END, "\n\n❌ [Đã dừng/thoát file theo yêu cầu!]")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        else:
            if self.panel_window and hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, "\n⚠️ Không có tiến trình nào đang chạy.")

    def go_home(self):
        self.stop_current_process()
        if self.panel_window and hasattr(self, 'output_text'):
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Đã về trang chủ. Chọn file hoặc bấm nút để chạy.")
            self.refresh_shortcuts()

    def browse_all_python_files(self):
        py_files = []
        start_dir = os.getcwd()
        for root_dir, dirs, files in os.walk(start_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root_dir, file))

        if not py_files:
            messagebox.showinfo("Thông báo", "Không tìm thấy file .py nào trong thư mục!")
            return

        win = tk.Toplevel(self.panel_window)
        win.title("Chọn file Python có sẵn")
        win.geometry("380x450")
        win.configure(bg="#222")
        try:
            win.attributes("-topmost", True)
        except:
            pass

        tk.Label(win, text="Danh sách file .py trong máy:", bg="#222", fg="#0ff", font=("Arial", 10, "bold")).pack(pady=10)

        frame_list = tk.Frame(win, bg="#111")
        frame_list.pack(padx=10, pady=5, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame_list, font=("Consolas", 9), bg="#111", fg="#0f0", yscrollcommand=scrollbar.set)
        for f in py_files:
            listbox.insert(tk.END, f)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        def on_select():
            selected_indices = listbox.curselection()
            if selected_indices:
                chosen_file = listbox.get(selected_indices[0])
                win.destroy()
                self.run_path(chosen_file)

        tk.Button(win, text="🚀 Chạy file đã chọn", command=on_select, bg="#007acc", fg="#fff", font=("Arial", 10, "bold")).pack(pady=10)

    def add_shortcut(self):
        f = filedialog.askopenfilename(title="Chọn file Python để thêm vào menu", filetypes=[("Python Files", "*.py")])
        if not f:
            return
        default_name = os.path.basename(f)
        name = simpledialog.askstring("Đặt tên nút", "Nhập tên hiển thị cho nút bấm:", initialvalue=default_name, parent=self.panel_window)
        if name:
            links = load_links()
            links[name] = f
            save_links(links)
            self.refresh_shortcuts()

    def add_git_link(self):
        git_url = simpledialog.askstring("Thêm Link Git/GitHub", "Dán đường dẫn file .py trên GitHub (khuyên dùng link Raw):", parent=self.panel_window)
        if not git_url:
            return
        
        git_url = git_url.strip().strip('"').strip("'")
        if "github.com" in git_url and "/blob/" in git_url:
            git_url = git_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        default_name = git_url.split("/")[-1]
        if not default_name.endswith(".py"):
            default_name += ".py"

        name = simpledialog.askstring("Đặt tên nút", "Nhập tên hiển thị cho nút bấm Git này:", initialvalue=default_name, parent=self.panel_window)
        if not name:
            return

        try:
            req = urllib.request.urlopen(git_url)
            code_content = req.read().decode("utf-8")
            
            save_path = os.path.join(DOWNLOAD_DIR, name)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(code_content)

            links = load_links()
            links[name] = os.path.abspath(save_path)
            save_links(links)
            self.refresh_shortcuts()
            messagebox.showinfo("Thành công", f"Đã thêm và lưu nút '{name}' thành công!")
        except Exception as ex:
            messagebox.showerror("Lỗi tải Git", f"Không thể tải code từ đường dẫn trên:\n{str(ex)}")

    def delete_auto_file(self, filename):
        if messagebox.askyesno("Xác nhận xoá file", f"Bạn có chắc muốn xoá vĩnh viễn file '{filename}' khỏi máy không?"):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                self.refresh_shortcuts()
                messagebox.showinfo("Thành công", f"Đã xoá file {filename} khỏi máy.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xoá file:\n{str(e)}")

    def delete_shortcut(self, name):
        if messagebox.askyesno("Xác nhận", f"Bạn có muốn xóa nút '{name}' và xóa file nguồn trong máy không?"):
            links = load_links()
            if name in links:
                path = links[name]
                try:
                    if os.path.exists(path) and os.path.abspath(path) != os.path.abspath("minh999.py"):
                        os.remove(path)
                except Exception as ex:
                    print(f"Không thể xoá file vật lý: {ex}")
                
                del links[name]
                save_links(links)
                self.refresh_shortcuts()

    def refresh_shortcuts(self):
        if not self.panel_window or not hasattr(self, 'scrollable_inner'):
            return
        for widget in self.scrollable_inner.winfo_children():
            widget.destroy()

        auto_files = []
        for f in os.listdir('.'):
            if f.lower().startswith('auto') and f.endswith('.py') and f != "minh999.py":
                auto_files.append(f)

        if auto_files:
            # Khung chứa nhóm file Auto gọn gàng
            f_auto_group = tk.Frame(self.scrollable_inner, bg="#1a1a1a")
            f_auto_group.pack(fill="x", pady=2, padx=2)

            tk.Label(f_auto_group, text="⚡ Các file Auto:", bg="#1a1a1a", fg="#28a745", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0,2))
            
            for af in sorted(auto_files):
                row_f = tk.Frame(f_auto_group, bg="#2a2a2a", bd=1, relief="solid")
                row_f.pack(fill="x", pady=2, padx=2)
                
                btn_run_auto = tk.Button(row_f, text=f"▶ {af}", command=lambda p=af: self.run_path(p), bg="#28a745", fg="#fff", font=("Arial", 9, "bold"), anchor="w", relief="flat")
                btn_run_auto.pack(side="left", fill="x", expand=True, padx=4, pady=3)

                btn_del_auto = tk.Button(row_f, text="❌ Xoá", command=lambda filename=af: self.delete_auto_file(filename), bg="#c9302c", fg="#fff", font=("Arial", 8, "bold"), relief="flat")
                btn_del_auto.pack(side="right", padx=4, pady=3)

        links = load_links()
        if links:
            f_links_group = tk.Frame(self.scrollable_inner, bg="#1a1a1a")
            f_links_group.pack(fill="x", pady=5, padx=2)

            tk.Label(f_links_group, text="--- Các file/Git đã lưu ---", bg="#1a1a1a", fg="#888", font=("Arial", 8)).pack(anchor="w", pady=(0,2))
            
            for name, path in links.items():
                row_frame = tk.Frame(f_links_group, bg="#2a2a2a", bd=1, relief="solid")
                row_frame.pack(fill="x", pady=2, padx=2)

                btn_run = tk.Button(row_frame, text=f"▶ {name}", command=lambda p=path: self.run_path(p), bg="#007acc", fg="#fff", font=("Arial", 9, "bold"), anchor="w", relief="flat")
                btn_run.pack(side="left", fill="x", expand=True, padx=4, pady=3)

                btn_del = tk.Button(row_frame, text="❌ Xoá", command=lambda n=name: self.delete_shortcut(n), bg="#c9302c", fg="#fff", font=("Arial", 8, "bold"), relief="flat")
                btn_del.pack(side="right", padx=4, pady=3)

    def paste_and_run_auto(self):
        try:
            clipboard_content = self.root.clipboard_get()
            if not clipboard_content.strip():
                messagebox.showwarning("Cảnh báo", "Bộ nhớ tạm đang trống!")
                return
            
            auto_name = simpledialog.askstring("Tên file Auto", "Nhập tên file Auto (VD: auto1.py, auto_click.py):", initialvalue="auto.py", parent=self.panel_window)
            if not auto_name:
                return
            if not auto_name.endswith(".py"):
                auto_name += ".py"

            save_path = os.path.join(os.getcwd(), auto_name)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(clipboard_content)
            
            self.refresh_shortcuts()
            self.run_path(save_path)
        except Exception as ex:
            messagebox.showerror("Lỗi Clipboard", f"Không đọc được bộ nhớ tạm:\n{str(ex)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FloatingApp(root)
    root.mainloop()
