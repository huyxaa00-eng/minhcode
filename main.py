import urllib.request, time, subprocess, sys, traceback

# Hàm tự động cài đặt thư viện nếu phát hiện thiếu trong code
def ensure_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Phát hiện thiếu thư viện '{package_name}', đang tự động cài đặt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Đường dẫn file zz trên GitHub kèm chống cache theo thời gian thực
url = 'https://raw.githubusercontent.com/huyxaa00-eng/minhcode/main/zz?t=' + str(int(time.time()))

try:
    print("[*] Đang đồng bộ code mới nhất từ GitHub...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        code_content = response.read().decode('utf-8')
        
    print("-" * 40)
    print("[*] Đang thực thi code:\n")
    
    # Thực thi trực tiếp nội dung lấy từ GitHub
    exec(code_content, {})
    
except Exception as e:
    print("\n[!] Đã xảy ra lỗi trong quá trình thực thi:")
    traceback.print_exc()
