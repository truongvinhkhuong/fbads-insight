#!/usr/bin/env python3
"""
Script test Facebook access token khác
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_facebook_token(access_token, account_id=None):
    """Test Facebook access token với các endpoints khác nhau"""
    
    base_url = "https://graph.facebook.com/v18.0"
    
    print(f"🔑 Testing Facebook Access Token: {access_token[:10]}...{access_token[-10:]}")
    print("=" * 60)
    
    # Test 1: Kiểm tra thông tin user
    print("👤 Test 1: Kiểm tra thông tin user (/me)")
    try:
        url = f"{base_url}/me"
        params = {'access_token': access_token}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Thành công! User ID: {data.get('id')}, Name: {data.get('name')}")
        else:
            print(f"❌ Lỗi {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    print()
    
    # Test 2: Kiểm tra quyền truy cập
    print("🔐 Test 2: Kiểm tra quyền truy cập (/me/permissions)")
    try:
        url = f"{base_url}/me/permissions"
        params = {'access_token': access_token}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            permissions = data.get('data', [])
            print(f"✅ Thành công! Có {len(permissions)} quyền:")
            for perm in permissions:
                status = "✅" if perm.get('status') == 'granted' else "❌"
                print(f"  {status} {perm.get('permission')}: {perm.get('status')}")
        else:
            print(f"❌ Lỗi {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    print()
    
    # Test 3: Kiểm tra tài khoản quảng cáo
    print("📊 Test 3: Kiểm tra tài khoản quảng cáo (/me/adaccounts)")
    try:
        url = f"{base_url}/me/adaccounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,account_status,account_type'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            print(f"✅ Thành công! Tìm thấy {len(accounts)} tài khoản quảng cáo:")
            for account in accounts[:5]:  # Chỉ hiển thị 5 tài khoản đầu
                status = "✅" if account.get('account_status') == 1 else "❌"
                print(f"  {status} {account.get('name')} (ID: {account.get('id')}) - Status: {account.get('account_status')}")
        else:
            print(f"❌ Lỗi {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    print()
    
    # Test 4: Kiểm tra tài khoản cụ thể (nếu có)
    if account_id:
        print(f"🎯 Test 4: Kiểm tra tài khoản cụ thể (/{account_id})")
        try:
            url = f"{base_url}/{account_id}"
            params = {
                'access_token': access_token,
                'fields': 'id,name,account_status,account_type,timezone_name,currency'
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Thành công! Tài khoản: {data.get('name')}")
                print(f"  ID: {data.get('id')}")
                print(f"  Status: {data.get('account_status')}")
                print(f"  Type: {data.get('account_type')}")
                print(f"  Timezone: {data.get('timezone_name')}")
                print(f"  Currency: {data.get('currency')}")
            else:
                print(f"❌ Lỗi {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
    
    print()
    
    # Test 5: Kiểm tra campaigns (nếu có account_id)
    if account_id:
        print(f"📈 Test 5: Kiểm tra campaigns (/{account_id}/campaigns)")
        try:
            url = f"{base_url}/{account_id}/campaigns"
            params = {
                'access_token': access_token,
                'fields': 'id,name,status,objective',
                'limit': 5
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                campaigns = data.get('data', [])
                print(f"✅ Thành công! Tìm thấy {len(campaigns)} campaigns:")
                for campaign in campaigns:
                    status = "✅" if campaign.get('status') == 'ACTIVE' else "⏸️"
                    print(f"  {status} {campaign.get('name')} - {campaign.get('status')} - {campaign.get('objective')}")
            else:
                print(f"❌ Lỗi {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

def generate_curl_commands(access_token, account_id=None):
    """Tạo các curl commands để test"""
    
    base_url = "https://graph.facebook.com/v18.0"
    
    print("\n" + "=" * 60)
    print("🔧 CURL COMMANDS ĐỂ TEST")
    print("=" * 60)
    
    # Test user info
    print("👤 Test thông tin user:")
    print(f"curl -s 'https://graph.facebook.com/v18.0/me?access_token={access_token}' | python -m json.tool")
    
    # Test permissions
    print("\n🔐 Test quyền truy cập:")
    print(f"curl -s 'https://graph.facebook.com/v18.0/me/permissions?access_token={access_token}' | python -m json.tool")
    
    # Test ad accounts
    print("\n📊 Test tài khoản quảng cáo:")
    print(f"curl -s 'https://graph.facebook.com/v18.0/me/adaccounts?access_token={access_token}&fields=id,name,account_status' | python -m json.tool")
    
    if account_id:
        # Test specific account
        print(f"\n🎯 Test tài khoản cụ thể:")
        print(f"curl -s 'https://graph.facebook.com/v18.0/{account_id}?access_token={access_token}&fields=id,name,account_status,currency' | python -m json.tool")
        
        # Test campaigns
        print(f"\n📈 Test campaigns:")
        print(f"curl -s 'https://graph.facebook.com/v18.0/{account_id}/campaigns?access_token={access_token}&fields=id,name,status&limit=5' | python -m json.tool")

def main():
    """Hàm chính"""
    load_dotenv()
    
    print("🚀 Facebook Access Token Tester")
    print("=" * 60)
    
    # Lấy token từ environment hoặc nhập từ user
    current_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    current_account = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')[0].strip() if os.getenv('FACEBOOK_ACCOUNT_IDS') else None
    
    print("🔍 Tìm thấy cấu hình hiện tại:")
    if current_token:
        print(f"  Token: {current_token[:10]}...{current_token[-10:]}")
    else:
        print("  Token: Không có")
    
    if current_account:
        print(f"  Account ID: {current_account}")
    else:
        print("  Account ID: Không có")
    
    print("\n" + "=" * 60)
    print("📝 NHẬP THÔNG TIN ĐỂ TEST")
    print("=" * 60)
    
    # Nhập token mới
    new_token = input("🔑 Nhập Facebook Access Token mới (hoặc Enter để dùng token hiện tại): ").strip()
    if not new_token:
        new_token = current_token
    
    # Nhập account ID mới
    new_account = input(f"🎯 Nhập Facebook Account ID (hoặc Enter để dùng {current_account}): ").strip()
    if not new_account:
        new_account = current_account
    
    if not new_token:
        print("❌ Không có access token để test!")
        return
    
    print("\n" + "=" * 60)
    print("🧪 BẮT ĐẦU TEST")
    print("=" * 60)
    
    # Test token
    test_facebook_token(new_token, new_account)
    
    # Tạo curl commands
    generate_curl_commands(new_token, new_account)
    
    print("\n" + "=" * 60)
    print("🏁 TEST HOÀN THÀNH!")
    print("=" * 60)

if __name__ == '__main__':
    main()
