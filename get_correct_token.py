#!/usr/bin/env python3
"""
Hướng dẫn lấy User Access Token đúng cho Facebook Ads API
"""

import os
import json
import requests
from dotenv import load_dotenv

def check_current_token():
    """Kiểm tra token hiện tại"""
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Kiểm tra loại token
    print("\n=== KIỂM TRA TOKEN HIỆN TẠI ===")
    try:
        url = f"{base_url}/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name,category'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token hợp lệ cho: {data.get('name')} (ID: {data.get('id')})")
            print(f"Loại: {data.get('category', 'N/A')}")
            
            if data.get('category') == 'Brand':
                print("❌ Đây là Page Access Token - KHÔNG ĐÚNG cho Ads API")
                return False
            else:
                print("✅ Đây có thể là User Access Token")
                return True
        else:
            print(f"❌ Token không hợp lệ: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def check_ads_permissions():
    """Kiểm tra quyền truy cập Ads API"""
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print("\n=== KIỂM TRA QUYỀN ADS API ===")
    try:
        # Kiểm tra quyền
        url = f"{base_url}/me/permissions"
        params = {'access_token': access_token}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            permissions = data.get('data', [])
            
            print("Quyền hiện tại:")
            required_permissions = [
                'ads_read',
                'ads_management', 
                'pages_read_engagement',
                'pages_show_list',
                'business_management'
            ]
            
            has_required = True
            for perm in required_permissions:
                found = any(p.get('permission') == perm and p.get('status') == 'granted' for p in permissions)
                status = "✅" if found else "❌"
                print(f"  {status} {perm}: {'Có' if found else 'Thiếu'}")
                if not found:
                    has_required = False
            
            return has_required
        else:
            print(f"❌ Không thể kiểm tra quyền: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_ads_api():
    """Test truy cập Ads API"""
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    account_id = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')[0].strip()
    base_url = "https://graph.facebook.com/v23.0"
    
    print("\n=== TEST ADS API ===")
    try:
        # Test lấy danh sách ads
        url = f"{base_url}/{account_id}/ads"
        params = {
            'access_token': access_token,
            'fields': 'id,name,status',
            'limit': 1
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            ads = data.get('data', [])
            print(f"✅ Có thể truy cập Ads API: {len(ads)} ads")
            return True
        else:
            print(f"❌ Không thể truy cập Ads API: {response.status_code}")
            print(f"Lỗi: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def print_token_instructions():
    """In hướng dẫn lấy token đúng"""
    print("\n" + "="*60)
    print("HƯỚNG DẪN LẤY USER ACCESS TOKEN ĐÚNG")
    print("="*60)
    
    print("\n🔧 CÁCH 1: Facebook Graph API Explorer")
    print("1. Vào: https://developers.facebook.com/tools/explorer/")
    print("2. Chọn ứng dụng của bạn")
    print("3. Chọn 'Get User Access Token'")
    print("4. Cấp các quyền sau:")
    print("   ✅ ads_read")
    print("   ✅ ads_management") 
    print("   ✅ pages_read_engagement")
    print("   ✅ pages_show_list")
    print("   ✅ business_management")
    print("5. Click 'Generate Access Token'")
    print("6. Copy token và cập nhật vào file .env")
    
    print("\n🔧 CÁCH 2: Facebook Business Manager")
    print("1. Vào: https://business.facebook.com/")
    print("2. Chọn Business Manager của bạn")
    print("3. Vào Settings > System Users")
    print("4. Tạo System User mới hoặc chọn user có sẵn")
    print("5. Cấp quyền:")
    print("   ✅ Ads Management")
    print("   ✅ Pages")
    print("   ✅ Business Management")
    print("6. Generate Access Token")
    print("7. Copy token và cập nhật vào file .env")
    
    print("\n🔧 CÁCH 3: Facebook Login (cho app)")
    print("1. Sử dụng Facebook Login SDK")
    print("2. Yêu cầu các quyền: ads_read, ads_management")
    print("3. Lấy User Access Token từ response")
    print("4. Cập nhật vào file .env")
    
    print("\n⚠️  LƯU Ý QUAN TRỌNG:")
    print("- KHÔNG sử dụng Page Access Token cho Ads API")
    print("- Cần User Access Token hoặc System User Token")
    print("- Token phải có quyền ads_read và ads_management")
    print("- Token có thể hết hạn, cần refresh định kỳ")

def main():
    print("🔍 KIỂM TRA TOKEN FACEBOOK ADS API")
    print("="*50)
    
    # Kiểm tra token hiện tại
    is_user_token = check_current_token()
    
    # Kiểm tra quyền
    has_permissions = check_ads_permissions()
    
    # Test API
    can_access_ads = test_ads_api()
    
    print("\n" + "="*50)
    print("KẾT QUẢ KIỂM TRA")
    print("="*50)
    print(f"Token loại User: {'✅' if is_user_token else '❌'}")
    print(f"Có đủ quyền: {'✅' if has_permissions else '❌'}")
    print(f"Truy cập được Ads API: {'✅' if can_access_ads else '❌'}")
    
    if not (is_user_token and has_permissions and can_access_ads):
        print_token_instructions()
    else:
        print("\n🎉 Token của bạn đã đúng! Có thể sử dụng Ads API.")

if __name__ == "__main__":
    main()
