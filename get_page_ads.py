#!/usr/bin/env python3

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def get_page_ads():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Bước 1: Lấy danh sách trang Facebook
    print("\n=== DANH SÁCH TRANG FACEBOOK ===")
    try:
        url = f"{base_url}/me/accounts"
        params = {
            'access_token': access_token,
            'fields': 'id,name,access_token',
            'limit': 100
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"Tìm thấy {len(pages)} trang Facebook:")
            
            for i, page in enumerate(pages):
                print(f"\n{i+1}. {page.get('name')} (ID: {page.get('id')})")
                
                # Kiểm tra quảng cáo từ trang này
                page_id = page.get('id')
                page_name = page.get('name')
                
                print(f"   - Kiểm tra quảng cáo từ trang...")
                
                # Thử lấy posts đã được quảng cáo
                try:
                    url = f"{base_url}/{page_id}/promotable_posts"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,message,created_time,updated_time,is_published',
                        'limit': 20
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', [])
                        print(f"     {len(posts)} posts có thể quảng cáo")
                        
                        for post in posts[:5]:
                            print(f"       - {post.get('id')} - {post.get('created_time')}")
                            print(f"         Message: {post.get('message', 'N/A')[:100]}...")
                    else:
                        print(f"     Lỗi posts: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"     Lỗi posts: {e}")
                
                # Thử lấy insights của trang
                try:
                    url = f"{base_url}/{page_id}/insights"
                    params = {
                        'access_token': access_token,
                        'metric': 'page_impressions,page_reach,page_engaged_users',
                        'period': 'day',
                        'since': '2023-01-01',
                        'until': date.today().isoformat()
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        insights = data.get('data', [])
                        print(f"     {len(insights)} insights")
                        
                        for insight in insights[:3]:
                            print(f"       - {insight.get('name')}: {insight.get('values', [])}")
                    else:
                        print(f"     Lỗi insights: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"     Lỗi insights: {e}")
                
                # Thử lấy posts của trang
                try:
                    url = f"{base_url}/{page_id}/posts"
                    params = {
                        'access_token': access_token,
                        'fields': 'id,message,created_time,updated_time,is_published,insights',
                        'limit': 20
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', [])
                        print(f"     {len(posts)} posts")
                        
                        for post in posts[:5]:
                            print(f"       - {post.get('id')} - {post.get('created_time')}")
                            print(f"         Message: {post.get('message', 'N/A')[:100]}...")
                    else:
                        print(f"     Lỗi posts: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"     Lỗi posts: {e}")
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_page_ads()
