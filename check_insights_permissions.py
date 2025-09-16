#!/usr/bin/env python3
"""
Kiểm tra quyền truy cập insights và hướng dẫn lấy token đúng
"""

import os
import json
import requests
from dotenv import load_dotenv

def check_insights_permissions():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Bước 1: Kiểm tra loại token
    print("\n=== KIỂM TRA LOẠI TOKEN ===")
    try:
        url = f"{base_url}/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name,category'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Token hợp lệ cho: {data.get('name')} (ID: {data.get('id')})")
            print(f"Loại: {data.get('category', 'N/A')}")
            
            # Kiểm tra xem có phải Page token không
            if data.get('category') == 'Brand':
                print("✅ Đây là Page Access Token")
            else:
                print("❌ Đây không phải Page Access Token")
        else:
            print(f"Token không hợp lệ: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Lỗi: {e}")
        return
    
    # Bước 2: Kiểm tra quyền truy cập insights
    print("\n=== KIỂM TRA QUYỀN INSIGHTS ===")
    try:
        # Thử lấy insights cơ bản
        url = f"{base_url}/me/insights"
        params = {
            'access_token': access_token,
            'metric': 'page_impressions',
            'period': 'day',
            'since': '2024-01-01',
            'until': '2024-01-02'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('data', [])
            print(f"✅ Có quyền truy cập insights: {len(insights)} metrics")
            
            for insight in insights:
                print(f"  - {insight.get('name')}: {insight.get('values', [])}")
        else:
            print(f"❌ Không có quyền truy cập insights: {response.status_code}")
            print(f"Lỗi: {response.text}")
            
            # Kiểm tra quyền cụ thể
            try:
                url = f"{base_url}/me/permissions"
                params = {'access_token': access_token}
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    permissions = data.get('data', [])
                    
                    print("\nQuyền hiện tại:")
                    for perm in permissions:
                        status = "✅" if perm.get('status') == 'granted' else "❌"
                        print(f"  {status} {perm.get('permission')}: {perm.get('status')}")
                    
                    # Kiểm tra quyền insights
                    insights_granted = any(p.get('permission') == 'pages_read_insights' and p.get('status') == 'granted' for p in permissions)
                    if not insights_granted:
                        print("\n❌ THIẾU QUYỀN 'pages_read_insights'")
                        print("Cần cấp quyền này để truy cập insights")
                else:
                    print(f"Không thể kiểm tra quyền: {response.status_code}")
            except Exception as e:
                print(f"Lỗi kiểm tra quyền: {e}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Bước 3: Hướng dẫn lấy token đúng
    print("\n=== HƯỚNG DẪN LẤY TOKEN ĐÚNG ===")
    print("Để truy cập insights, bạn cần:")
    print("\n1. Vào Facebook Graph API Explorer: https://developers.facebook.com/tools/explorer/")
    print("2. Chọn ứng dụng của bạn")
    print("3. Chọn 'Get User Access Token'")
    print("4. Cấp quyền: pages_read_insights, pages_show_list")
    print("5. Copy token và cập nhật vào file .env")
    print("\nHOẶC:")
    print("1. Vào Facebook Business Manager")
    print("2. Chọn trang LS2 Helmets Vietnam")
    print("3. Vào Settings > Page Access Token")
    print("4. Tạo token mới với quyền 'pages_read_insights'")
    print("5. Copy token và cập nhật vào file .env")
    
    # Bước 4: Thử lấy insights với metrics khác
    print("\n=== THỬ CÁC METRICS KHÁC ===")
    metrics_to_try = [
        'page_impressions',
        'page_reach',
        'page_engaged_users',
        'page_post_engagements',
        'page_impressions_unique'
    ]
    
    for metric in metrics_to_try:
        try:
            url = f"{base_url}/me/insights"
            params = {
                'access_token': access_token,
                'metric': metric,
                'period': 'day',
                'since': '2024-01-01',
                'until': '2024-01-02'
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get('data', [])
                print(f"✅ {metric}: {len(insights)} metrics")
            else:
                print(f"❌ {metric}: {response.status_code}")
        except Exception as e:
            print(f"❌ {metric}: {e}")

if __name__ == "__main__":
    check_insights_permissions()
