#!/usr/bin/env python3
"""
Hướng dẫn lấy token Facebook mới
"""

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("=== HƯỚNG DẪN LẤY TOKEN FACEBOOK MỚI ===")
    print()
    print("Token hiện tại đã hết hạn. Để lấy token mới:")
    print()
    print("CÁCH 1: Sử dụng Facebook Graph API Explorer")
    print("1. Truy cập: https://developers.facebook.com/tools/explorer/")
    print("2. Chọn ứng dụng của bạn")
    print("3. Chọn 'Get User Access Token'")
    print("4. Cấp quyền: pages_read_insights, pages_show_list, ads_read")
    print("5. Copy token và cập nhật vào file .env")
    print()
    print("CÁCH 2: Sử dụng Facebook Business Manager")
    print("1. Truy cập: https://business.facebook.com/")
    print("2. Chọn trang LS2 Helmets Vietnam")
    print("3. Vào Settings > Page Access Token")
    print("4. Tạo token mới với quyền 'pages_read_insights'")
    print("5. Copy token và cập nhật vào file .env")
    print()
    print("CÁCH 3: Sử dụng Facebook Marketing API")
    print("1. Truy cập: https://developers.facebook.com/tools/explorer/")
    print("2. Chọn ứng dụng của bạn")
    print("3. Chọn 'Get User Access Token'")
    print("4. Cấp quyền: ads_read, ads_management")
    print("5. Copy token và cập nhật vào file .env")
    print()
    print("SAU KHI CÓ TOKEN MỚI:")
    print("1. Mở file .env")
    print("2. Cập nhật FACEBOOK_ACCESS_TOKEN=your_new_token_here")
    print("3. Lưu file")
    print("4. Restart ứng dụng")
    print()
    print("KIỂM TRA TOKEN:")
    print("Chạy: python3 check_insights_permissions.py")
    print()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("File .env hiện tại:")
        with open('.env', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'FACEBOOK_ACCESS_TOKEN' in line or 'USER_TOKEN' in line:
                    print(f"  {line.strip()}")
    else:
        print("Không tìm thấy file .env")

if __name__ == "__main__":
    main()
