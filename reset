# 1. Dừng hoàn toàn các tiến trình liên quan để tránh xung đột
pkill -f com.termux.x11
am force-stop com.termux

# 2. Đảm bảo biến môi trường được thiết lập đúng trước khi khởi động X11 server
export XDG_RUNTIME_DIR="${TMPDIR:-/data/data/com.termux/files/usr/tmp}"
export DISPLAY=":0"

# 3. Khởi động Termux-X11 server ngầm trước
termux-x11 :0 -ac &

# 4. Đợi một chút (khoảng 1 giây) để server kịp khởi tạo rồi mới bật Activity
sleep 1

# 5. Mở giao diện Termux-X11
am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity
