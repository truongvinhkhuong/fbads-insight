#!/usr/bin/env python3
"""
Test Page Access Token trực tiếp
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def test_page_token():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Bước 1: Kiểm tra thông tin token
    print("\n=== KIỂM TRA THÔNG TIN TOKEN ===")
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
        else:
            print(f"Token không hợp lệ: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Lỗi: {e}")
        return
    
    # Bước 2: Lấy posts của trang
    print("\n=== LẤY POSTS CỦA TRANG ===")
    try:
        url = f"{base_url}/me/posts"
        params = {
            'access_token': access_token,
            'fields': 'id,message,created_time,updated_time,is_published,insights',
            'limit': 20
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"Tìm thấy {len(posts)} posts")
            
            if posts:
                for i, post in enumerate(posts[:5]):
                    print(f"\n{i+1}. Post ID: {post.get('id')}")
                    print(f"   - Tạo lúc: {post.get('created_time')}")
                    print(f"   - Cập nhật: {post.get('updated_time')}")
                    print(f"   - Đã xuất bản: {post.get('is_published')}")
                    print(f"   - Message: {post.get('message', 'N/A')[:100]}...")
                    
                    # Kiểm tra insights nếu có
                    if 'insights' in post:
                        print(f"   - Insights: {post.get('insights')}")
            else:
                print("Không có posts nào")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Bước 3: Lấy insights của trang
    print("\n=== LẤY INSIGHTS CỦA TRANG ===")
    try:
        url = f"{base_url}/me/insights"
        params = {
            'access_token': access_token,
            'metric': 'page_impressions,page_reach,page_engaged_users,page_post_engagements',
            'period': 'day',
            'since': '2023-01-01',
            'until': date.today().isoformat()
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('data', [])
            print(f"Tìm thấy {len(insights)} insights")
            
            for insight in insights:
                print(f"\n- {insight.get('name')}:")
                values = insight.get('values', [])
                if values:
                    print(f"  {len(values)} ngày dữ liệu")
                    # Hiển thị 3 ngày gần nhất
                    for value in values[-3:]:
                        print(f"    {value.get('end_time', 'N/A')}: {value.get('value', 'N/A')}")
                else:
                    print("  Không có dữ liệu")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Bước 4: Lấy posts đã được quảng cáo
    print("\n=== LẤY POSTS ĐÃ ĐƯỢC QUẢNG CÁO ===")
    try:
        url = f"{base_url}/me/promotable_posts"
        params = {
            'access_token': access_token,
            'fields': 'id,message,created_time,updated_time,is_published',
            'limit': 20
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"Tìm thấy {len(posts)} posts có thể quảng cáo")
            
            if posts:
                for i, post in enumerate(posts[:5]):
                    print(f"\n{i+1}. Post ID: {post.get('id')}")
                    print(f"   - Tạo lúc: {post.get('created_time')}")
                    print(f"   - Message: {post.get('message', 'N/A')[:100]}...")
            else:
                print("Không có posts nào có thể quảng cáo")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Bước 5: Lấy ads từ trang
    print("\n=== LẤY ADS TỪ TRANG ===")
    try:
        url = f"{base_url}/me/ads"
        params = {
            'access_token': access_token,
            'fields': 'id,name,status,created_time,updated_time',
            'limit': 20
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            ads = data.get('data', [])
            print(f"Tìm thấy {len(ads)} ads")
            
            if ads:
                for i, ad in enumerate(ads[:5]):
                    print(f"\n{i+1}. Ad ID: {ad.get('id')}")
                    print(f"   - Tên: {ad.get('name', 'N/A')}")
                    print(f"   - Trạng thái: {ad.get('status', 'N/A')}")
                    print(f"   - Tạo lúc: {ad.get('created_time', 'N/A')}")
            else:
                print("Không có ads nào")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    test_page_token()
