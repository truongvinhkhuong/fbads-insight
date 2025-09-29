#!/usr/bin/env python3
"""
Debug chi tiết token và hướng dẫn lấy User Access Token
"""

import os
import json
import requests
from dotenv import load_dotenv

def debug_token_detailed():
    """Debug chi tiết token hiện tại"""
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # 1. Kiểm tra thông tin token
    print("\n=== THÔNG TIN TOKEN ===")
    try:
        url = f"{base_url}/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name,category,link'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token hợp lệ")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Tên: {data.get('name')}")
            print(f"   - Loại: {data.get('category')}")
            print(f"   - Link: {data.get('link', 'N/A')}")
            
            if data.get('category') == 'Brand':
                print("❌ ĐÂY LÀ PAGE ACCESS TOKEN - SAI!")
                print("   → Cần User Access Token hoặc System User Token")
            else:
                print("✅ Có thể là User Access Token")
        else:
            print(f"❌ Token không hợp lệ: {response.status_code}")
            print(f"Lỗi: {response.text}")
            return
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return
    
    # 2. Kiểm tra quyền chi tiết
    print("\n=== QUYỀN CHI TIẾT ===")
    try:
        url = f"{base_url}/me/permissions"
        params = {'access_token': access_token}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            permissions = data.get('data', [])
            
            print("Quyền hiện tại:")
            for perm in permissions:
                status = "✅" if perm.get('status') == 'granted' else "❌"
                print(f"  {status} {perm.get('permission')}: {perm.get('status')}")
            
            # Kiểm tra quyền quan trọng
            important_perms = ['ads_read', 'ads_management', 'pages_read_engagement']
            has_important = all(
                any(p.get('permission') == perm and p.get('status') == 'granted' 
                    for p in permissions) 
                for perm in important_perms
            )
            
            if has_important:
                print("\n✅ Có đủ quyền quan trọng")
            else:
                print("\n❌ Thiếu quyền quan trọng")
        else:
            print(f"❌ Không thể kiểm tra quyền: {response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi kiểm tra quyền: {e}")
    
    # 3. Test Ads API với error handling chi tiết
    print("\n=== TEST ADS API CHI TIẾT ===")
    account_id = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')[0].strip()
    
    try:
        # Test lấy ads
        url = f"{base_url}/{account_id}/ads"
        params = {
            'access_token': access_token,
            'fields': 'id,name,status',
            'limit': 1
        }
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ads = data.get('data', [])
            print(f"✅ Có thể lấy danh sách ads: {len(ads)} ads")
            
            # Test insights cho ad đầu tiên
            if ads:
                ad_id = ads[0].get('id')
                print(f"\n--- Test insights cho ad: {ad_id} ---")
                
                url = f"{base_url}/{ad_id}/insights"
                params = {
                    'access_token': access_token,
                    'fields': 'impressions,clicks,spend',
                    'date_preset': 'maximum',
                    'level': 'ad'
                }
                response = requests.get(url, params=params)
                
                print(f"Insights Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    insights = data.get('data', [])
                    print(f"✅ Có thể lấy insights: {len(insights)} records")
                    if insights:
                        print(f"   Sample: {insights[0]}")
                else:
                    print(f"❌ Không thể lấy insights: {response.text}")
        else:
            print(f"❌ Không thể lấy ads: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi test Ads API: {e}")

def print_solution():
    """In giải pháp chi tiết"""
    print("\n" + "="*70)
    print("🔧 GIẢI PHÁP: LẤY USER ACCESS TOKEN")
    print("="*70)
    
    print("\n📋 VẤN ĐỀ:")
    print("   - Token hiện tại là Page Access Token")
    print("   - Page Token KHÔNG thể truy cập Ads API")
    print("   - Cần User Access Token hoặc System User Token")
    
    print("\n🎯 GIẢI PHÁP 1: Facebook Graph API Explorer")
    print("1. Vào: https://developers.facebook.com/tools/explorer/")
    print("2. Chọn ứng dụng của bạn")
    print("3. Click 'Get Token' → 'Get User Access Token'")
    print("4. Chọn các quyền:")
    print("   ✅ ads_read")
    print("   ✅ ads_management")
    print("   ✅ pages_read_engagement")
    print("   ✅ pages_show_list")
    print("   ✅ business_management")
    print("5. Click 'Generate Access Token'")
    print("6. Copy token và cập nhật vào .env")
    
    print("\n🎯 GIẢI PHÁP 2: Facebook Business Manager")
    print("1. Vào: https://business.facebook.com/")
    print("2. Chọn Business Manager")
    print("3. Settings → System Users")
    print("4. Tạo System User mới:")
    print("   - Name: 'Ads API User'")
    print("   - Role: 'Admin'")
    print("5. Cấp quyền:")
    print("   ✅ Ads Management")
    print("   ✅ Pages")
    print("   ✅ Business Management")
    print("6. Generate Access Token")
    print("7. Copy token và cập nhật vào .env")
    
    print("\n🎯 GIẢI PHÁP 3: Sử dụng App Access Token")
    print("1. Vào: https://developers.facebook.com/apps/")
    print("2. Chọn app của bạn")
    print("3. Settings → Basic")
    print("4. Copy App ID và App Secret")
    print("5. Tạo App Access Token:")
    print("   https://graph.facebook.com/oauth/access_token?")
    print("   client_id=YOUR_APP_ID&")
    print("   client_secret=YOUR_APP_SECRET&")
    print("   grant_type=client_credentials")
    
    print("\n⚠️  LƯU Ý QUAN TRỌNG:")
    print("- Page Access Token ≠ User Access Token")
    print("- Ads API cần User Token hoặc System User Token")
    print("- App Access Token có thể hạn chế quyền")
    print("- Token có thể hết hạn, cần refresh")

def main():
    print("🔍 DEBUG TOKEN CHI TIẾT")
    print("="*50)
    
    debug_token_detailed()
    print_solution()

if __name__ == "__main__":
    main()
