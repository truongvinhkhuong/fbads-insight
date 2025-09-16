#!/usr/bin/env python3
"""
Lấy insights đơn giản từ trang Facebook
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def get_simple_insights():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Lấy posts của trang
    print("\n=== LẤY POSTS VÀ INSIGHTS ĐƠN GIẢN ===")
    try:
        url = f"{base_url}/me/posts"
        params = {
            'access_token': access_token,
            'fields': 'id,message,created_time,updated_time,is_published',
            'limit': 20
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"Tìm thấy {len(posts)} posts")
            
            all_data = {
                'extraction_date': datetime.now().isoformat(),
                'start_date': '2023-01-01',
                'page_name': 'LS2 Helmets Vietnam',
                'page_id': '273719346452016',
                'posts': []
            }
            
            for i, post in enumerate(posts):
                post_id = post.get('id')
                post_message = post.get('message', 'N/A')
                created_time = post.get('created_time', 'N/A')
                
                print(f"\n{i+1}. Post ID: {post_id}")
                print(f"   - Tạo lúc: {created_time}")
                print(f"   - Message: {post_message[:100]}...")
                
                # Thử lấy insights với metrics cơ bản
                post_insights = {}
                try:
                    # Thử metrics cơ bản
                    url = f"{base_url}/{post_id}/insights"
                    params = {
                        'access_token': access_token,
                        'metric': 'post_impressions',
                        'period': 'lifetime'
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        insights = data.get('data', [])
                        
                        if insights:
                            print(f"   ✅ Insights:")
                            for insight in insights:
                                metric_name = insight.get('name')
                                values = insight.get('values', [])
                                if values:
                                    value = values[0].get('value', 0)
                                    post_insights[metric_name] = value
                                    print(f"      - {metric_name}: {value}")
                        else:
                            print(f"   ❌ Không có insights")
                    else:
                        print(f"   ❌ Lỗi insights: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"   ❌ Lỗi insights: {e}")
                
                # Lưu dữ liệu post
                post_data = {
                    'post_id': post_id,
                    'message': post_message,
                    'created_time': created_time,
                    'is_published': post.get('is_published', False),
                    'insights': post_insights
                }
                
                all_data['posts'].append(post_data)
            
            # Lưu dữ liệu vào file JSON
            with open('ads_data.json', 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Đã lưu {len(all_data['posts'])} posts vào ads_data.json")
            
            # Hiển thị tổng kết
            print(f"\n=== TỔNG KẾT ===")
            total_impressions = sum(post['insights'].get('post_impressions', 0) for post in all_data['posts'])
            print(f"Tổng impressions: {total_impressions:,}")
            print(f"Số posts có insights: {sum(1 for post in all_data['posts'] if post['insights'])}")
            
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
    # Thử lấy insights của trang
    print("\n=== LẤY INSIGHTS CỦA TRANG ===")
    try:
        url = f"{base_url}/me/insights"
        params = {
            'access_token': access_token,
            'metric': 'page_impressions',
            'period': 'day',
            'since': '2023-01-01',
            'until': date.today().isoformat()
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('data', [])
            print(f"Tìm thấy {len(insights)} insights của trang")
            
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

if __name__ == "__main__":
    get_simple_insights()
