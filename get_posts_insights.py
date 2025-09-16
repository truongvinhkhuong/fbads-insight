#!/usr/bin/env python3
"""
Lấy insights từ các posts của trang Facebook
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def get_posts_insights():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Lấy posts của trang
    print("\n=== LẤY POSTS VÀ INSIGHTS ===")
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
                
                # Lấy insights chi tiết cho post này
                post_insights = {}
                try:
                    url = f"{base_url}/{post_id}/insights"
                    params = {
                        'access_token': access_token,
                        'metric': 'post_impressions,post_impressions_unique,post_engaged_users,post_clicks,post_reactions_by_type_total,post_comments,post_shares',
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
            total_engaged_users = sum(post['insights'].get('post_engaged_users', 0) for post in all_data['posts'])
            total_clicks = sum(post['insights'].get('post_clicks', 0) for post in all_data['posts'])
            total_reactions = sum(post['insights'].get('post_reactions_by_type_total', 0) for post in all_data['posts'])
            total_comments = sum(post['insights'].get('post_comments', 0) for post in all_data['posts'])
            total_shares = sum(post['insights'].get('post_shares', 0) for post in all_data['posts'])
            
            print(f"Tổng impressions: {total_impressions:,}")
            print(f"Tổng engaged users: {total_engaged_users:,}")
            print(f"Tổng clicks: {total_clicks:,}")
            print(f"Tổng reactions: {total_reactions:,}")
            print(f"Tổng comments: {total_comments:,}")
            print(f"Tổng shares: {total_shares:,}")
            
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_posts_insights()
