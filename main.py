import json
import os
import sys
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Cấu hình biến môi trường hiển thị qua X11 cho Termux
os.environ["DISPLAY"] = ":0"

# 2. Tự động giải nén thư viện libs.zip nếu chưa có thư mục libs
libs_dir = os.path.abspath("./libs")
libs_zip = os.path.abspath("./libs.zip")

if not os.path.exists(libs_dir) and os.path.exists(libs_zip):
  print("📦 Đang giải nén thư viện từ libs.zip...")
  with zipfile.ZipFile(libs_zip, "r") as zip_ref:
    zip_ref.extractall(".")

# 3. Đưa thư mục libs lên ưu tiên trong sys.path
if libs_dir not in sys.path:
  sys.path.insert(0, libs_dir)

# 4. Import Kivy an toàn
try:
  from kivy.app import App
  from kivy.uix.boxlayout import BoxLayout
  from kivy.uix.button import Button
  from kivy.uix.label import Label

  KIVY_AVAILABLE = True
  print("✅ Nạp thư viện Kivy thành công qua môi trường X11!")
except Exception as e:
  KIVY_AVAILABLE = False
  print(f"⚠️ Cảnh báo Kivy: {e}")


# --- KHU VỰC XỬ LÝ TÁC VỤ / AUTO GAME ---
def xu_ly_auto_game():
  print("🎮 Đang chạy kịch bản auto game...")
  return "Auto game đã thực thi thành công!"


# --- SERVER NHẬN LỆNH NGẦM ---
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
    return  # Ẩn log rườm rà của http server


def run_server(port=5000):
  server_address = ("0.0.0.0", port)
  httpd = HTTPServer(server_address, TaskHandler)
  print(f"🚀 Server HTTP đang chạy tại cổng {port}, sẵn sàng nhận lệnh!")
  httpd.serve_forever()


# --- GIAO DIỆN KIVY (XUẤT RA X11) ---
if KIVY_AVAILABLE:

  class MainApp(App):

    def build(self):
      layout = BoxLayout(orientation="vertical", padding=30, spacing=20)
      self.label = Label(
          text="Trạng thái: Sẵn sàng nhận lệnh / Auto", font_size=20
      )
      btn = Button(
          text="Chạy Auto Ngay", font_size=18, size_hint=(1, 0.3)
      )
      btn.bind(on_press=self.on_button_click)

      layout.add_widget(self.label)
      layout.add_widget(btn)
      return layout

    def on_button_click(self, instance):
      msg = xu_ly_auto_game()
      self.label.text = f"Trạng thái: {msg}"
else:
  MainApp = None


# --- KHỞI ĐỘNG CHƯƠNG TRÌNH ---
if __name__ == "__main__":
  # Khởi động Server ngầm ở một luồng riêng biệt (Background Thread)
  server_thread = threading.Thread(target=run_server, args=(5000,))
  server_thread.daemon = True
  server_thread.start()

  # Bật trực tiếp giao diện Kivy ra màn hình X11 trên luồng chính
  if KIVY_AVAILABLE and MainApp:
    print("🖥️ Đang khởi động giao diện Kivy qua X11...")
    MainApp().run()
  else:
    print(
        "⚠️ Kivy chưa sẵn sàng hoặc thiếu thư viện libs.zip. Chạy chế độ server"
        " thuần."
    )
    server_thread.join()
