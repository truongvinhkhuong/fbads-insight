#!/usr/bin/env python3
"""
Script để lấy Page Access Token từ User Access Token
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_user_access_token():
    """Lấy User Access Token từ environment variables."""
    return os.getenv('USER_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN') or ''

def get_page_access_token(user_token, page_id):
    """Lấy Page Access Token từ User Access Token."""
    
    print(f"🔑 Đang lấy Page Access Token cho Page ID: {page_id}")
    
    # Step 1: Lấy danh sách pages của user
    pages_url = "https://graph.facebook.com/v23.0/me/accounts"
    params = {
        'access_token': user_token,
        'fields': 'id,name,access_token'
    }
    
    try:
        response = requests.get(pages_url, params=params)
        
        if response.status_code != 200:
            print(f"❌ Lỗi khi lấy danh sách pages: {response.text}")
            return None
        
        data = response.json()
        pages = data.get('data', [])
        
        print(f"📄 Tìm thấy {len(pages)} pages:")
        for page in pages:
            print(f"   - {page.get('name')} (ID: {page.get('id')})")
        
        # Tìm page với ID phù hợp
        target_page = None
        for page in pages:
            if page.get('id') == page_id:
                target_page = page
                break
        
        if not target_page:
            print(f"❌ Không tìm thấy page với ID: {page_id}")
            print("📋 Danh sách pages có sẵn:")
            for page in pages:
                print(f"   - {page.get('name')} (ID: {page.get('id')})")
            return None
        
        page_token = target_page.get('access_token')
        page_name = target_page.get('name')
        
        print(f"✅ Tìm thấy Page Access Token cho: {page_name}")
        print(f"🔑 Page Access Token: {page_token[:20]}...")
        
        return page_token
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None

def test_page_access_token(page_token, page_id):
    """Test Page Access Token bằng cách lấy page info."""
    
    print(f"\n🧪 Testing Page Access Token...")
    
    page_url = f"https://graph.facebook.com/v23.0/{page_id}"
    params = {
        'access_token': page_token,
        'fields': 'name,fan_count,new_like_count'
    }
    
    try:
        response = requests.get(page_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Page Access Token hoạt động!")
            print(f"   - Page name: {data.get('name')}")
            print(f"   - Fan count: {data.get('fan_count')}")
            print(f"   - New likes: {data.get('new_like_count')}")
            return True
        else:
            print(f"❌ Page Access Token không hoạt động: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test: {e}")
        return False

def test_page_insights(page_token, page_id):
    """Test Page Insights với Page Access Token."""
    
    print(f"\n📊 Testing Page Insights...")
    
    insights_url = f"https://graph.facebook.com/v23.0/{page_id}/insights"
    params = {
        'access_token': page_token,
        'metric': 'page_impressions',
        'period': 'day',
        'since': '2024-10-01',
        'until': '2024-10-02'
    }
    
    try:
        response = requests.get(insights_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Page Insights hoạt động!")
            print(f"   - Metrics: {len(data.get('data', []))}")
            return True
        else:
            print(f"❌ Page Insights không hoạt động: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test insights: {e}")
        return False

def test_page_posts(page_token, page_id):
    """Test Page Posts với Page Access Token."""
    
    print(f"\n📝 Testing Page Posts...")
    
    posts_url = f"https://graph.facebook.com/v23.0/{page_id}/posts"
    params = {
        'access_token': page_token,
        'fields': 'id,message,created_time,type',
        'limit': 5
    }
    
    try:
        response = requests.get(posts_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            print(f"✅ Page Posts hoạt động!")
            print(f"   - Posts found: {len(posts)}")
            for i, post in enumerate(posts[:3]):
                print(f"   - Post {i+1}: {post.get('type')} - {post.get('created_time')}")
            return True
        else:
            print(f"❌ Page Posts không hoạt động: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test posts: {e}")
        return False

def main():
    """Main function."""
    
    print("🚀 Facebook Page Access Token Generator")
    print("=" * 50)
    
    # Lấy thông tin từ environment
    user_token = get_user_access_token()
    page_id = (os.getenv('FB_PAGE_ID') or os.getenv('PAGE_ID') or '').strip()
    
    if not user_token:
        print("❌ USER_TOKEN hoặc FACEBOOK_ACCESS_TOKEN chưa được cấu hình")
        return
    
    if not page_id:
        print("❌ FB_PAGE_ID hoặc PAGE_ID chưa được cấu hình")
        return
    
    print(f"👤 User Token: {user_token[:20]}...")
    print(f"📄 Page ID: {page_id}")
    
    # Lấy Page Access Token
    page_token = get_page_access_token(user_token, page_id)
    
    if not page_token:
        print("❌ Không thể lấy Page Access Token")
        return
    
    # Test các chức năng
    test_page_access_token(page_token, page_id)
    test_page_insights(page_token, page_id)
    test_page_posts(page_token, page_id)
    
    print(f"\n🎉 Hoàn thành!")
    print(f"📝 Để sử dụng Page Access Token này, hãy thêm vào .env file:")
    print(f"PAGE_ACCESS_TOKEN={page_token}")
    
    # Ghi vào file .env
    env_content = f"""
# Facebook Page Access Token
PAGE_ACCESS_TOKEN={page_token}
"""
    
    try:
        with open('.env', 'a') as f:
            f.write(env_content)
        print(f"✅ Đã thêm PAGE_ACCESS_TOKEN vào file .env")
    except Exception as e:
        print(f"⚠️ Không thể ghi vào .env: {e}")
        print(f"📋 Hãy thêm thủ công: PAGE_ACCESS_TOKEN={page_token}")

if __name__ == "__main__":
    main()
