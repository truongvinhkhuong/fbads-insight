#!/usr/bin/env python3
"""
Lấy insights của posts với metrics đúng
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date

def get_posts_insights_fixed():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Lấy insights của posts
    print("\n=== LẤY INSIGHTS CỦA POSTS ===")
    try:
        # Lấy posts gần đây
        url = f"{base_url}/me/posts"
        params = {
            'access_token': access_token,
            'fields': 'id,message,created_time,updated_time,is_published',
            'limit': 10
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"Tìm thấy {len(posts)} posts")
            
            posts_with_insights = []
            
            for i, post in enumerate(posts):
                post_id = post.get('id')
                post_message = post.get('message', 'N/A')
                created_time = post.get('created_time', 'N/A')
                
                print(f"\n{i+1}. Post ID: {post_id}")
                print(f"   - Tạo lúc: {created_time}")
                print(f"   - Message: {post_message[:100]}...")
                
                # Thử các metrics khác nhau
                metrics_to_try = [
                    'post_impressions',
                    'post_impressions_unique',
                    'post_engaged_users',
                    'post_clicks',
                    'post_reactions_by_type_total',
                    'post_comments',
                    'post_shares'
                ]
                
                post_insights = {}
                
                for metric in metrics_to_try:
                    try:
                        url = f"{base_url}/{post_id}/insights"
                        params = {
                            'access_token': access_token,
                            'metric': metric,
                            'period': 'lifetime'
                        }
                        response = requests.get(url, params=params)
                        
                        if response.status_code == 200:
                            data = response.json()
                            insights = data.get('data', [])
                            
                            if insights:
                                value = insights[0].get('values', [{}])[0].get('value', 0)
                                post_insights[metric] = value
                                print(f"   ✅ {metric}: {value:,}")
                            else:
                                print(f"   ❌ {metric}: Không có dữ liệu")
                        else:
                            print(f"   ❌ {metric}: {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {metric}: {e}")
                
                if post_insights:
                    posts_with_insights.append({
                        'post_id': post_id,
                        'message': post_message,
                        'created_time': created_time,
                        'insights': post_insights
                    })
                    print(f"   ✅ Đã lấy được {len(post_insights)} metrics")
                else:
                    print(f"   ❌ Không lấy được insights nào")
            
            # Lưu dữ liệu
            if posts_with_insights:
                all_data = {
                    'extraction_date': datetime.now().isoformat(),
                    'start_date': '2023-01-01',
                    'page_name': 'LS2 Helmets Vietnam',
                    'page_id': '273719346452016',
                    'posts': posts_with_insights
                }
                
                with open('ads_data.json', 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ Đã lưu {len(posts_with_insights)} posts với insights vào ads_data.json")
                
                # Hiển thị tổng kết
                print(f"\n=== TỔNG KẾT ===")
                total_impressions = sum(post['insights'].get('post_impressions', 0) for post in posts_with_insights)
                total_engaged_users = sum(post['insights'].get('post_engaged_users', 0) for post in posts_with_insights)
                total_clicks = sum(post['insights'].get('post_clicks', 0) for post in posts_with_insights)
                total_reactions = sum(post['insights'].get('post_reactions_by_type_total', 0) for post in posts_with_insights)
                total_comments = sum(post['insights'].get('post_comments', 0) for post in posts_with_insights)
                total_shares = sum(post['insights'].get('post_shares', 0) for post in posts_with_insights)
                
                print(f"Tổng impressions: {total_impressions:,}")
                print(f"Tổng engaged users: {total_engaged_users:,}")
                print(f"Tổng clicks: {total_clicks:,}")
                print(f"Tổng reactions: {total_reactions:,}")
                print(f"Tổng comments: {total_comments:,}")
                print(f"Tổng shares: {total_shares:,}")
            else:
                print("\n❌ Không lấy được insights nào từ posts")
            
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_posts_insights_fixed()
