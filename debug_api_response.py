#!/usr/bin/env python3
"""
Script để debug API response từ Facebook Graph API
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_access_token():
    """Lấy access token từ environment variables."""
    return os.getenv('USER_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN') or ''

def debug_facebook_api():
    """Debug Facebook API response để xem cấu trúc dữ liệu thực tế."""
    
    page_id = (os.getenv('FB_PAGE_ID') or os.getenv('PAGE_ID') or '').strip()
    access_token = get_access_token()
    
    if not page_id or not access_token:
        print("❌ PAGE_ID hoặc ACCESS_TOKEN chưa được cấu hình")
        return
    
    print(f"🔍 Debugging Facebook API for Page ID: {page_id}")
    print("=" * 60)
    
    base_url = "https://graph.facebook.com/v23.0"
    
    # 1. Test Page Info
    print("\n1. 📄 Page Info:")
    page_url = f"{base_url}/{page_id}"
    page_params = {
        'access_token': access_token,
        'fields': 'name,fan_count,new_like_count,likes'
    }
    
    try:
        response = requests.get(page_url, params=page_params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Page Info Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 2. Test Page Insights - Basic metrics
    print("\n2. 📊 Page Insights (Basic):")
    insights_url = f"{base_url}/{page_id}/insights"
    insights_params = {
        'access_token': access_token,
        'metric': 'page_impressions,page_post_engagements,page_video_views',
        'period': 'day',
        'since': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'until': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.get(insights_url, params=insights_params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Page Insights Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 3. Test Page Insights - More metrics
    print("\n3. 📈 Page Insights (Extended):")
    extended_metrics = [
        'page_impressions_unique',
        'page_engaged_users', 
        'page_fan_adds_unique',
        'page_fan_removes_unique',
        'page_actions_post_reactions_total',
        'page_actions_post_comments',
        'page_actions_post_shares'
    ]
    
    insights_params_extended = {
        'access_token': access_token,
        'metric': ','.join(extended_metrics),
        'period': 'day',
        'since': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'until': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.get(insights_url, params=insights_params_extended)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Extended Insights Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 4. Test Posts with Insights
    print("\n4. 📝 Posts with Insights:")
    posts_url = f"{base_url}/{page_id}/posts"
    posts_params = {
        'access_token': access_token,
        'fields': 'id,message,created_time,type,permalink_url',
        'since': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'until': datetime.now().strftime('%Y-%m-%d'),
        'limit': 5
    }
    
    try:
        response = requests.get(posts_url, params=posts_params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Posts Response (first 5 posts):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 5. Test Individual Post Insights
    print("\n5. 🔍 Individual Post Insights:")
    try:
        # First get a post ID
        response = requests.get(posts_url, params=posts_params)
        if response.status_code == 200:
            posts_data = response.json()
            posts = posts_data.get('data', [])
            
            if posts:
                post_id = posts[0]['id']
                print(f"Testing insights for post: {post_id}")
                
                post_insights_url = f"{base_url}/{post_id}/insights"
                post_insights_params = {
                    'access_token': access_token,
                    'metric': 'post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total,post_comments,post_shares'
                }
                
                response = requests.get(post_insights_url, params=post_insights_params)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Post Insights Response:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ Error: {response.text}")
            else:
                print("❌ No posts found to test insights")
        else:
            print(f"❌ Cannot get posts: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_facebook_api()
