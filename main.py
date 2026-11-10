import json
import os
import threading
import tkinter as tk
from tkinter import messagebox
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Bắt buộc cấu hình biến môi trường hiển thị qua X11 cho Termux / Samsung DeX
os.environ["DISPLAY"] = ":0"

# --- KHU VỰC XỬ LÝ TÁC VỤ / AUTO GAME ---
def xu_ly_auto_game():
  print("🎮 Đang chạy kịch bản auto game...")
  # Viết logic code auto game của bạn tại đây
  return "Auto game đã thực thi thành công!"


# --- HTTP SERVER NHẬN LỆNH NGẦM ---
class TaskHandler(BaseHTTPRequestHandler):

  def do_POST(self):
    content_length = int(self.headers["Content-Length"])
    post_data = self.rfile.read(content_length)
    data = json.loads(post_data.decode("utf-8"))

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
    self.wfile.write(json.dumps(response).encode("utf-8"))

  def log_message(self, format, *args):
    return  # Ẩn log rườm rà của HTTP server


def run_server(port=5000):
  server_address = ("0.0.0.0", port)
  httpd = HTTPServer(server_address, TaskHandler)
  print(f"🚀 Server HTTP đang chạy tại cổng {port}, sẵn sàng nhận lệnh!")
  httpd.serve_forever()


# --- GIAO DIỆN GUI (XUẤT RA X11) ---
class AutoGUI:
  def __init__(self, root):
    self.root = root
    self.root.title("Quản lý Auto Game - X11")
    self.root.geometry("350x250")

    # Tiêu đề
    self.label = tk.Label(root, text="Hệ thống điều khiển Auto", font=("Arial", 14, "bold"))
    self.label.pack(pady=15)

    # Nút bấm chạy auto trực tiếp trên giao diện X11
    self.btn_run = tk.Button(root, text="Chạy Auto Ngay", font=("Arial", 12), bg="#4CAF50", fg="white", width=20, height=2, command=self.on_click_run)
    self.btn_run.pack(pady=10)

    # Nhãn trạng thái
    self.status_label = tk.Label(root, text="Trạng thái: Sẵn sàng", font=("Arial", 10), fg="gray")
    self.status_label.pack(pady=15)

  def on_click_run(self):
    msg = xu_ly_auto_game()
    self.status_label.config(text=f"Trạng thái: {msg}", fg="blue")
    messagebox.showinfo("Thông báo", msg)


if __name__ == "__main__":
  # 1. Khởi động HTTP Server ở một luồng riêng (Background Thread)
  server_thread = threading.Thread(target=run_server, args=(5000,))
  server_thread.daemon = True
  server_thread.start()

  # 2. Khởi chạy Giao diện GUI trên luồng chính để xuất thẳng ra X11
  print("🖥️ Đang mở giao diện GUI ra màn hình X11...")
  root = tk.Tk()
  app = AutoGUI(root)
  root.mainloop()
