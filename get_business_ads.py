#!/usr/bin/env python3
"""
Thử lấy dữ liệu quảng cáo từ Business Manager
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def get_business_ads():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Bước 1: Lấy thông tin Business Manager
    print("\n=== THÔNG TIN BUSINESS MANAGER ===")
    try:
        url = f"{base_url}/me/businesses"
        params = {
            'access_token': access_token,
            'fields': 'id,name,primary_page'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            businesses = data.get('data', [])
            print(f"Tìm thấy {len(businesses)} doanh nghiệp:")
            
            for business in businesses:
                business_id = business.get('id')
                business_name = business.get('name')
                print(f"\nDoanh nghiệp: {business_name} (ID: {business_id})")
                
                # Thử lấy tài khoản quảng cáo từ Business Manager
                try:
                    url = f"{base_url}/{business_id}/owned_ad_accounts"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,name,account_status,currency,timezone_name,amount_spent,balance',
                        'limit': 100
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        accounts = data.get('data', [])
                        print(f"  Tài khoản quảng cáo: {len(accounts)}")
                        
                        for account in accounts:
                            print(f"    - {account.get('name')} ({account.get('id')})")
                            print(f"      Trạng thái: {account.get('account_status')}")
                            print(f"      Đã chi: {account.get('amount_spent', 'N/A')}")
                            
                            # Kiểm tra campaigns trong tài khoản này
                            try:
                                url = f"{base_url}/{account.get('id')}/campaigns"
                                params = {
                                    'access_token': access_token,
                                    'fields': 'id,name,status,objective,created_time,start_time,stop_time',
                                    'limit': 100
                                }
                                response = requests.get(url, params=params)
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    campaigns = data.get('data', [])
                                    print(f"      Campaigns: {len(campaigns)}")
                                    
                                    if campaigns:
                                        for campaign in campaigns[:3]:
                                            print(f"        - {campaign.get('name')} ({campaign.get('status')})")
                                    
                                    # Nếu có campaigns, lấy ads
                                    if campaigns:
                                        for campaign in campaigns[:2]:
                                            campaign_id = campaign.get('id')
                                            print(f"        Lấy ads từ campaign {campaign_id}...")
                                            
                                            try:
                                                url = f"{base_url}/{campaign_id}/ads"
                                                params = {
                                                    'access_token': access_token,
                                                    'fields': 'id,name,status,created_time,updated_time',
                                                    'limit': 20
                                                }
                                                response = requests.get(url, params=params)
                                                
                                                if response.status_code == 200:
                                                    data = response.json()
                                                    ads = data.get('data', [])
                                                    print(f"          Ads: {len(ads)}")
                                                    
                                                    for ad in ads[:3]:
                                                        print(f"            - {ad.get('name')} ({ad.get('status')})")
                                                else:
                                                    print(f"          Lỗi ads: {response.status_code}")
                                            except Exception as e:
                                                print(f"          Lỗi ads: {e}")
                                else:
                                    print(f"      Lỗi campaigns: {response.status_code}")
                            except Exception as e:
                                print(f"      Lỗi campaigns: {e}")
                    else:
                        print(f"  Lỗi tài khoản: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    print(f"  Lỗi: {e}")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Bước 2: Thử lấy dữ liệu từ tài khoản quảng cáo hiện tại với các tham số khác
    print("\n=== THỬ CÁC THAM SỐ KHÁC ===")
    current_account = os.getenv('FACEBOOK_ACCOUNT_IDS', '').split(',')[0].strip()
    
    if current_account:
        # Thử lấy campaigns với các tham số khác
        try:
            url = f"{base_url}/{current_account}/campaigns"
            params = {
                'access_token': access_token,
                'fields': 'id,name,status,objective,created_time,start_time,stop_time',
                'limit': 100,
                'effective_status': 'ACTIVE,PAUSED,ARCHIVED'  # Thêm tham số này
            }
            response = requests.get(url, params=params)
            
            print(f"Campaigns với effective_status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                campaigns = data.get('data', [])
                print(f"  Tìm thấy {len(campaigns)} campaigns")
                
                if campaigns:
                    for campaign in campaigns[:5]:
                        print(f"    - {campaign.get('name')} ({campaign.get('status')})")
        except Exception as e:
            print(f"Lỗi: {e}")
        
        # Thử lấy ads với các tham số khác
        try:
            url = f"{base_url}/{current_account}/ads"
            params = {
                'access_token': access_token,
                'fields': 'id,name,status,created_time,updated_time',
                'limit': 100,
                'effective_status': 'ACTIVE,PAUSED,ARCHIVED'  # Thêm tham số này
            }
            response = requests.get(url, params=params)
            
            print(f"Ads với effective_status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                ads = data.get('data', [])
                print(f"  Tìm thấy {len(ads)} ads")
                
                if ads:
                    for ad in ads[:5]:
                        print(f"    - {ad.get('name')} ({ad.get('status')})")
        except Exception as e:
            print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_business_ads()
