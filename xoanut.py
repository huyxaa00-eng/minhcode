import requests
import os

GITHUB_TOKEN = "TOKEN_CUA_BAN"  # Token GitHub của bạn
REPO_OWNER = "huyxaa00-eng"
REPO_NAME = "my_project"

def delete_button_script(file_name):
    """Xóa file script tương ứng trên GitHub và làm mới giao diện"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. Lấy SHA của file hiện tại trên GitHub (GitHub yêu cầu SHA khi xóa file)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_sha = response.json().get("sha")
        
        # 2. Gửi yêu cầu DELETE lên GitHub API
        data = {
            "message": f"Xóa nút/script {file_name} qua giao diện quản lý",
            "sha": file_sha
        }
        del_response = requests.delete(url, headers=headers, json=data)
        
        if del_response.status_code == 200:
            print(f"✅ Đã xóa thành công {file_name} trên GitHub!")
            return True, "Xóa thành công"
        else:
            return False, f"Lỗi GitHub: {del_response.json().get('message', 'Không rõ')}"
    else:
        return False, "Không tìm thấy file trên GitHub để xóa."
# Viết code của bạn ở đây
print('Hello from Termux Professional System!')