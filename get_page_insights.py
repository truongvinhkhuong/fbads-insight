#!/usr/bin/env python3
"""
Lấy insights từ trang Facebook với Page Access Token
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

def get_page_insights():
    load_dotenv()
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    base_url = "https://graph.facebook.com/v23.0"
    
    print(f"Access Token: {access_token[:20]}...")
    
    # Lấy insights của trang
    print("\n=== LẤY INSIGHTS CỦA TRANG ===")
    try:
        # Lấy insights trong 30 ngày qua
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        url = f"{base_url}/me/insights"
        params = {
            'access_token': access_token,
            'metric': 'page_impressions,page_post_engagements,page_impressions_unique',
            'period': 'day',
            'since': start_date.isoformat(),
            'until': end_date.isoformat()
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('data', [])
            print(f"Tìm thấy {len(insights)} insights")
            
            all_data = {
                'extraction_date': datetime.now().isoformat(),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'page_name': 'LS2 Helmets Vietnam',
                'page_id': '273719346452016',
                'insights': {}
            }
            
            for insight in insights:
                metric_name = insight.get('name')
                values = insight.get('values', [])
                
                print(f"\n- {metric_name}:")
                print(f"  {len(values)} ngày dữ liệu")
                
                # Tính tổng
                total = sum(value.get('value', 0) for value in values)
                print(f"  Tổng: {total:,}")
                
                # Hiển thị 5 ngày gần nhất
                print(f"  5 ngày gần nhất:")
                for value in values[-5:]:
                    print(f"    {value.get('end_time', 'N/A')}: {value.get('value', 'N/A'):,}")
                
                all_data['insights'][metric_name] = {
                    'total': total,
                    'daily_data': values
                }
            
            # Lưu dữ liệu
            with open('ads_data.json', 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Đã lưu insights vào ads_data.json")
            
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")
    
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
                
                # Lấy insights của post này
                try:
                    url = f"{base_url}/{post_id}/insights"
                    params = {
                        'access_token': access_token,
                        'metric': 'post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total,post_comments,post_shares',
                        'period': 'lifetime'
                    }
                    response = requests.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        insights = data.get('data', [])
                        
                        if insights:
                            print(f"   ✅ Insights:")
                            post_insights = {}
                            for insight in insights:
                                metric_name = insight.get('name')
                                values = insight.get('values', [])
                                if values:
                                    value = values[0].get('value', 0)
                                    post_insights[metric_name] = value
                                    print(f"      - {metric_name}: {value:,}")
                            
                            posts_with_insights.append({
                                'post_id': post_id,
                                'message': post_message,
                                'created_time': created_time,
                                'insights': post_insights
                            })
                        else:
                            print(f"   ❌ Không có insights")
                    else:
                        print(f"   ❌ Lỗi insights: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"   ❌ Lỗi insights: {e}")
            
            # Cập nhật dữ liệu với posts
            if posts_with_insights:
                all_data['posts'] = posts_with_insights
                
                # Lưu lại dữ liệu
                with open('ads_data.json', 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ Đã cập nhật {len(posts_with_insights)} posts với insights")
            
        else:
            print(f"Lỗi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_page_insights()
