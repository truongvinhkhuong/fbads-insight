#!/usr/bin/env python3
"""
Debug để kiểm tra tài khoản quảng cáo đúng
"""

import os
import json
import requests
from dotenv import load_dotenv

def debug_account():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Bước 1: Kiểm tra tất cả tài khoản quảng cáo
    print("\n=== TẤT CẢ TÀI KHOẢN QUẢNG CÁO ===")
    try:
        url = f"{base_url}/me/adaccounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,account_status,currency,timezone_name,amount_spent,balance',
            'limit': 100
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('data', [])
            print(f"Tìm thấy {len(accounts)} tài khoản quảng cáo:")
            
            for i, account in enumerate(accounts):
                print(f"\n{i+1}. {account.get('name')} (ID: {account.get('id')})")
                print(f"   - Trạng thái: {account.get('account_status')}")
                print(f"   - Tiền tệ: {account.get('currency')}")
                print(f"   - Đã chi: {account.get('amount_spent', 'N/A')}")
                print(f"   - Số dư: {account.get('balance', 'N/A')}")
                
                # Kiểm tra campaigns trong tài khoản này
                print(f"   - Kiểm tra campaigns...")
                try:
                    url = f"{base_url}/{account.get('id')}/campaigns"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,name,status',
                        'limit': 10
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        campaigns = data.get('data', [])
                        print(f"     ✅ {len(campaigns)} campaigns")
                        for campaign in campaigns[:3]:
                            print(f"       - {campaign.get('name')} ({campaign.get('status')})")
                    else:
                        print(f"     ❌ Lỗi campaigns: {response.status_code}")
                except Exception as e:
                    print(f"     ❌ Lỗi campaigns: {e}")
                
                # Kiểm tra ads trong tài khoản này
                print(f"   - Kiểm tra ads...")
                try:
                    url = f"{base_url}/{account.get('id')}/ads"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,name,status',
                        'limit': 10
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        ads = data.get('data', [])
                        print(f"     ✅ {len(ads)} ads")
                        for ad in ads[:3]:
                            print(f"       - {ad.get('name')} ({ad.get('status')})")
                    else:
                        print(f"     ❌ Lỗi ads: {response.status_code}")
                except Exception as e:
                    print(f"     ❌ Lỗi ads: {e}")
                
                # Kiểm tra ad sets trong tài khoản này
                print(f"   - Kiểm tra ad sets...")
                try:
                    url = f"{base_url}/{account.get('id')}/adsets"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,name,status',
                        'limit': 10
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        adsets = data.get('data', [])
                        print(f"     ✅ {len(adsets)} ad sets")
                        for adset in adsets[:3]:
                            print(f"       - {adset.get('name')} ({adset.get('status')})")
                    else:
                        print(f"     ❌ Lỗi ad sets: {response.status_code}")
                except Exception as e:
                    print(f"     ❌ Lỗi ad sets: {e}")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Bước 2: Kiểm tra tài khoản hiện tại trong .env
    print("\n=== TÀI KHOẢN HIỆN TẠI TRONG .ENV ===")
    current_account = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')[0].strip()
    print(f"Account ID trong .env: {current_account}")
    
    if current_account:
        try:
            url = f"{base_url}/{current_account}"
            params = {
                'access_token': access_token,
                'fields': 'id,name,account_status,currency,timezone_name,amount_spent,balance'
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Thông tin tài khoản:")
                print(f"  - Tên: {data.get('name')}")
                print(f"  - ID: {data.get('id')}")
                print(f"  - Trạng thái: {data.get('account_status')}")
                print(f"  - Tiền tệ: {data.get('currency')}")
                print(f"  - Đã chi: {data.get('amount_spent', 'N/A')}")
                print(f"  - Số dư: {data.get('balance', 'N/A')}")
            else:
                print(f"Lỗi: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    debug_account()
